#!/usr/bin/env bash
# Runs every check: the scanner's fixtures, the docs against the harness, and the harness against the iOS 27.1 SDK.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m unittest discover -s tests -p 'test_*.py'
python3 tests/check_snippets.py
xcrun -sdk iphonesimulator swiftc -typecheck -target arm64-apple-ios27.1-simulator tests/snippets/*.swift
echo "snippets type-check against $(xcrun -sdk iphonesimulator --show-sdk-version)"
