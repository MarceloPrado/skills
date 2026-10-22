import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "..", "skills", "iphone-duo", "scripts", "apple_doc.py")
spec = importlib.util.spec_from_file_location("apple_doc", SCRIPT)
apple_doc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(apple_doc)


def text(value):
    return [{"type": "text", "text": value}]


def paragraph(*inline):
    return {"type": "paragraph", "inlineContent": list(inline)}


PAGE = {
    "metadata": {"title": "Designing for a test device"},
    "abstract": text("A page shaped like Apple's render JSON."),
    "primaryContentSections": [{"kind": "content", "content": [
        {"type": "heading", "level": 2, "text": "Best practices"},
        paragraph({"type": "text", "text": "Use an "},
                  {"type": "reference", "identifier": "doc://hig/layout", "isActive": True, "overridingTitle": "adaptable layout"},
                  {"type": "text", "text": " and "},
                  {"type": "codeVoice", "code": "ArrangementView"},
                  {"type": "text", "text": "."}),
        {"type": "tabNavigator", "tabs": [{"title": "Inner display", "content": [paragraph({"type": "image", "identifier": "inner.png"})]}]},
        {"type": "unorderedList", "items": [{"content": [paragraph(*text("Keep the fold clear."))]}]},
        {"type": "aside", "style": "note", "content": [paragraph(*text("Test every pose."))]},
        {"type": "heading", "level": 2, "text": "Change log"},
        {"type": "table", "header": "row", "rows": [[[paragraph(*text("Date"))], [paragraph(*text("Changes"))]],
                                                    [[paragraph(*text("September 9, 2026"))], [paragraph(*text("New page."))]]]},
        {"type": "links", "items": ["doc://videos/1"]},
    ]}],
    "references": {
        "doc://hig/layout": {"type": "topic", "title": "Layout", "url": "/design/human-interface-guidelines/layout"},
        "inner.png": {"type": "image", "alt": "The inner display with its fold."},
        "doc://videos/1": {"type": "link", "title": "Design for a test device", "url": "/videos/play/tech-talks/1"},
    },
}


class AppleDocTest(unittest.TestCase):
    def test_page_urls_map_to_their_json(self):
        self.assertEqual(
            apple_doc.json_url("https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo"),
            "https://developer.apple.com/tutorials/data/design/human-interface-guidelines/designing-for-iphone-duo.json")
        self.assertEqual(
            apple_doc.json_url("https://developer.apple.com/documentation/SwiftUI/ArrangementView/#overview"),
            "https://developer.apple.com/tutorials/data/documentation/swiftui/arrangementview.json")

    def test_other_pages_are_refused(self):
        for url in ("https://example.com/documentation/swiftui", "https://developer.apple.com/videos/play/tech-talks/111466/"):
            with self.assertRaises(ValueError):
                apple_doc.json_url(url)

    def test_render_keeps_what_an_agent_needs(self):
        out = apple_doc.render(PAGE)
        self.assertTrue(out.startswith("# Designing for a test device\n\nA page shaped like Apple's render JSON.\n"))
        for expected in (
            "## Best practices",
            "Use an [adaptable layout](https://developer.apple.com/design/human-interface-guidelines/layout) and `ArrangementView`.",
            "**Inner display**",
            "[image: The inner display with its fold.]",
            "- Keep the fold clear.",
            "> **Note.** Test every pose.",
            "| Date | Changes |\n| --- | --- |\n| September 9, 2026 | New page. |",
            "- [Design for a test device](https://developer.apple.com/videos/play/tech-talks/1)",
        ):
            self.assertIn(expected, out)
        self.assertNotIn("\n\n\n", out)

    def test_cli_reads_a_saved_page(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump(PAGE, handle)
        try:
            result = subprocess.run([sys.executable, SCRIPT, handle.name], capture_output=True, text=True)
        finally:
            os.unlink(handle.name)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, apple_doc.render(PAGE))

    def test_cli_rejects_a_page_it_cant_read(self):
        result = subprocess.run([sys.executable, SCRIPT, "https://example.com/x"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("not a documentation or HIG page", result.stderr)


if __name__ == "__main__":
    unittest.main()
