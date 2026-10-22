#!/usr/bin/env python3
"""Scan an iOS project for code that keeps it from adapting to iPhone Duo.

Usage: duo_scan.py <source-root> [--json] [--strict] [--include-tests]

Each finding names a rule in references/rules.md. Severities:
  blocker  breaks layout on resize
  warn     likely wrong on one display or pose, check it
  note     fine on its own, verify it in the pose matrix

It reads lines, not Swift syntax. It skips comments and the inside of string literals, but it misses
code split across lines and can't tell which target a build setting belongs to. Treat it as a lead list.
"""

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass

SKIP_DIRS = {"build", "DerivedData", "Pods", "Carthage", "SourcePackages", "node_modules", "vendor"}
CODE_EXTENSIONS = {".swift", ".m", ".mm", ".h"}
IPHONE_SIZES = "568|667|736|812|844|852|874|896|926|932|956|320|375|390|393|402|414|428|430|440"
LAUNCH_SCREEN = re.compile(
    r"UILaunchScreen\b|UILaunchScreens\b|UILaunchStoryboardName\b|UILaunchStoryboards\b"
    r"|INFOPLIST_KEY_UILaunchScreen_Generation\s*[=:]\s*(?:YES|true)\b"
)
SEVERITY_ORDER = {"blocker": 0, "warn": 1, "note": 2}


@dataclass(frozen=True)
class Rule:
    id: str
    severity: str
    pattern: re.Pattern
    fix: str
    # Rules about symbol names look inside string literals; the rest see them blanked out.
    reads_strings: bool = False


CODE_RULES = [
    Rule("L1", "blocker", re.compile(r"UIScreen\.main\b|UIScreen\s+mainScreen\]|UIScreen\.mainScreen"),
         "Size from the view (view.bounds, onGeometryChange). Scale from traitCollection.displayScale."),
    Rule("L1", "blocker", re.compile(r"UIWindow\(\s*frame:"),
         "Create the window with UIWindow(windowScene:)."),
    Rule("L2", "warn", re.compile(r"\buserInterfaceIdiom\b|UI_USER_INTERFACE_IDIOM"),
         "Pick the layout by size class or available width. Regular width now includes iPhone."),
    Rule("L2", "blocker", re.compile(
        r"UIDevice\.current\.orientation|currentDevice\]\s*\.orientation|currentDevice\]\s+orientation\]"
        r"|\binterfaceOrientation\b|statusBarOrientation"),
         "Compare the width and height of the space you have instead of the orientation."),
    Rule("L2", "blocker", re.compile(
        r"\b(?:bounds|frame|size|nativeBounds)\.(?:height|width)\s*(?:==|>=|<=|>|<)\s*(?:" + IPHONE_SIZES + r")\b"),
         "Remove checks for known iPhone sizes."),
    Rule("L2", "warn", re.compile(r"\b(?:let|var|func|case)\s+(?:is_?[iI]?[pP]ad|iPadLayout)\b"),
         "Name and branch on the size class or the width, not the device."),
    Rule("L3", "blocker", re.compile(
        r"safeAreaInsets\.(?:left|right|top|bottom)\s*\*\s*2\b|\b2\s*\*\s*[\w.]*safeAreaInsets\.(?:left|right|top|bottom)"),
         "Inset each edge on its own: bounds.inset(by: safeAreaInsets)."),
    Rule("L3", "blocker", re.compile(r"\b(?:top|bottom)LayoutGuide\b"),
         "Use safeAreaLayoutGuide."),
    Rule("L3", "warn", re.compile(r"statusBarFrame"),
         "Read the safe area instead of the status bar frame."),
    Rule("B1", "warn", re.compile(
        r"\bUI(?:Toolbar|TabBar|NavigationBar)\(\s*(?:frame:[^)]*)?\)|\[\[UI(?:Toolbar|TabBar|NavigationBar)\s+alloc\]"),
         "A standalone bar stays put. Unless it is a keyboard accessory, move its items to a view controller in "
         "UINavigationController or UITabBarController."),
    Rule("B1", "warn", re.compile(
        r"\.toolbar\(\s*\.hidden\s*,\s*for:\s*\.(?:tabBar|navigationBar|bottomBar)"
        r"|\.toolbarVisibility\(\s*\.hidden\s*,\s*for:\s*\.(?:tabBar|navigationBar|bottomBar)"),
         "Hidden system bars usually mean custom chrome, which stays put. Move its actions into .toolbar."),
    Rule("B1", "note", re.compile(r"\.safeAreaInset\(\s*edge:\s*\.bottom"),
         "Controls in a bottom inset stay at the bottom instead of joining the strip, and cross the fold at full width."),
    Rule("B7", "warn", re.compile(r"(?:systemName|systemImage):\s*\"ellipsis"),
         "Move these actions into ToolbarOverflowMenu or additionalOverflowItems. The ellipsis means system overflow.",
         reads_strings=True),
    Rule("B9", "note", re.compile(r"toolbarVerticalBehavior\(\s*\.disabled|preferredVerticalBarBehavior"),
         "Keep the opt-out for bottom-heavy single screens and one-button sheets."),
    Rule("A3", "warn", re.compile(r"requestGeometryUpdate\(.*interfaceOrientations"),
         "An orientation lock must still fill every display and pose."),
    Rule("A3", "note", re.compile(r"\bsupportedInterfaceOrientations\b"),
         "An orientation lock must still fill every display and pose."),
    Rule("L6", "note", re.compile(r"repeating:\s*GridItem\(|GridItem\(\s*\.fixed"),
         "Count columns from the width, and prefer an even count when open."),
    Rule("L7", "note", re.compile(r"aspectRatio\(\s*contentMode:\s*\.fill|\.scaledToFill\(\)|scaleAspectFill|resizeAspectFill"),
         "Check the subject is still in frame at 1.4:1. Pick fill or fit by aspect ratio."),
    Rule("L8", "warn", re.compile(r"\.frame\(\s*width:\s*(?:[3-9]\d\d|\d{4,})(?:\.\d+)?\s*[,)]"),
         "A fixed width this large fits one display only. Use a flexible frame or containerRelativeFrame."),
    Rule("L8", "warn", re.compile(r"\.frame\((?:[^()]*,)?\s*height:\s*(?:[5-9]\d\d|\d{4,})(?:\.\d+)?\s*[,)]"),
         "A fixed height this large fits one display only. Size from the space you get."),
    Rule("F2", "note", re.compile(r"\.ignoresSafeArea\(\s*\)"),
         "Keep tappable views out from under the strip and the camera."),
]

TOOLBAR_OPEN = re.compile(r"\.toolbar\s*\{")
# Menu items and keyboard accessories never go in the strip, so their title-only buttons are fine.
EXEMPT_OPEN = re.compile(r"\bMenu\b[^{]*\{|placement:\s*\.keyboard[^{]*\{")
TITLE_ONLY_BUTTON = re.compile(r"\bButton\(\s*\"[^\"]*\"\s*(?:\)|,\s*action:|,\s*role:[^,)]*\))(?![^\n]*systemImage)")
UIKIT_TITLE_ITEM = re.compile(r"UIBarButtonItem\(\s*title:")


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    path: str
    line: int
    code: str
    fix: str


def without_comments(text):
    """Each line with its comments removed, string literals kept."""
    out, in_block = [], False
    for raw in text.splitlines():
        line, kept, i, in_string = raw, [], 0, False
        while i < len(line):
            if in_block:
                end = line.find("*/", i)
                if end < 0:
                    i = len(line)
                    break
                in_block, i = False, end + 2
                continue
            ch = line[i]
            if ch == '"' and (i == 0 or line[i - 1] != "\\"):
                in_string = not in_string
            elif not in_string and line.startswith("//", i):
                break
            elif not in_string and line.startswith("/*", i):
                in_block, i = True, i + 2
                continue
            kept.append(ch)
            i += 1
        out.append("".join(kept))
    return out


def blank_strings(line):
    """The line with the inside of each string literal replaced by spaces, so code in strings doesn't match."""
    return re.sub(r'"(?:\\.|[^"\\])*"', lambda m: '"' + " " * (len(m.group(0)) - 2) + '"', line)


def block_ranges(lines, opener):
    """1-based (first, last) line ranges of brace blocks whose first line matches `opener`."""
    ranges = []
    for index, line in enumerate(lines):
        match = opener.search(line)
        if not match:
            continue
        depth, started = 0, False
        for offset, following in enumerate(lines[index:]):
            segment = following[match.end() - 1:] if offset == 0 else following
            depth += segment.count("{") - segment.count("}")
            started = started or "{" in segment
            if started and depth <= 0:
                ranges.append((index + 1, index + offset + 1))
                break
    return ranges


def within(ranges, number):
    return any(first <= number <= last for first, last in ranges)


def statement(lines, index, limit=6):
    """The expression that opens at `index`, joined until its parentheses close."""
    joined, depth = "", 0
    for line in lines[index:index + limit]:
        joined += " " + line
        depth += line.count("(") - line.count(")")
        if depth <= 0:
            break
    return joined


def scan_code(path, rel):
    with open(path, encoding="utf-8", errors="replace") as handle:
        lines = without_comments(handle.read())
    findings = []
    for number, line in enumerate(lines, start=1):
        blanked = blank_strings(line)
        for rule in CODE_RULES:
            if rule.pattern.search(line if rule.reads_strings else blanked):
                findings.append(Finding(rule.id, rule.severity, rel, number, line.strip(), rule.fix))
        if UIKIT_TITLE_ITEM.search(blanked) and "image:" not in blank_strings(statement(lines, number - 1)):
            findings.append(Finding("B3", "warn", rel, number, line.strip(), "Give the item an image too, so it can go vertical."))
    if path.endswith(".swift"):
        exempt = block_ranges(lines, EXEMPT_OPEN)
        for first, last in block_ranges(lines, TOOLBAR_OPEN):
            for number in range(first, last + 1):
                if not within(exempt, number) and TITLE_ONLY_BUTTON.search(lines[number - 1]):
                    findings.append(Finding("B3", "warn", rel, number, lines[number - 1].strip(),
                                            "Give the item a symbol: Button(_:systemImage:action:) or a Label."))
    return findings


def portrait_only(values):
    has_portrait = any("Portrait" in v for v in values)
    has_landscape = any("Landscape" in v for v in values)
    return has_portrait and not has_landscape


def scan_config(path, rel, text):
    findings = []
    lines = text.splitlines()

    def add(rule, severity, number, fix):
        findings.append(Finding(rule, severity, rel, number, lines[number - 1].strip()[:120], fix))

    for number, line in enumerate(lines, start=1):
        if re.search(r"UIRequiresFullScreen(?!Ignored)", line):
            window = " ".join(lines[number - 1:number + 1])
            if re.search(r"<true\s*/>|:\s*(?:true|YES)\b|=\s*YES\b", window):
                add("A2", "warn", number, "The scene still resizes, discretely. Remove the key once every screen resizes cleanly.")
        if re.search(r"UISupportedInterfaceOrientations(?:_iPhone)?\b(?!~ipad)", line) and "~ipad" not in line:
            if path.endswith(".plist"):
                block = []
                for following in lines[number:number + 8]:
                    if "</array>" in following:
                        break
                    block.append(following)
            elif "=" in line:
                block = [line.split("=", 1)[1]]
            else:
                block = [line.split(":", 1)[1].split("#", 1)[0]] if ":" in line else []
                if not block or not block[0].strip():
                    block = []
                    for following in lines[number:number + 6]:
                        if not following.strip().startswith("-"):
                            break
                        block.append(following)
            if portrait_only(block):
                add("A3", "warn", number,
                    "Portrait-only on iPhone. The open inner display still shows a landscape UI, so the layout must fit it.")
    return findings


def is_config(name):
    return name.endswith("Info.plist") or name in ("project.yml", "project.pbxproj", "Project.swift") \
        or name.endswith(".xcconfig")


def scan(root, include_tests=False):
    findings, launch_screen, saw_app_config, files = [], False, False, 0
    for directory, subdirs, names in os.walk(root):
        subdirs[:] = sorted(
            d for d in subdirs
            if not d.startswith(".") and d not in SKIP_DIRS
            and not d.endswith((".xcassets", ".xcframework"))
            and (include_tests or not d.endswith(("Tests", "UITests")))
        )
        for name in sorted(names):
            path = os.path.join(directory, name)
            rel = os.path.relpath(path, root)
            if os.path.splitext(name)[1] in CODE_EXTENSIONS:
                files += 1
                findings.extend(scan_code(path, rel))
            elif is_config(name):
                files += 1
                with open(path, encoding="utf-8", errors="replace") as handle:
                    text = handle.read()
                if name != "Project.swift":
                    saw_app_config = saw_app_config or "CFBundle" in text or "PRODUCT_BUNDLE_IDENTIFIER" in text \
                        or "bundleIdPrefix" in text or "INFOPLIST" in text
                launch_screen = launch_screen or bool(LAUNCH_SCREEN.search(text))
                findings.extend(scan_config(path, rel, text))
    if saw_app_config and not launch_screen:
        findings.append(Finding("A4", "blocker", ".", 0, "no launch screen key found",
                                "Add UILaunchScreen. iOS 27 rejects uploads without one (ITMS-90870)."))
    findings.sort(key=lambda f: (SEVERITY_ORDER[f.severity], f.rule, f.path, f.line))
    return findings, files


def cell(text):
    return text.replace("|", "\\|").replace("\n", " ")


def report(root, findings, files):
    counts = {s: sum(f.severity == s for f in findings) for s in SEVERITY_ORDER}
    out = [f"# iPhone Duo scan of {root}", "",
           f"{counts['blocker']} blockers, {counts['warn']} warnings, {counts['note']} notes in {files} files.", ""]
    titles = {"blocker": "Blockers", "warn": "Warnings", "note": "Notes"}
    for severity in SEVERITY_ORDER:
        rows = [f for f in findings if f.severity == severity]
        if not rows:
            continue
        out += [f"## {titles[severity]}", "", "| Rule | Where | Code | Fix |", "| --- | --- | --- | --- |"]
        for f in rows:
            code = f.code if len(f.code) <= 90 else f.code[:87] + "..."
            out.append(f"| {f.rule} | `{f.path}:{f.line}` | `{cell(code)}` | {cell(f.fix)} |")
        out.append("")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("root")
    parser.add_argument("--json", action="store_true", help="print findings as JSON")
    parser.add_argument("--strict", action="store_true", help="exit 1 when any blocker remains")
    parser.add_argument("--include-tests", action="store_true", help="also scan *Tests directories")
    args = parser.parse_args()
    if not os.path.isdir(args.root):
        parser.error(f"not a directory: {args.root}")
    findings, files = scan(args.root, args.include_tests)
    if args.json:
        print(json.dumps([asdict(f) for f in findings], indent=2))
    else:
        print(report(args.root, findings, files))
    if args.strict and any(f.severity == "blocker" for f in findings):
        sys.exit(1)


if __name__ == "__main__":
    main()
