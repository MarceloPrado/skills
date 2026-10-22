"""Fail when a Swift block in a reference file is missing from the compiled harness in tests/snippets."""
import glob
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
BLOCK = re.compile(r"```swift\n(.*?)```", re.S)


def lines(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


harness = []
for path in sorted(glob.glob(os.path.join(ROOT, "tests", "snippets", "*.swift"))):
    with open(path, encoding="utf-8") as handle:
        harness += lines(handle.read())
joined = "\n".join(harness)

missing = 0
for path in sorted(glob.glob(os.path.join(ROOT, "skills", "*", "**", "*.md"), recursive=True)):
    with open(path, encoding="utf-8") as handle:
        for number, block in enumerate(BLOCK.findall(handle.read()), start=1):
            if "\n".join(lines(block)) not in joined:
                missing += 1
                print(f"{os.path.relpath(path, ROOT)}: swift block {number} is not in tests/snippets")
if missing:
    sys.exit(1)
print("every swift block is in the harness")
