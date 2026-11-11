import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import envcheck


class ParseTests(unittest.TestCase):
    def test_basic(self):
        v, p, d = envcheck.parse('A=1\n# c\nexport B="x y"\nC=z # nota\n')
        self.assertEqual(v, {"A": "1", "B": "x y", "C": "z"})
        self.assertEqual((p, d), ([], []))

    def test_problems_and_dups(self):
        v, p, d = envcheck.parse("A=1\nsuelta\n1X=2\nA=3\n")
        self.assertEqual(v["A"], "3")
        self.assertEqual([n for n, _ in p], [2, 3])
        self.assertEqual(d, [("A", 4)])

    def test_mask(self):
        self.assertEqual(envcheck.mask("API_TOKEN", "abc"), "***")
        self.assertEqual(envcheck.mask("PORT", "80"), "80")


class CliTests(unittest.TestCase):
    def write(self, text):
        f = tempfile.NamedTemporaryFile("w", suffix=".env", delete=False, encoding="utf-8")
        f.write(text)
        f.close()
        self.addCleanup(os.remove, f.name)
        return f.name

    def test_check_exit_codes(self):
        tpl = self.write("A=\nB=\n")
        self.assertEqual(envcheck.main(["check", self.write("A=1\nB=2\n"), tpl]), 0)
        self.assertEqual(envcheck.main(["check", self.write("A=1\n"), tpl]), 1)

    def test_diff(self):
        self.assertEqual(envcheck.main(["diff", self.write("A=1\n"), self.write("A=1\n")]), 0)
        self.assertEqual(envcheck.main(["diff", self.write("A=1\n"), self.write("A=2\n")]), 1)


if __name__ == "__main__":
    unittest.main()
