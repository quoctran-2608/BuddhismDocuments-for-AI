from __future__ import annotations

import unittest

from pathlib import Path

from corpus_research.index import (
    BILARA_PARSER_VERSION,
    PARSER_VERSION,
    SC_RELATIONS_PARSER_VERSION,
    TEI_84000_PARSER_VERSION,
    normalize_cbeta_work_id,
    normalize_taisho_line,
    state_parser_version,
    taisho_line_key,
)
from corpus_research.model import compact, fold_diacritics, normalize, relative, work_from_segment


class NormalizationTests(unittest.TestCase):
    def test_preserves_diacritics_in_primary_normalization(self) -> None:
        self.assertEqual(normalize("  SUTAṂ  "), "sutaṃ")

    def test_explicit_diacritic_fold_is_separate(self) -> None:
        self.assertEqual(fold_diacritics("Sutaṃ"), "sutam")

    def test_compact_unicode_removes_spacing_and_punctuation(self) -> None:
        self.assertEqual(compact("如 是，我 聞"), "如是我聞")

    def test_work_id_from_segment(self) -> None:
        self.assertEqual(work_from_segment("mn1:1.1"), "mn1")

    def test_relative_path_is_lexical_and_repo_relative(self) -> None:
        root = Path("/repo")
        self.assertEqual(relative(root, root / "a/b.txt"), "a/b.txt")

    def test_profile_sensitive_parser_state(self) -> None:
        self.assertEqual(
            state_parser_version("suttacentral-bilara", "core"),
            BILARA_PARSER_VERSION,
        )
        self.assertEqual(
            state_parser_version("suttacentral-bilara", "all"),
            f"{BILARA_PARSER_VERSION}:full",
        )
        self.assertEqual(
            state_parser_version("84000-tei", "acceptance"),
            f"{TEI_84000_PARSER_VERSION}:acceptance",
        )
        self.assertEqual(
            state_parser_version("84000-tei", "core"),
            TEI_84000_PARSER_VERSION,
        )
        self.assertEqual(
            state_parser_version("84000-tei", "all"),
            TEI_84000_PARSER_VERSION,
        )
        self.assertEqual(
            state_parser_version("suttacentral-relations", "core"),
            SC_RELATIONS_PARSER_VERSION,
        )

    def test_cbeta_and_taisho_identifier_normalization(self) -> None:
        self.assertEqual(normalize_cbeta_work_id("T02N0125"), "T02n0125")
        self.assertEqual(normalize_cbeta_work_id("T2n0125"), "T02n0125")
        self.assertEqual(normalize_cbeta_work_id("T02n0150A"), "T02n0150a")
        self.assertEqual(normalize_taisho_line("t563a7"), "0563a07")
        self.assertLess(taisho_line_key("0563a14"), taisho_line_key("0563b01"))


if __name__ == "__main__":
    unittest.main()
