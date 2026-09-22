from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .index import EVIDENCE_WEIGHT, connect_readonly
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
        score = EVIDENCE_WEIGHT.get(row["evidence_class"], 0)
        reasons = []
        if query in raw:
            score += 120
            reasons.append("exact")
        elif norm in row["norm_text"]:
            score += 95
            reasons.append("normalized")
        elif folded in row["folded_text"]:
            score += 75
            reasons.append("diacritic-folded")
        elif comp and comp in row["compact_text"]:
            score += 70
            reasons.append("compact-unicode")
        else:
            score += 30
            reasons.append("fts")
        has_lemma_form = any(
            form and (
                form in row["norm_text"]
                or fold_diacritics(form) in row["folded_text"]
                or compact(form) in row["compact_text"]
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
