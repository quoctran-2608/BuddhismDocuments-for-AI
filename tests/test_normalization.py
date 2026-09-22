from __future__ import annotations

import unittest

from pathlib import Path

from corpus_research.index import PARSER_VERSION, state_parser_version
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
        self.assertEqual(state_parser_version("suttacentral-bilara", "core"), PARSER_VERSION)
        self.assertEqual(
            state_parser_version("suttacentral-bilara", "all"),
            f"{PARSER_VERSION}:full",
        )
        self.assertEqual(
            state_parser_version("84000-tei", "acceptance"),
            f"{PARSER_VERSION}:acceptance",
        )
        self.assertEqual(state_parser_version("84000-tei", "all"), PARSER_VERSION)


if __name__ == "__main__":
    unittest.main()
