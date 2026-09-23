from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

from .index import (
    EVIDENCE_WEIGHT,
    SEARCH_INDEX_COMPONENT,
    SEARCH_INDEX_VERSION,
    connect_readonly,
    normalize_cbeta_work_id,
    normalize_taisho_line,
    taisho_line_key,
)
from .model import compact, fold_diacritics, normalize


def _row(row: sqlite3.Row) -> dict:
    item = dict(row)
    for key in ("relation_ids", "metadata_json", "details_json", "morphology_json"):
        if key in item and isinstance(item[key], str):
            try:
                item[key] = json.loads(item[key])
            except json.JSONDecodeError:
                pass
    return item


def _is_cjk_character(value: str) -> bool:
    codepoint = ord(value)
    return (
        0x3400 <= codepoint <= 0x4DBF
        or 0x4E00 <= codepoint <= 0x9FFF
        or 0xF900 <= codepoint <= 0xFAFF
        or 0x20000 <= codepoint <= 0x323AF
        or 0x3040 <= codepoint <= 0x30FF
        or 0xAC00 <= codepoint <= 0xD7AF
    )


def _cjk_substring_query(query: str) -> str | None:
    value = compact(query)
    if len(value) < 3 or not any(_is_cjk_character(char) for char in value):
        return None
    return value


def _search_index_version(con: sqlite3.Connection) -> str | None:
    tables = {
        row["name"]
        for row in con.execute(
            """SELECT name FROM sqlite_master
               WHERE type='table'
                 AND name IN ('search_index_state','records_cjk_fts')"""
        )
    }
    if tables != {"search_index_state", "records_cjk_fts"}:
        return None
    row = con.execute(
        "SELECT version FROM search_index_state WHERE component=?",
        (SEARCH_INDEX_COMPONENT,),
    ).fetchone()
    return row["version"] if row else None


def status(db_path: Path) -> dict:
    if not db_path.exists():
        return {"database": str(db_path), "exists": False, "ready": False, "sources": []}
    con = connect_readonly(db_path)
    sources = [_row(r) for r in con.execute("SELECT * FROM source_state ORDER BY corpus")]
    counts = {
        table: con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        for table in ("records", "works", "relations", "variants", "lemmas")
    }
    con.close()
    return {"database": str(db_path), "exists": True, "ready": bool(sources), "counts": counts, "sources": sources}


def search(
    db_path: Path,
    query: str,
    limit: int = 20,
    language: str | None = None,
    corpus: str | None = None,
) -> dict:
    con = connect_readonly(db_path)
    norm = normalize(query)
    folded = fold_diacritics(query)
    comp = compact(query)
    cjk_query = _cjk_substring_query(query)
    search_index_version = _search_index_version(con)
    cjk_index_available = search_index_version == SEARCH_INDEX_VERSION
    limitations: list[str] = []
    if any(_is_cjk_character(char) for char in comp):
        if len(comp) < 3:
            limitations.append(
                "cjk_middle_substring_queries_shorter_than_3_characters_are_not_guaranteed"
            )
        elif not cjk_index_available:
            limitations.append(
                "cjk_substring_index_unavailable_or_stale; rebuild the derived search indexes"
            )
    params: list = []
    filters = []
    if language:
        filters.append("r.language=?")
        params.append(language)
    if corpus:
        filters.append("r.corpus=?")
        params.append(corpus)
    where = (" AND " + " AND ".join(filters)) if filters else ""
    candidates: dict[int, sqlite3.Row] = {}
    lemma_forms = {norm}
    for row in con.execute(
        """SELECT DISTINCT surface FROM lemmas
           WHERE lemma=? OR surface=? LIMIT 200""",
        (norm, norm),
    ):
        lemma_forms.add(row["surface"])
    # FTS creates a small candidate set for all scripts. Exact, normalized,
    # folded, and corpus-lemma evidence are evaluated only on those candidates.
    terms = {query, norm, folded, comp, *lemma_forms}
    for term in sorted((t for t in terms if t), key=lambda value: (value != query, -len(value))):
        escaped = term.replace('"', '""')
        match = f'"{escaped}"'
        try:
            fts_sql = f"""SELECT r.* FROM records_fts f
                          JOIN records r ON r.id=f.rowid
                          WHERE records_fts MATCH ?{where}
                          ORDER BY bm25(records_fts) LIMIT ?"""
            for row in con.execute(fts_sql, [match, *params, max(limit * 5, 50)]):
                candidates[row["id"]] = row
        except sqlite3.OperationalError:
            continue
    if cjk_query and cjk_index_available:
        escaped = cjk_query.replace('"', '""')
        cjk_sql = f"""SELECT r.* FROM records_cjk_fts f
                      JOIN records r ON r.id=f.rowid
                      WHERE records_cjk_fts MATCH ?{where}
                      ORDER BY
                        CASE WHEN instr(r.raw_text, ?) > 0 THEN 0 ELSE 1 END,
                        bm25(records_cjk_fts)
                      LIMIT ?"""
        for row in con.execute(
            cjk_sql,
            [f'"{escaped}"', *params, query, max(limit * 5, 50)],
        ):
            candidates[row["id"]] = row
    lemma_segments = set()
    for row in con.execute(
        """SELECT work_id,segment_id FROM lemmas
           WHERE surface=? OR lemma=? OR surface=? OR lemma=? LIMIT 500""",
        (norm, norm, folded, folded),
    ):
        lemma_segments.add((row["work_id"], row["segment_id"]))
    ranked = []
    for row in candidates.values():
        raw = row["raw_text"]
        cjk_candidate = cjk_query is not None and row["language"] in {"lzh", "zh"}
        row_norm = row["norm_text"] or (normalize(raw) if cjk_candidate else "")
        row_folded = row["folded_text"] or (
            fold_diacritics(raw) if cjk_candidate else ""
        )
        row_compact = row["compact_text"] or (compact(raw) if cjk_candidate else "")
        score = EVIDENCE_WEIGHT.get(row["evidence_class"], 0)
        reasons = []
        if query in raw:
            score += 120
            reasons.append("exact")
        elif norm in row_norm:
            score += 95
            reasons.append("normalized")
        elif folded in row_folded:
            score += 75
            reasons.append("diacritic-folded")
        elif comp and comp in row_compact:
            score += 70
            reasons.append("compact-unicode")
        else:
            score += 30
            reasons.append("fts")
        has_lemma_form = any(
            form and (
                form in row_norm
                or fold_diacritics(form) in row_folded
                or compact(form) in row_compact
            )
            for form in lemma_forms - {norm}
        )
        if (
            (row["work_id"], row["segment_id"]) in lemma_segments
            or norm in row["lemma_text"].split()
            or has_lemma_form
        ):
            score += 80
            reasons.append("corpus-lemma")
        if row["segment_id"]:
            score += 5
        item = _row(row)
        item["score"] = score
        item["match_reasons"] = reasons
        ranked.append(item)
    ranked.sort(key=lambda x: (-x["score"], x["corpus"], x["source_path"], x["sequence_no"]))
    con.close()
    return {
        "query": query,
        "results": ranked[:limit],
        "result_count": min(len(ranked), limit),
        "fail_closed": not ranked,
        "message": None if ranked else "không đủ dữ liệu trong corpus hiện tại",
        "search_index_version": search_index_version,
        "cjk_substring_index_available": cjk_index_available,
        "limitations": limitations,
    }


def context(db_path: Path, record_id: int, window: int = 2) -> dict:
    con = connect_readonly(db_path)
    target = con.execute("SELECT * FROM records WHERE id=?", (record_id,)).fetchone()
    if not target:
        con.close()
        return {"record_id": record_id, "found": False, "message": "không đủ dữ liệu trong corpus hiện tại"}
    rows = con.execute(
        """SELECT * FROM records
           WHERE corpus=? AND work_id IS ? AND source_path=?
             AND sequence_no BETWEEN ? AND ?
           ORDER BY sequence_no""",
        (
            target["corpus"],
            target["work_id"],
            target["source_path"],
            target["sequence_no"] - window,
            target["sequence_no"] + window,
        ),
    )
    result = [_row(r) for r in rows]
    con.close()
    return {"record_id": record_id, "found": True, "context": result}


def work(db_path: Path, identifier: str) -> dict:
    con = connect_readonly(db_path)
    works = [_row(r) for r in con.execute("SELECT * FROM works WHERE work_id=? ORDER BY corpus", (identifier,))]
    records = [
        _row(r)
        for r in con.execute(
            """SELECT id,corpus,language,work_id,segment_id,title,source_path,
                      source_sha,evidence_class,witness,sequence_no
               FROM records WHERE work_id=? ORDER BY corpus,sequence_no LIMIT 100""",
            (identifier,),
        )
    ]
    con.close()
    return {
        "identifier": identifier,
        "works": works,
        "records": records,
        "found": bool(works or records),
        "message": None if works or records else "không đủ dữ liệu trong corpus hiện tại",
    }


def parallels(db_path: Path, identifier: str) -> dict:
    con = connect_readonly(db_path)
    rows = [
        _row(r)
        for r in con.execute(
            """SELECT * FROM relations
               WHERE from_id=? OR to_id=? OR from_id LIKE ? OR to_id LIKE ?
               ORDER BY relation_type,from_id,to_id LIMIT 500""",
            (identifier, identifier, identifier + "#%", identifier + "#%"),
        )
    ]
    con.close()
    return {
        "identifier": identifier,
        "relations": rows,
        "found": bool(rows),
        "message": None if rows else "không đủ dữ liệu trong corpus hiện tại",
    }


def _parse_cbeta_identifier(identifier: str) -> tuple[str, str | None, str | None] | None:
    range_match = re.fullmatch(
        r"([A-Za-z]{1,4}\d{1,3}[nN]\d{4,5}[a-z]?):"
        r"(\d{3,4}[a-c]\d{1,2}[a-z]?)"
        r"(?:\.\.(\d{3,4}[a-c]\d{1,2}[a-z]?))?",
        identifier,
        re.I,
    )
    if range_match:
        work_id = normalize_cbeta_work_id(range_match.group(1))
        start_anchor = normalize_taisho_line(range_match.group(2))
        end_anchor = normalize_taisho_line(range_match.group(3) or range_match.group(2))
        start_key = taisho_line_key(start_anchor) if start_anchor else None
        end_key = taisho_line_key(end_anchor) if end_anchor else None
        if (
            work_id
            and start_anchor
            and end_anchor
            and start_key is not None
            and end_key is not None
            and start_key <= end_key
        ):
            return work_id, start_anchor, end_anchor
        return None
    work_id = normalize_cbeta_work_id(identifier)
    return (work_id, None, None) if work_id else None


def _record_cbeta_interval(
    item: dict,
    expected_work_id: str,
) -> tuple[tuple[int, int, int, str], tuple[int, int, int, str], str] | None:
    record_work_id = normalize_cbeta_work_id(item.get("work_id") or "")
    if record_work_id != expected_work_id:
        return None

    relation_ids = item.get("relation_ids") or []
    if len(relation_ids) >= 2:
        first = _parse_cbeta_identifier(str(relation_ids[0]))
        last = _parse_cbeta_identifier(str(relation_ids[-1]))
        if first and last:
            first_work, first_start, _first_end = first
            last_work, _last_start, last_end = last
            record_start = taisho_line_key(first_start) if first_start else None
            record_end = taisho_line_key(last_end) if last_end else None
            if (
                first_work == expected_work_id
                and last_work == expected_work_id
                and record_start is not None
                and record_end is not None
                and record_start <= record_end
            ):
                return record_start, record_end, "relation_ids"

    segment = _parse_cbeta_identifier(item.get("segment_id") or "")
    if not segment:
        return None
    segment_work, segment_start, segment_end = segment
    record_start = taisho_line_key(segment_start) if segment_start else None
    record_end = taisho_line_key(segment_end) if segment_end else None
    if (
        segment_work != expected_work_id
        or record_start is None
        or record_end is None
        or record_start > record_end
    ):
        return None
    return record_start, record_end, "segment_id"


def _resolve_cbeta_records(
    con: sqlite3.Connection,
    work_id: str,
    start_anchor: str | None,
    end_anchor: str | None,
    limit: int,
) -> list[dict]:
    rows = con.execute(
        """SELECT * FROM records
           WHERE work_id COLLATE NOCASE = ?
             AND corpus IN ('cbeta-bm','cbeta-tei')
           ORDER BY corpus,sequence_no""",
        (work_id,),
    )
    resolved: list[dict] = []
    target_start = taisho_line_key(start_anchor) if start_anchor else None
    target_end = taisho_line_key(end_anchor) if end_anchor else None
    for row in rows:
        item = _row(row)
        if target_start is not None and target_end is not None:
            interval = _record_cbeta_interval(item, work_id)
            if interval is None:
                continue
            record_start, record_end, locator = interval
            if record_end < target_start or record_start > target_end:
                continue
            item["resolution_reason"] = "taisho_range_overlap"
            item["resolution_locator"] = locator
        else:
            item["resolution_reason"] = "cbeta_work_id"
        resolved.append(item)
        if len(resolved) >= limit:
            break
    return resolved


def resolve(db_path: Path, identifier: str, limit: int = 100) -> dict:
    con = connect_readonly(db_path)
    parsed = _parse_cbeta_identifier(identifier)
    bridge_relations: list[dict] = []
    requests: list[tuple[str, str | None, str | None]] = []
    if parsed:
        requests.append(parsed)
    else:
        bridge_relations = [
            _row(row)
            for row in con.execute(
                """SELECT * FROM relations
                   WHERE from_id=?
                     AND relation_type IN (
                       'suttacentral_cbeta:work',
                       'suttacentral_cbeta:line_range'
                     )
                   ORDER BY relation_type,to_id""",
                (identifier,),
            )
        ]
        range_relations = [
            row
            for row in bridge_relations
            if row["relation_type"] == "suttacentral_cbeta:line_range"
        ]
        targets = range_relations or [
            row
            for row in bridge_relations
            if row["relation_type"] == "suttacentral_cbeta:work"
        ]
        for relation in targets:
            target = _parse_cbeta_identifier(relation["to_id"])
            if target:
                requests.append(target)
    resolved_by_id: dict[int, dict] = {}
    for work_id, start_anchor, end_anchor in requests:
        for item in _resolve_cbeta_records(
            con,
            work_id,
            start_anchor,
            end_anchor,
            limit,
        ):
            resolved_by_id[item["id"]] = item
            if len(resolved_by_id) >= limit:
                break
        if len(resolved_by_id) >= limit:
            break
    con.close()
    resolved = list(resolved_by_id.values())
    if parsed:
        work_id, start_anchor, end_anchor = parsed
        normalized = work_id
        if start_anchor and end_anchor:
            normalized = f"{work_id}:{start_anchor}..{end_anchor}"
    else:
        normalized = identifier
    return {
        "identifier": identifier,
        "normalized_identifier": normalized,
        "bridge_relations": bridge_relations,
        "records": resolved,
        "found": bool(resolved),
        "message": None if resolved else "không đủ dữ liệu trong corpus hiện tại",
    }


def variants(db_path: Path, identifier: str) -> dict:
    con = connect_readonly(db_path)
    rows = [
        _row(r)
        for r in con.execute(
            """SELECT * FROM variants
               WHERE work_id=? OR segment_id=? OR segment_id LIKE ?
               ORDER BY corpus,segment_id,id LIMIT 500""",
            (identifier, identifier, identifier + "%"),
        )
    ]
    con.close()
    return {
        "identifier": identifier,
        "variants": rows,
        "found": bool(rows),
        "message": None if rows else "không đủ dữ liệu trong corpus hiện tại",
    }


def provenance(db_path: Path, record_id: int) -> dict:
    con = connect_readonly(db_path)
    row = con.execute("SELECT * FROM records WHERE id=?", (record_id,)).fetchone()
    con.close()
    if not row:
        return {"record_id": record_id, "found": False, "message": "không đủ dữ liệu trong corpus hiện tại"}
    item = _row(row)
    return {
        "record_id": record_id,
        "found": True,
        "provenance": {
            key: item.get(key)
            for key in (
                "corpus",
                "source_path",
                "work_id",
                "segment_id",
                "source_sha",
                "evidence_class",
                "witness",
                "language",
                "collection_name",
                "relation_ids",
            )
        },
        "text": item["raw_text"],
    }


def compare(db_path: Path, identifiers: list[str]) -> dict:
    con = connect_readonly(db_path)
    groups = []
    for identifier in identifiers:
        rows = [
            _row(r)
            for r in con.execute(
                """SELECT * FROM records
                   WHERE work_id=? OR segment_id=?
                   ORDER BY evidence_class,corpus,sequence_no LIMIT 50""",
                (identifier, identifier),
            )
        ]
        groups.append({"identifier": identifier, "records": rows})
    con.close()
    found = any(group["records"] for group in groups)
    return {
        "comparanda": groups,
        "found": found,
        "harmonized": False,
        "message": None if found else "không đủ dữ liệu trong corpus hiện tại",
    }
