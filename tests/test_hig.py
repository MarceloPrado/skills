import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REFERENCES = os.path.join(HERE, "..", "skills", "iphone-duo", "references")
RULE = re.compile(r"^\*\*([A-Z]\d+)\. ", re.M)
MAPPED = re.compile(r"\(([A-Z]\d+(?:, [A-Z]\d+)*)\)$", re.M)


def read(name):
    with open(os.path.join(REFERENCES, name), encoding="utf-8") as handle:
        return handle.read()


def rules_citing_hig(rules):
    cited = set()
    for chunk in re.split(r"(?m)^(?=\*\*[A-Z]\d+\. )", rules):
        match = RULE.match(chunk)
        if match and "[HIG][hig]" in chunk.split("\n\n")[0]:
            cited.add(match.group(1))
    return cited


class HigDigestTest(unittest.TestCase):
    def test_digest_and_rules_cite_each_other(self):
        rules = read("rules.md")
        mapped = {rule for group in MAPPED.findall(read("hig.md")) for rule in group.split(", ")}
        cited = rules_citing_hig(rules)
        self.assertEqual(mapped - set(RULE.findall(rules)), set(), "hig.md names rules that don't exist")
        self.assertEqual(cited - mapped, set(), "these rules cite the HIG, but no point in hig.md leads to them")
        self.assertEqual(mapped - cited, set(), "hig.md leads to these rules, but they don't cite the HIG")


if __name__ == "__main__":
    unittest.main()
