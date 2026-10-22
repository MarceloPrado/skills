#!/usr/bin/env python3
"""Print a developer.apple.com documentation or Human Interface Guidelines page as Markdown.

Usage: apple_doc.py <developer.apple.com URL | saved .json>

Those pages are JavaScript apps, so fetching their URL returns no text. Apple serves the same content as JSON under
/tutorials/data/, which this script reads. A HIG page ends with its change log.
"""

import json
import re
import sys
import urllib.parse
import urllib.request

HOST = "developer.apple.com"


def json_url(url):
    parts = urllib.parse.urlsplit(url)
    path = parts.path.rstrip("/").lower()
    if parts.netloc != HOST or not path.startswith(("/design/", "/documentation/")):
        raise ValueError(f"not a documentation or HIG page on {HOST}: {url}")
    return f"https://{HOST}/tutorials/data{path}.json"


def load(source):
    if source.startswith(("https://", "http://")):
        with urllib.request.urlopen(json_url(source), timeout=30) as response:
            return json.load(response)
    with open(source, encoding="utf-8") as handle:
        return json.load(handle)


class Page:
    def __init__(self, data):
        self.refs = data.get("references", {})

    def url(self, ref):
        url = ref.get("url", "")
        return f"https://{HOST}{url}" if url.startswith("/") else url

    def link(self, identifier, title=None):
        ref = self.refs.get(identifier, {})
        title = title or ref.get("title") or identifier
        return f"[{title}]({self.url(ref)})" if ref.get("url") else title

    def inline(self, items):
        out = []
        for item in items or []:
            kind = item.get("type")
            if kind == "text":
                out.append(item["text"])
            elif kind == "codeVoice":
                out.append(f"`{item['code']}`")
            elif kind == "reference":
                out.append(self.link(item.get("identifier", ""), item.get("overridingTitle")))
            elif kind == "link":
                out.append(f"[{item.get('title') or item.get('destination')}]({item.get('destination')})")
            elif kind == "image":
                alt = self.refs.get(item.get("identifier"), {}).get("alt")
                out.append(f"[image: {alt}]" if alt else "[image]")
            else:
                out.append(self.inline(item.get("inlineContent")))
        return "".join(out)

    def text(self, blocks):
        return " ".join(line.strip() for line in self.blocks(blocks) if line.strip())

    def blocks(self, blocks):
        return [line for block in blocks or [] for line in self.block(block)]

    def block(self, block):
        kind = block.get("type")
        if kind == "heading":
            return ["", "#" * block.get("level", 2) + " " + block.get("text", ""), ""]
        if kind in ("paragraph", "small"):
            return [self.inline(block.get("inlineContent")), ""]
        if kind in ("unorderedList", "orderedList"):
            items = block.get("items", [])
            markers = ["- "] * len(items) if kind == "unorderedList" else [f"{n}. " for n in range(1, len(items) + 1)]
            return [marker + self.text(item.get("content")) for marker, item in zip(markers, items)] + [""]
        if kind == "aside":
            label = block.get("name") or block.get("style", "note").title()
            return [f"> **{label}.** {self.text(block.get('content'))}", ""]
        if kind == "codeListing":
            return ["```" + (block.get("syntax") or ""), *block.get("code", []), "```", ""]
        if kind == "table":
            rows = [[self.text(cell) for cell in row] for row in block.get("rows", [])]
            lines = ["| " + " | ".join(row) + " |" for row in rows]
            if block.get("header") == "row" and rows:
                lines.insert(1, "|" + " --- |" * len(rows[0]))
            return lines + [""]
        if kind == "tabNavigator":
            return [line for tab in block.get("tabs", [])
                    for line in [f"**{tab.get('title', '')}**", "", *self.blocks(tab.get("content"))]]
        if kind == "links":
            return [f"- {self.link(identifier)}" for identifier in block.get("items", [])] + [""]
        if kind == "termList":
            return [f"- **{self.inline(item.get('term', {}).get('inlineContent'))}.** "
                    f"{self.text(item.get('definition', {}).get('content'))}" for item in block.get("items", [])] + [""]
        if kind == "row":
            return [line for column in block.get("columns", []) for line in self.blocks(column.get("content"))]
        return self.blocks(block.get("content"))


def render(data):
    page = Page(data)
    lines = [f"# {data.get('metadata', {}).get('title', '')}", "", page.inline(data.get("abstract")), ""]
    for section in data.get("primaryContentSections", []):
        lines += page.blocks(section.get("content"))
    for heading, key in (("Topics", "topicSections"), ("See Also", "seeAlsoSections")):
        sections = data.get(key) or []
        if sections:
            lines += ["", f"## {heading}", ""]
        for section in sections:
            lines += [f"### {section.get('title', '')}", ""]
            lines += [f"- {page.link(identifier)}" for identifier in section.get("identifiers", [])] + [""]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip() + "\n"


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: apple_doc.py <developer.apple.com URL | saved .json>")
    try:
        data = load(sys.argv[1])
    except (ValueError, OSError, json.JSONDecodeError) as error:
        sys.exit(f"apple_doc.py: {error}")
    sys.stdout.write(render(data))


if __name__ == "__main__":
    main()
