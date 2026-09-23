from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def normalize(text: str) -> str:
    return " ".join(unicodedata.normalize("NFC", text).casefold().split())


def fold_diacritics(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", normalize(text))
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def compact(text: str) -> str:
    return re.sub(r"[\W_]+", "", normalize(text), flags=re.UNICODE)


def work_from_segment(segment_id: str | None) -> str | None:
    if not segment_id:
        return None
    return segment_id.split(":", 1)[0].split("#", 1)[0]


@dataclass(slots=True)
class Record:
    corpus: str
    language: str | None
    collection: str | None
    work_id: str | None
    segment_id: str | None
    title: str | None
    text: str
    source_path: str
    source_sha: str
    evidence_class: str
    witness: str | None = None
    relation_ids: list[str] = field(default_factory=list)
    sequence_no: int = 0
    lemma_text: str = ""

    def row(self) -> tuple[Any, ...]:
        norm_text = normalize(self.text)
        folded_text = fold_diacritics(self.text)
        # Avoid storing several near-identical gigabyte-scale copies for long
        # script-heavy chunks. Derived search indexes can use raw_text directly.
        if self.language in {"lzh", "zh", "bo"} and len(self.text) >= 2_000:
            norm_text = ""
            folded_text = ""
        elif folded_text == norm_text:
            folded_text = ""
        compact_text = compact(self.text) if len(self.text) < 2_000 else ""
        return (
            self.corpus,
            self.language,
            self.collection,
            self.work_id,
            self.segment_id,
            self.title,
            self.text,
            norm_text,
            folded_text,
            compact_text,
            normalize(self.lemma_text),
            self.source_path,
            self.source_sha,
            self.evidence_class,
            self.witness,
            json.dumps(self.relation_ids, ensure_ascii=False),
            self.sequence_no,
        )


@dataclass(slots=True)
class Work:
    corpus: str
    work_id: str
    language: str | None
    collection: str | None
    title: str | None
    metadata: dict[str, Any]
    source_path: str
    source_sha: str
    evidence_class: str

    def row(self) -> tuple[Any, ...]:
        return (
            self.corpus,
            self.work_id,
            self.language,
            self.collection,
            self.title,
            json.dumps(self.metadata, ensure_ascii=False),
            self.source_path,
            self.source_sha,
            self.evidence_class,
        )


def relative(root: Path, path: Path) -> str:
    # Callers pass paths rooted under the already-absolute repository root.
    # A lexical relative path avoids extremely slow realpath calls on WSL mounts.
    return path.relative_to(root).as_posix()
