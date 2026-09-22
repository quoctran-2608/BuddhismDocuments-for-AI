from __future__ import annotations

import csv
import gzip
import html
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable, Iterator

from .model import Record, Work, normalize, relative, work_from_segment

PARSER_VERSION = "2026-09-22.6"
TEI = "{http://www.tei-c.org/ns/1.0}"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
RDF_ABOUT = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"
RDF_RESOURCE = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"

EVIDENCE_WEIGHT = {
    "canonical_root": 70,
    "authoritative_structured": 65,
    "metadata_relationship": 35,
    "parallel_alignment": 25,
    "computational_segmented": 15,
    "derived_critical_lemma": 30,
    "auxiliary_reference": 10,
}


def local_sha(root: Path, repo: str) -> str:
    path = root / repo
    if not (path / ".git").exists():
        raise FileNotFoundError(f"missing local submodule: {repo}")
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(f"cannot read local SHA for {repo}: {result.stderr.strip()}")
    return result.stdout.strip()


def connect(db_path: Path, schema_path: Path | None = None) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    con.execute("PRAGMA temp_store=MEMORY")
    if schema_path:
        con.executescript(schema_path.read_text(encoding="utf-8"))
    return con


def connect_readonly(db_path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(
        f"file:{db_path.resolve()}?mode=ro&immutable=1",
        uri=True,
        timeout=5,
    )
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA query_only=ON")
    return con


class Writer:
    def __init__(self, con: sqlite3.Connection):
        self.con = con
        self.records = self.works = self.relations = self.variants = self.lemmas = 0
        self._record_rows: list[tuple] = []
        self._relation_rows: list[tuple] = []
        self._variant_rows: list[tuple] = []
        self._lemma_rows: list[tuple] = []
        self.batch_size = 5000

    def add_record(self, rec: Record) -> None:
        if not rec.text.strip():
            return
        self._record_rows.append(rec.row())
        if len(self._record_rows) >= self.batch_size:
            self._flush_records()

    def _flush_records(self) -> None:
        if not self._record_rows:
            return
        before = self.con.total_changes
        self.con.executemany(
            """INSERT OR IGNORE INTO records(
               corpus,language,collection_name,work_id,segment_id,title,raw_text,
               norm_text,folded_text,compact_text,lemma_text,source_path,source_sha,
               evidence_class,witness,relation_ids,sequence_no)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            self._record_rows,
        )
        self.records += self.con.total_changes - before
        self._record_rows.clear()

    def add_work(self, work: Work) -> None:
        self.con.execute(
            """INSERT OR REPLACE INTO works(
               corpus,work_id,language,collection_name,title,metadata_json,
               source_path,source_sha,evidence_class) VALUES (?,?,?,?,?,?,?,?,?)""",
            work.row(),
        )
        self.works += 1

    def add_relation(
        self,
        corpus: str,
        relation_type: str,
        from_id: str,
        to_id: str,
        source_path: str,
        source_sha: str,
        evidence_class: str,
        details: dict | None = None,
    ) -> None:
        self._relation_rows.append(
            (
                corpus,
                relation_type,
                from_id,
                to_id,
                json.dumps(details or {}, ensure_ascii=False),
                source_path,
                source_sha,
                evidence_class,
            )
        )
        if len(self._relation_rows) >= self.batch_size:
            self._flush_relations()

    def _flush_relations(self) -> None:
        if not self._relation_rows:
            return
        before = self.con.total_changes
        self.con.executemany(
            """INSERT OR IGNORE INTO relations(
               corpus,relation_type,from_id,to_id,details_json,source_path,
               source_sha,evidence_class) VALUES (?,?,?,?,?,?,?,?)""",
            self._relation_rows,
        )
        self.relations += self.con.total_changes - before
        self._relation_rows.clear()

    def add_variant(
        self,
        corpus: str,
        work_id: str | None,
        segment_id: str | None,
        reading: str,
        source_path: str,
        source_sha: str,
        evidence_class: str,
        lemma: str | None = None,
        witnesses: str | None = None,
        variant_type: str | None = None,
        confidence: float | None = None,
        notes: str | None = None,
    ) -> None:
        self._variant_rows.append(
            (
                corpus,
                work_id,
                segment_id,
                lemma,
                reading,
                witnesses,
                variant_type,
                confidence,
                notes,
                source_path,
                source_sha,
                evidence_class,
            )
        )
        if len(self._variant_rows) >= self.batch_size:
            self._flush_variants()

    def _flush_variants(self) -> None:
        if not self._variant_rows:
            return
        self.con.executemany(
            """INSERT INTO variants(
               corpus,work_id,segment_id,lemma,reading,witnesses,variant_type,
               confidence,notes,source_path,source_sha,evidence_class)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            self._variant_rows,
        )
        self.variants += len(self._variant_rows)
        self._variant_rows.clear()

    def add_lemma(
        self,
        corpus: str,
        language: str,
        work_id: str | None,
        segment_id: str | None,
        surface: str,
        lemma: str,
        source_path: str,
        source_sha: str,
        evidence_class: str,
        pos: str | None = None,
        morphology: dict | None = None,
    ) -> None:
        self._lemma_rows.append(
            (
                corpus,
                language,
                work_id,
                segment_id,
                surface,
                lemma,
                pos,
                json.dumps(morphology or {}, ensure_ascii=False),
                source_path,
                source_sha,
                evidence_class,
            )
        )
        if len(self._lemma_rows) >= self.batch_size:
            self._flush_lemmas()

    def _flush_lemmas(self) -> None:
        if not self._lemma_rows:
            return
        self.con.executemany(
            """INSERT INTO lemmas(
               corpus,language,work_id,segment_id,surface,lemma,pos,morphology_json,
               source_path,source_sha,evidence_class) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            self._lemma_rows,
        )
        self.lemmas += len(self._lemma_rows)
        self._lemma_rows.clear()

    def flush(self) -> None:
        self._flush_records()
        self._flush_relations()
        self._flush_variants()
        self._flush_lemmas()


def _json_files(base: Path, pattern: str, acceptance: list[str] | None = None) -> Iterable[Path]:
    if acceptance is not None:
        return [base / p for p in acceptance if (base / p).exists()]
    return base.glob(pattern)


def _language_from_bilara(path: Path, base: Path) -> str | None:
    parts = path.relative_to(base).parts
    if not parts:
        return None
    if parts[0] in {"root", "variant", "reference"} and len(parts) > 1:
        return parts[1]
    if parts[0] in {"translation", "comment"} and len(parts) > 1:
        return parts[1]
    return None


def index_bilara(root: Path, sha: str, writer: Writer, profile: str) -> None:
    base = root / "suttacentral/bilara-data"
    corpus = "suttacentral-bilara"
    evidence = "canonical_root"
    selected = [
        "root/pli/ms/sutta/mn/mn1_root-pli-ms.json",
        "translation/en/sujato/sutta/mn/mn1_translation-en-sujato.json",
        "variant/pli/ms/sutta/mn/mn1_variant-pli-ms.json",
    ]
    acceptance = profile == "acceptance"
    if acceptance:
        files = _json_files(base, "**/*.json", selected)
    elif profile == "core":
        files = list(base.glob("root/**/*.json"))
        files.extend(base.glob("translation/en/**/*.json"))
        files.extend(base.glob("variant/**/*.json"))
    else:
        files = base.glob("**/*.json")
    for path in files:
        rel = relative(root, path)
        kind = path.relative_to(base).parts[0]
        if kind not in {"root", "translation", "variant", "comment"}:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        language = _language_from_bilara(path, base)
        witness = path.stem.rsplit("_", 1)[-1]
        if profile == "core" and kind == "variant":
            items = [
                (segment_id, text)
                for segment_id, text in data.items()
                if isinstance(text, str) and text.strip()
            ]
            for chunk_no in range(0, len(items), 50):
                chunk = items[chunk_no : chunk_no + 50]
                first_id, last_id = chunk[0][0], chunk[-1][0]
                reading = "\n".join(f"{segment_id}: {text}" for segment_id, text in chunk)
                writer.add_variant(
                    corpus,
                    work_from_segment(first_id),
                    f"{first_id}..{last_id}",
                    reading,
                    rel,
                    sha,
                    "canonical_root",
                    variant_type="bilara_variant_range",
                    witnesses=witness,
                    notes=f"{len(chunk)} local Bilara variant entries",
                )
            continue
        if profile == "core" and kind != "variant":
            items = [
                (segment_id, text)
                for segment_id, text in data.items()
                if isinstance(text, str) and text.strip()
            ]
            for chunk_no in range(0, len(items), 50):
                chunk = items[chunk_no : chunk_no + 50]
                first_id, last_id = chunk[0][0], chunk[-1][0]
                work_id = work_from_segment(first_id)
                joined = " ".join(
                    html.unescape(re.sub(r"<[^>]+>", " ", text))
                    for _, text in chunk
                )
                writer.add_record(
                    Record(
                        corpus,
                        language,
                        path.parts[-3] if len(path.parts) > 3 else None,
                        work_id,
                        f"{first_id}..{last_id}",
                        None,
                        joined,
                        rel,
                        sha,
                        evidence if kind == "root" else "authoritative_structured",
                        witness=f"{kind}:{witness}",
                        relation_ids=[first_id, last_id],
                        sequence_no=chunk_no // 50,
                    )
                )
            continue
        for sequence, (segment_id, text) in enumerate(data.items()):
            if not isinstance(text, str) or not text.strip():
                continue
            work_id = work_from_segment(segment_id)
            if kind == "variant":
                writer.add_variant(
                    corpus,
                    work_id,
                    segment_id,
                    text,
                    rel,
                    sha,
                    "canonical_root",
                    variant_type="bilara_variant",
                    witnesses=witness,
                )
                continue
            cls = evidence if kind == "root" else "authoritative_structured"
            writer.add_record(
                Record(
                    corpus,
                    language,
                    path.parts[-3] if len(path.parts) > 3 else None,
                    work_id,
                    segment_id,
                    None,
                    html.unescape(re.sub(r"<[^>]+>", " ", text)),
                    rel,
                    sha,
                    cls,
                    witness=f"{kind}:{witness}",
                    sequence_no=sequence,
                )
            )


def index_sc_relations(root: Path, sha: str, writer: Writer, profile: str) -> None:
    base = root / "suttacentral/sc-data"
    corpus = "suttacentral-relations"
    evidence = "metadata_relationship"
    rel_path = base / "relationship/new_parallels.json"
    data = json.loads(rel_path.read_text(encoding="utf-8"))
    if profile == "acceptance":
        data = {"an1.1-5": data["an1.1-5"]}
    for from_id, groups in data.items():
        for relation_type, targets in groups.items():
            for to_id in targets:
                writer.add_relation(
                    corpus,
                    f"suttacentral_parallel:{relation_type}",
                    from_id,
                    to_id,
                    relative(root, rel_path),
                    sha,
                    evidence,
                )
                writer.add_relation(
                    corpus,
                    f"suttacentral_parallel:{relation_type}",
                    to_id,
                    from_id,
                    relative(root, rel_path),
                    sha,
                    evidence,
                )
    info_path = base / "structure/text_extra_info.json"
    info = json.loads(info_path.read_text(encoding="utf-8"))
    if profile == "acceptance":
        info = [item for item in info if item.get("uid") in {"an1.1-5", "ea9.7", "mn1"}]
    for item in info:
        uid = item.get("uid")
        if uid:
            writer.add_work(
                Work(
                    corpus,
                    uid,
                    None,
                    None,
                    item.get("acronym"),
                    item,
                    relative(root, info_path),
                    sha,
                    evidence,
                )
            )


def _cbeta_title(root_el: ET.Element) -> str | None:
    for element in root_el.findall(f".//{TEI}title"):
        lang = element.get(XML_ID.replace("id", "lang"))
        level = element.get("level")
        text = " ".join("".join(element.itertext()).split())
        if text and (lang == "zh-Hant" or level == "m"):
            return text
    return None


def _cbeta_lines(path: Path) -> tuple[str, str | None, list[tuple[str, str]], list[dict]]:
    root_el = ET.parse(path).getroot()
    work_id = root_el.get(XML_ID) or path.stem
    title = _cbeta_title(root_el)
    body = root_el.find(f".//{TEI}body")
    if body is None:
        return work_id, title, [], []
    lines: list[tuple[str, str]] = []
    variants: list[dict] = []
    current_id = f"{work_id}:head"
    buf: list[str] = []

    def flush() -> None:
        text = " ".join("".join(buf).split())
        if text:
            lines.append((current_id, text))
        buf.clear()

    def walk(element: ET.Element) -> None:
        nonlocal current_id
        tag = element.tag.rsplit("}", 1)[-1]
        if tag == "lb":
            flush()
            current_id = element.get("n") or current_id
        if element.text and tag not in {"note", "rdg"}:
            buf.append(element.text)
        for child in element:
            walk(child)
            if child.tail:
                buf.append(child.tail)

    walk(body)
    flush()
    # CBETA stores much of the critical apparatus outside <body>, linked back
    # to anchors by app/@from and app/@to. Parse it across the whole document.
    for app in root_el.findall(f".//{TEI}app"):
        lem = app.find(f"{TEI}lem")
        readings = []
        for rdg in app.findall(f"{TEI}rdg"):
            readings.append(
                {
                    "reading": " ".join("".join(rdg.itertext()).split()),
                    "witnesses": rdg.get("wit"),
                    "responsibility": rdg.get("resp"),
                }
            )
        variants.append(
            {
                "line": (app.get("from") or app.get("to") or "apparatus").lstrip("#"),
                "lemma": " ".join("".join(lem.itertext()).split()) if lem is not None else "",
                "lemma_witness": lem.get("wit") if lem is not None else None,
                "readings": readings,
            }
        )
    return work_id, title, lines, variants


def index_cbeta(root: Path, sha: str, writer: Writer, profile: str) -> None:
    base = root / "cbeta/xml-p5"
    paths = [base / "T/T01/T01n0001.xml"] if profile == "acceptance" else base.glob("*/*/*.xml")
    for path in paths:
        work_id, title, lines, variants = _cbeta_lines(path)
        rel = relative(root, path)
        collection = path.relative_to(base).parts[0]
        writer.add_work(
            Work(
                "cbeta-tei",
                work_id,
                "lzh",
                collection,
                title,
                {"cbeta_id": work_id},
                rel,
                sha,
                "authoritative_structured",
            )
        )
        for sequence, (line_id, text) in enumerate(lines):
            writer.add_record(
                Record(
                    "cbeta-tei",
                    "lzh",
                    collection,
                    work_id,
                    f"{work_id}:{line_id}",
                    title,
                    text,
                    rel,
                    sha,
                    "authoritative_structured",
                    witness=collection,
                    sequence_no=sequence,
                )
            )
        for apparatus in variants:
            for reading in apparatus["readings"]:
                writer.add_variant(
                    "cbeta-tei",
                    work_id,
                    f"{work_id}:{apparatus['line']}",
                    reading["reading"] or "[omission]",
                    rel,
                    sha,
                    "authoritative_structured",
                    lemma=apparatus["lemma"],
                    witnesses=reading["witnesses"],
                    variant_type="cbeta_app",
                    notes=reading["responsibility"],
                )


def index_cbeta_bm(root: Path, sha: str, writer: Writer, profile: str) -> None:
    if profile == "acceptance":
        return
    base = root / "cbeta/BM_u8"
    pattern = re.compile(r"^([A-Z]+\d+n\d+)_p([0-9a-z]+).{4}(.*)$")
    for path in base.glob("*/*/new.txt"):
        rel = relative(root, path)
        sequence = 0
        current_work: str | None = None
        first_line: str | None = None
        last_line: str | None = None
        chunk: list[str] = []

        def flush() -> None:
            nonlocal sequence, first_line, last_line
            if not current_work or not first_line or not last_line or not chunk:
                return
            writer.add_record(
                Record(
                    "cbeta-bm",
                    "lzh",
                    path.relative_to(base).parts[0],
                    current_work,
                    f"{current_work}:{first_line}..{last_line}",
                    None,
                    " ".join(chunk),
                    rel,
                    sha,
                    "canonical_root",
                    witness="CBETA BM_u8",
                    relation_ids=[f"{current_work}:{first_line}", f"{current_work}:{last_line}"],
                    sequence_no=sequence,
                )
            )
            sequence += 1
            first_line = last_line = None
            chunk.clear()

        with path.open(encoding="utf-8", errors="replace") as handle:
            for raw in handle:
                match = pattern.match(raw)
                if not match:
                    continue
                work_id, line_id, text = match.groups()
                clean = re.sub(r"<[^>]+>|\[[^\]]+\]", " ", text).strip()
                if profile == "core":
                    if current_work is not None and (work_id != current_work or len(chunk) >= 300):
                        flush()
                    current_work = work_id
                    first_line = first_line or line_id
                    last_line = line_id
                    if clean:
                        chunk.append(clean)
                    continue
                writer.add_record(
                    Record(
                        "cbeta-bm",
                        "lzh",
                        path.relative_to(base).parts[0],
                        work_id,
                        f"{work_id}:{line_id}",
                        None,
                        clean,
                        rel,
                        sha,
                        "canonical_root",
                        witness="CBETA BM_u8",
                        sequence_no=sequence,
                    )
                )
                sequence += 1
        if profile == "core":
            flush()


def _tei_titles(root_el: ET.Element) -> list[dict]:
    titles = []
    for e in root_el.findall(f".//{TEI}title"):
        text = " ".join("".join(e.itertext()).split())
        if text:
            titles.append(
                {
                    "text": text,
                    "lang": e.get("{http://www.w3.org/XML/1998/namespace}lang"),
                    "type": e.get("type"),
                }
            )
    return titles


def index_84000_tei(root: Path, sha: str, writer: Writer, profile: str) -> None:
    base = root / "84000/data-tei"
    sample = base / "translations/kangyur/translations/001-001_toh1-1_chapter_on_going_forth.xml"
    paths = [sample] if profile == "acceptance" else base.glob("translations/**/translations/*.xml")
    for path in paths:
        try:
            root_el = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        body = root_el.find(f".//{TEI}body")
        if body is None:
            continue
        titles = _tei_titles(root_el)
        title = next((x["text"] for x in titles if x["lang"] == "en" and x["type"] == "mainTitle"), None)
        idno = root_el.find(f".//{TEI}publicationStmt/{TEI}idno")
        work_id = idno.get(XML_ID) if idno is not None else path.stem
        bibl = root_el.find(f".//{TEI}sourceDesc/{TEI}bibl")
        toh = bibl.get("key") if bibl is not None else None
        rel = relative(root, path)
        writer.add_work(
            Work(
                "84000-tei",
                work_id,
                "en",
                "kangyur" if "kangyur" in path.parts else "tengyur",
                title,
                {"titles": titles, "toh": toh, "bibl": " ".join("".join(bibl.itertext()).split()) if bibl is not None else None},
                rel,
                sha,
                "authoritative_structured",
            )
        )
        current_segment = work_id
        sequence = 0
        for element in body.iter():
            tag = element.tag.rsplit("}", 1)[-1]
            if tag == "milestone" and element.get(XML_ID):
                current_segment = element.get(XML_ID)
            if tag not in {"head", "p", "l"}:
                continue
            if any(child.tag.rsplit("}", 1)[-1] in {"p", "l"} for child in element):
                continue
            text = " ".join("".join(element.itertext()).split())
            if not text:
                continue
            segment = element.get(XML_ID) or current_segment or f"{work_id}:{sequence}"
            writer.add_record(
                Record(
                    "84000-tei",
                    "en",
                    "kangyur" if "kangyur" in path.parts else "tengyur",
                    work_id,
                    segment,
                    title,
                    text,
                    rel,
                    sha,
                    "authoritative_structured",
                    witness=toh,
                    relation_ids=[toh] if toh else [],
                    sequence_no=sequence,
                )
            )
            sequence += 1


def index_84000_rdf(root: Path, sha: str, writer: Writer, profile: str) -> None:
    base = root / "84000/data-rdf"
    paths = [base / "toh1-1.rdf"] if profile == "acceptance" else base.glob("*.rdf")
    for path in paths:
        try:
            root_el = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        rel = relative(root, path)
        for desc in list(root_el):
            subject = desc.get(RDF_ABOUT)
            if not subject:
                continue
            subject_id = subject.rsplit("/", 1)[-1]
            labels = []
            for child in desc:
                tag = child.tag.rsplit("}", 1)[-1]
                resource = child.get(RDF_RESOURCE)
                text = " ".join("".join(child.itertext()).split())
                if tag in {"prefLabel", "altLabel"} and text:
                    labels.append(
                        {
                            "text": text,
                            "lang": child.get("{http://www.w3.org/XML/1998/namespace}lang"),
                            "type": tag,
                        }
                    )
                if resource and tag in {
                    "sameAs",
                    "workHasTranslation",
                    "workTranslationOf",
                    "workHasInstance",
                    "instanceOf",
                    "partOf",
                }:
                    writer.add_relation(
                        "84000-rdf",
                        f"84000:{tag}",
                        subject_id,
                        resource.rsplit("/", 1)[-1],
                        rel,
                        sha,
                        "metadata_relationship",
                    )
            if labels:
                writer.add_work(
                    Work(
                        "84000-rdf",
                        subject_id,
                        labels[0].get("lang"),
                        None,
                        labels[0]["text"],
                        {"labels": labels},
                        rel,
                        sha,
                        "metadata_relationship",
                    )
                )


def index_84000_tm(root: Path, sha: str, writer: Writer, profile: str) -> None:
    base = root / "84000/data-translation-memory"
    paths = [base / "json/UT22084-001-001.json"] if profile == "acceptance" else base.glob("json/*.json")
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        work_id = data.get("text-id") or path.stem
        rel = relative(root, path)
        for sequence, unit in enumerate(data.get("tus", [])):
            group = f"{work_id}:tu:{sequence + 1}"
            segment = unit.get("passage-xmlId") or group
            for lang, field in (("bo", "tibetan"), ("en", "english")):
                text = unit.get(field) or ""
                writer.add_record(
                    Record(
                        "84000-tm",
                        lang,
                        None,
                        work_id,
                        f"{group}:{lang}",
                        None,
                        text,
                        rel,
                        sha,
                        "parallel_alignment",
                        witness=unit.get("creation_method"),
                        relation_ids=[group, segment, unit.get("folio") or ""],
                        sequence_no=sequence,
                    )
                )
            writer.add_relation(
                "84000-tm",
                "translation_alignment",
                f"{group}:bo",
                f"{group}:en",
                rel,
                sha,
                "parallel_alignment",
                {"passage_id": segment, "folio": unit.get("folio"), "creation_method": unit.get("creation_method")},
            )


def index_openpecha(root: Path, sha: str, writer: Writer, profile: str) -> None:
    base = root / "openpecha/C0A2DD042"
    catalog_path = base / "text-pairs-catalog.csv"
    catalog: dict[str, dict] = {}
    with catalog_path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            catalog[row["file"]] = row
    groups: dict[str, list[Path]] = defaultdict(list)
    for path in (base / "text-pairs").glob("*.txt"):
        groups[path.stem.rsplit("-", 1)[0]].append(path)
    if profile == "acceptance":
        groups = {k: v for k, v in groups.items() if k == "A00023033"}
    for work_id, paths in groups.items():
        language_lines: dict[str, list[str]] = {}
        for path in paths:
            language = path.stem.rsplit("-", 1)[1]
            language_lines[language] = path.read_text(encoding="utf-8", errors="replace").splitlines()
        max_lines = max((len(lines) for lines in language_lines.values()), default=0)
        for sequence in range(max_lines):
            group_id = f"{work_id}:line:{sequence + 1}"
            members = []
            for language, lines in language_lines.items():
                if sequence >= len(lines):
                    continue
                path = next(p for p in paths if p.stem.endswith("-" + language))
                segment_id = f"{group_id}:{language}"
                members.append(segment_id)
                meta = catalog.get(path.name, {})
                writer.add_record(
                    Record(
                        "openpecha",
                        language,
                        "C0A2DD042",
                        work_id,
                        segment_id,
                        meta.get("title"),
                        lines[sequence],
                        relative(root, path),
                        sha,
                        "parallel_alignment",
                        witness=meta.get("source"),
                        relation_ids=[group_id],
                        sequence_no=sequence,
                    )
                )
            for member in members[1:]:
                writer.add_relation(
                    "openpecha",
                    "line_alignment",
                    members[0],
                    member,
                    relative(root, catalog_path),
                    sha,
                    "parallel_alignment",
                    {"group_id": group_id},
                )


def _load_segmented(path: Path) -> dict:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as handle:
        data = json.load(handle)
    return data if isinstance(data, dict) else {}


def index_buddhanexus(root: Path, sha: str, writer: Writer, corpus: str, profile: str) -> None:
    specs = {
        "buddhanexus-pali": (
            root / "buddhanexus/segmented-pali",
            "pli",
            "inputfiles_cut_segments_on_typography/*.json",
            ["inputfiles_cut_segments_on_typography/ds1.1.json"],
        ),
        "buddhanexus-chinese": (
            root / "buddhanexus/segmented-chinese",
            "lzh",
            "files_segmented_by_sentence/*.json.gz",
            ["files_segmented_by_sentence/T01n0001_001.json.gz"],
        ),
        "buddhanexus-sanskrit": (
            root / "buddhanexus/segmented-sanskrit",
            "san",
            "segmented_files/*.json",
            ["segmented_files/GE07bhgce__u.json"],
        ),
    }
    base, language, pattern, samples = specs[corpus]
    paths = [base / p for p in samples] if profile == "acceptance" else base.glob(pattern)
    for path in paths:
        work_id = path.name.split(".json", 1)[0]
        rel = relative(root, path)
        for sequence, (segment_id, text) in enumerate(_load_segmented(path).items()):
            writer.add_record(
                Record(
                    corpus,
                    language,
                    None,
                    work_from_segment(segment_id) or work_id,
                    segment_id,
                    None,
                    str(text),
                    rel,
                    sha,
                    "computational_segmented",
                    witness="BuddhaNexus",
                    sequence_no=sequence,
                )
            )


def index_pts(root: Path, sha: str, writer: Writer, profile: str) -> None:
    base = root / "pts/pts-archive"
    paths = [base / "texts/09-mn-i.txt"] if profile == "acceptance" else (base / "texts").glob("*.txt")
    page_re = re.compile(r"^page\s+(\d+)\s*$")
    for path in paths:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        title = lines[0].strip() if lines else path.stem
        page = None
        buf: list[str] = []
        sequence = 0

        def flush() -> None:
            nonlocal sequence
            text = "\n".join(buf).strip()
            if page and text:
                writer.add_record(
                    Record(
                        "pts-archive",
                        "pli",
                        None,
                        title,
                        f"{title}:page:{page}",
                        title,
                        text,
                        relative(root, path),
                        sha,
                        "auxiliary_reference",
                        witness="Dhammakaya PaliText V2.5 export",
                        sequence_no=sequence,
                    )
                )
                sequence += 1
            buf.clear()

        for line in lines:
            match = page_re.match(line.strip())
            if match:
                flush()
                page = match.group(1)
            elif set(line.strip()) == {"="}:
                continue
            else:
                buf.append(line)
        flush()


def index_pali_derived(root: Path, sha: str, writer: Writer, profile: str) -> None:
    base = root / "third-party/pali-canon"
    lemma_paths = [base / "data/lemmatized/mn/mn1.json"] if profile == "acceptance" else base.glob("data/lemmatized/**/*.json")
    lemma_lexicon: dict[tuple[str, str, str | None], tuple[str, str, dict]] = {}
    for path in lemma_paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        work_id = data.get("id")
        title = data.get("title_pali")
        rel = relative(root, path)
        for sequence, segment in enumerate(data.get("segments", [])):
            segment_id = segment.get("id")
            tokens = segment.get("tokens", [])
            lemma_text = " ".join(str(t.get("lemma", "")) for t in tokens)
            if profile == "acceptance":
                writer.add_record(
                    Record(
                        "pali-canon-derived",
                        "pli",
                        data.get("collection"),
                        work_id,
                        segment_id,
                        title,
                        segment.get("pali", ""),
                        rel,
                        sha,
                        "derived_critical_lemma",
                        witness="lemmatized SuttaCentral Mahāsaṅgīti",
                        sequence_no=sequence,
                        lemma_text=lemma_text,
                    )
                )
            for token in tokens:
                surface = token.get("word")
                lemma = token.get("lemma")
                if surface and lemma:
                    morphology = {k: v for k, v in token.items() if k not in {"word", "lemma", "pos"}}
                    if profile == "acceptance":
                        writer.add_lemma(
                            "pali-canon-derived",
                            "pli",
                            work_id,
                            segment_id,
                            surface,
                            lemma,
                            rel,
                            sha,
                            "derived_critical_lemma",
                            token.get("pos"),
                            morphology,
                        )
                    else:
                        key = (normalize(surface), normalize(lemma), token.get("pos"))
                        lemma_lexicon.setdefault(key, (rel, title or "", morphology))
    if profile != "acceptance":
        for (surface, lemma, pos), (rel, _title, morphology) in lemma_lexicon.items():
            writer.add_lemma(
                "pali-canon-derived",
                "pli",
                None,
                None,
                surface,
                lemma,
                rel,
                sha,
                "derived_critical_lemma",
                pos,
                morphology,
            )
    critical_paths = [base / "data/critical/mn/mn1_critical.json"] if profile == "acceptance" else base.glob("data/critical/**/*_critical.json")
    for path in critical_paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        rel = relative(root, path)
        work_id = data.get("id")
        for item in data.get("apparatus", []):
            witnesses = json.dumps(item.get("witnesses", {}), ensure_ascii=False)
            selected = item.get("selected")
            if selected:
                writer.add_variant(
                    "pali-canon-derived",
                    work_id,
                    f"{work_id}:token:{item.get('position')}",
                    selected,
                    rel,
                    sha,
                    "derived_critical_lemma",
                    witnesses=witnesses,
                    variant_type=item.get("type"),
                    confidence=item.get("confidence"),
                    notes=item.get("notes"),
                )


SOURCE_BUILDERS: dict[str, tuple[str, str, Callable]] = {
    "suttacentral-bilara": ("suttacentral/bilara-data", "canonical_root", index_bilara),
    "suttacentral-relations": ("suttacentral/sc-data", "metadata_relationship", index_sc_relations),
    "cbeta-tei": ("cbeta/xml-p5", "authoritative_structured", index_cbeta),
    "cbeta-bm": ("cbeta/BM_u8", "canonical_root", index_cbeta_bm),
    "84000-tei": ("84000/data-tei", "authoritative_structured", index_84000_tei),
    "84000-rdf": ("84000/data-rdf", "metadata_relationship", index_84000_rdf),
    "84000-tm": ("84000/data-translation-memory", "parallel_alignment", index_84000_tm),
    "openpecha": ("openpecha/C0A2DD042", "parallel_alignment", index_openpecha),
    "buddhanexus-pali": ("buddhanexus/segmented-pali", "computational_segmented", None),
    "buddhanexus-chinese": ("buddhanexus/segmented-chinese", "computational_segmented", None),
    "buddhanexus-sanskrit": ("buddhanexus/segmented-sanskrit", "computational_segmented", None),
    "pts-archive": ("pts/pts-archive", "auxiliary_reference", index_pts),
    "pali-canon-derived": ("third-party/pali-canon", "derived_critical_lemma", index_pali_derived),
}

PROFILE_SOURCES = {
    "acceptance": list(SOURCE_BUILDERS),
    "core": [
        "suttacentral-bilara",
        "suttacentral-relations",
        "cbeta-bm",
        "84000-tei",
        "84000-rdf",
        "pali-canon-derived",
    ],
    "discovery": [
        "84000-tm",
        "openpecha",
        "buddhanexus-pali",
        "buddhanexus-chinese",
        "buddhanexus-sanskrit",
    ],
    "all": list(SOURCE_BUILDERS),
}


def state_parser_version(corpus: str, profile: str) -> str:
    if profile == "acceptance":
        return f"{PARSER_VERSION}:acceptance"
    if profile == "all" and corpus in {"suttacentral-bilara", "cbeta-bm"}:
        return f"{PARSER_VERSION}:full"
    return PARSER_VERSION


def purge_source(con: sqlite3.Connection, corpus: str) -> None:
    for table in ("records", "works", "relations", "variants", "lemmas"):
        con.execute(f"DELETE FROM {table} WHERE corpus=?", (corpus,))
    con.execute("DELETE FROM source_state WHERE corpus=?", (corpus,))


def build_index(
    root: Path,
    db_path: Path,
    profile: str = "core",
    force: bool = False,
    progress: bool = True,
    only_sources: list[str] | None = None,
    rebuild_fts: bool = True,
) -> dict:
    schema = root / "schema/corpus-index.sql"
    db_path = db_path.resolve()
    use_fast_workspace = str(db_path).startswith("/mnt/")
    workspace_dir: tempfile.TemporaryDirectory[str] | None = None
    work_db = db_path
    if use_fast_workspace:
        workspace_dir = tempfile.TemporaryDirectory(prefix="buddhist-corpus-")
        work_db = Path(workspace_dir.name) / db_path.name
        if db_path.exists():
            source = sqlite3.connect(db_path)
            source.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            source.close()
            shutil.copy2(db_path, work_db)
    con = connect(work_db, schema)
    for trigger in ("records_ai", "records_ad", "records_au"):
        con.execute(f"DROP TRIGGER IF EXISTS {trigger}")
    selected = only_sources or PROFILE_SOURCES[profile]
    invalid = sorted(set(selected) - set(SOURCE_BUILDERS))
    if invalid:
        raise ValueError(f"unknown sources: {', '.join(invalid)}")
    summary = {"profile": profile, "database": str(db_path), "sources": []}
    manifest = {x["rel_dest"]: x["commit_sha"] for x in json.loads((root / "manifest.json").read_text(encoding="utf-8"))}
    def checkpoint() -> None:
        if not use_fast_workspace:
            return
        con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        db_path.parent.mkdir(parents=True, exist_ok=True)
        next_path = db_path.with_name(db_path.name + ".next")
        shutil.copy2(work_db, next_path)
        for suffix in ("-wal", "-shm"):
            Path(str(db_path) + suffix).unlink(missing_ok=True)
        os.replace(next_path, db_path)

    for corpus in selected:
        repo, evidence, builder = SOURCE_BUILDERS[corpus]
        sha = local_sha(root, repo)
        state_version = state_parser_version(corpus, profile)
        if manifest.get(repo) and manifest[repo] != sha:
            raise RuntimeError(f"SHA mismatch for {repo}: manifest={manifest[repo]} local={sha}")
        state = con.execute("SELECT source_sha,parser_version FROM source_state WHERE corpus=?", (corpus,)).fetchone()
        if state and state["source_sha"] == sha and state["parser_version"] == state_version and not force:
            summary["sources"].append({"corpus": corpus, "status": "unchanged", "sha": sha})
            continue
        if progress:
            print(f"[index] {corpus} @ {sha[:12]}", file=sys.stderr, flush=True)
        with con:
            purge_source(con, corpus)
            writer = Writer(con)
            if corpus.startswith("buddhanexus-"):
                index_buddhanexus(root, sha, writer, corpus, profile)
            elif builder:
                builder(root, sha, writer, profile)
            writer.flush()
            con.execute(
                """INSERT INTO source_state(
                   corpus,repo_path,source_sha,parser_version,evidence_class,indexed_at,
                   record_count,relation_count,variant_count,lemma_count)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (
                    corpus,
                    repo,
                    sha,
                    state_version,
                    evidence,
                    datetime.now(timezone.utc).isoformat(),
                    writer.records,
                    writer.relations,
                    writer.variants,
                    writer.lemmas,
                ),
            )
        summary["sources"].append(
            {
                "corpus": corpus,
                "status": "rebuilt",
                "sha": sha,
                "records": writer.records,
                "works": writer.works,
                "relations": writer.relations,
                "variants": writer.variants,
                "lemmas": writer.lemmas,
            }
        )
        checkpoint()
    if rebuild_fts:
        with con:
            con.execute("INSERT INTO records_fts(records_fts) VALUES('rebuild')")
            con.execute("PRAGMA optimize")
        checkpoint()
    con.close()
    if use_fast_workspace:
        workspace_dir.cleanup()
    return summary
