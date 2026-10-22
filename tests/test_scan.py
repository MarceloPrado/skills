import json
import os
import re
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCANNER = os.path.join(HERE, "..", "skills", "iphone-duo", "scripts", "duo_scan.py")
MARKER = re.compile(r"expect:\s*([A-Z]\d+(?:\s*,\s*[A-Z]\d+)*)")


def scan(root, *flags):
    return subprocess.run([sys.executable, SCANNER, root, *flags], capture_output=True, text=True)


def findings(root):
    result = scan(root, "--json")
    result.check_returncode()
    return json.loads(result.stdout)


def expected(root):
    marks = set()
    for directory, _, names in os.walk(root):
        for name in names:
            path = os.path.join(directory, name)
            with open(path, encoding="utf-8") as handle:
                for number, line in enumerate(handle, start=1):
                    match = MARKER.search(line)
                    if match:
                        for rule in match.group(1).split(","):
                            marks.add((os.path.relpath(path, root), number, rule.strip()))
    return marks


class ScanTests(unittest.TestCase):
    def test_finds_exactly_the_marked_lines(self):
        root = os.path.join(HERE, "fixtures", "App")
        got = {(f["path"], f["line"], f["rule"]) for f in findings(root)}
        self.assertEqual(got, expected(root))

    def test_reports_a_missing_launch_screen(self):
        root = os.path.join(HERE, "fixtures", "NoLaunch")
        self.assertEqual([(f["rule"], f["severity"]) for f in findings(root)], [("A4", "blocker")])

    def test_reads_any_info_plist_and_skips_hidden_folders(self):
        root = os.path.join(HERE, "fixtures", "Plist")
        got = {(f["path"], f["line"], f["rule"]) for f in findings(root)}
        self.assertEqual(got, expected(root))

    def test_a_generated_launch_screen_set_to_no_is_missing(self):
        root = os.path.join(HERE, "fixtures", "GenerationNo")
        self.assertEqual([(f["rule"], f["severity"]) for f in findings(root)], [("A4", "blocker")])

    def test_strict_fails_on_blockers_only(self):
        self.assertEqual(scan(os.path.join(HERE, "fixtures", "App"), "--strict").returncode, 1)
        self.assertEqual(scan(os.path.join(HERE, "fixtures", "App", "Sources"), "--strict").returncode, 1)

    def test_markdown_report_counts(self):
        out = scan(os.path.join(HERE, "fixtures", "App")).stdout
        self.assertRegex(out, r"\d+ blockers, \d+ warnings, \d+ notes in 6 files\.")


if __name__ == "__main__":
    unittest.main()
