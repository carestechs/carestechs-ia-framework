"""The verdict contract (orchestrator-integration.md section 2) as read by both tools.

v2.8.6 moved verdict reading to the '## Verdict' section after a re-review's opening
sentence ("This file overwrites the previous (verdict `revise`) review") was read as the
verdict. next-step.py and metrics-report.py each carry a copy of the parser; the two must
agree on every shape here and on every committed review artifact.
"""

import unittest

from helpers import BASELINES_DIR, CASES_DIR, FrameworkTestCase, load_tool

ns = load_tool("next-step")
mr = load_tool("metrics-report")

SHAPES = [
    ("heading tail", "# Review\n\n## Verdict: approve\n", "approve"),
    ("section body", "# Review\n\n## Verdict\n\napprove\n", "approve"),
    ("bold heading", "## **Verdict:** revise\n", "revise"),
    ("deeper heading level", "### Verdict\n\nrevise\n", "revise"),
    ("re-review trap sentence",
     "# Re-review\n\nThis file overwrites the previous (verdict `revise`) review.\n\n"
     "## Verdict\n\napprove\n", "approve"),
    ("inline declaration without a section", "# Review\n\n**Verdict:** revise\n\nbecause.\n",
     "revise"),
    ("quoted prior verdict before the section",
     "> Previous round verdict: revise\n\n## Verdict\n\napprove\n", "approve"),
    ("quoted line inside the section is skipped",
     "## Verdict\n\n> earlier round said revise\n\napprove\n", "approve"),
    ("fenced example only", "```\n## Verdict\n\napprove\n```\n", None),
    ("prose mention only", "The author hopes you will approve of this plan.\n", None),
    ("cannot approve reads as revise",
     "## Verdict\n\nI cannot approve this as written - revise.\n", "revise"),
    ("not approve reads as revise", "## Verdict\n\nnot approve; revise\n", "revise"),
    ("verdict summary heading does not claim the section",
     "## Verdict summary\n\nStrong overall; I would approve most of it.\n\n"
     "## Verdict\n\nrevise\n", "revise"),
    ("empty section falls through to a declaration",
     "## Verdict\n\nSee the closing line.\n\n## Notes\n\n**Verdict:** approve\n", "approve"),
    ("approve with advisories stays approve",
     "## Verdict\n\napprove\n\n## Advisories\n\n- consider a revise of the naming later\n",
     "approve"),
    ("empty file", "", None),
    ("section ends at the next heading",
     "## Verdict\n\nPending.\n\n## Findings\n\nrevise everything\n", None),
]


class VerdictShapes(FrameworkTestCase):
    def test_every_shape_parses_as_specified_in_both_tools(self):
        for i, (label, text, expected) in enumerate(SHAPES):
            path = self.p.write(f"review-{i}.md", text)
            with self.subTest(label):
                self.assertEqual(ns.parse_verdict(path), expected)
                self.assertEqual(mr.read_verdict(path), expected)

    def test_published_regex_still_matches_the_documented_forms(self):
        """VERDICT_RE is the cross-tool contract drivers match; it must not change."""
        for text in ("## Verdict: approve", "**Verdict:** revise", "Verdict - approve"):
            self.assertIsNotNone(ns.VERDICT_RE.search(text), text)
        self.assertEqual(ns.VERDICT_RE.pattern, r"verdict[^a-z]*(approve|revise)")


class CommittedReviewCorpus(unittest.TestCase):
    """Both parsers agree on every review artifact the repo ships or archived."""

    def review_files(self):
        files = sorted(CASES_DIR.glob("*/*/reference/review.md"))
        for case in ("case-003-review-flawed-tasks", "case-010-review-t002-impl"):
            files += sorted(BASELINES_DIR.glob(f"*/{case}/sample-*.md"))
        return files

    def test_corpus_is_present(self):
        self.assertGreaterEqual(len(self.review_files()), 8)

    def test_parsers_agree_on_every_committed_review(self):
        for path in self.review_files():
            with self.subTest(path.relative_to(CASES_DIR.parent).as_posix()):
                self.assertEqual(ns.parse_verdict(path), mr.read_verdict(path))

    def test_reference_reviews_reach_the_planted_verdict(self):
        """Both review cases plant defects that must force a revise."""
        for path in sorted(CASES_DIR.glob("*/*/reference/review.md")):
            with self.subTest(path.parent.parent.name):
                self.assertEqual(ns.parse_verdict(path), "revise")


if __name__ == "__main__":
    unittest.main()
