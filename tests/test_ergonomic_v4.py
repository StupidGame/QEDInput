import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))

def main_label(wrapper):
    label = wrapper.get("key", {}).get("design", {}).get("label", {})
    return label.get("main", label.get("text"))

class ErgonomicV4Test(unittest.TestCase):
    def test_kana_positions(self):
        data = load("QED_KANA_4.0.json")
        pos = {main_label(w): (w["specifier"]["x"], w["specifier"]["y"])
               for w in data["interface"]["keys"] if w.get("key_type") == "custom"}
        self.assertEqual(pos["ん"], (0, 2))
        self.assertEqual(pos["ま"], (1, 3))
        self.assertEqual(pos["ABC"], (0, 3))
        self.assertEqual(pos["小゛゜"], (2, 3))

    def test_direction_maps(self):
        data = load("QED_KANA_4.0.json")
        expected = {
            "か": {"left":"き","top":"く","right":"け","bottom":"こ"},
            "し": {"left":"さ","top":"す","right":"せ","bottom":"そ"},
            "と": {"left":"ち","top":"つ","right":"て","bottom":"た"},
            "の": {"left":"に","top":"な","right":"ね","bottom":"、"},
            "は": {"left":"ひ","top":"ふ","right":"へ","bottom":"ほ"},
            "ま": {"left":"み","top":"む","right":"め","bottom":"も"},
            "る": {"left":"り","top":"ら","right":"れ","bottom":"ろ"},
        }
        wrappers = {main_label(w): w for w in data["interface"]["keys"] if w.get("key_type") == "custom"}
        for label, mapping in expected.items():
            got = {}
            for v in wrappers[label]["key"].get("variations", []):
                text = v.get("key", {}).get("design", {}).get("label", {}).get("text")
                got[v["direction"]] = text
            for direction, text in mapping.items():
                self.assertEqual(got[direction], text)

    def test_no_v30_links(self):
        for path in ROOT.glob("QED_*_4.0.json"):
            self.assertNotIn("_v30", path.read_text(encoding="utf-8"))

    def test_bundle_matches_individuals(self):
        bundle = load("00_QED_Input_KANA_DEFAULT_4.0.json")
        names = ("KANA","ABC","ABC_Plus","CAPS","123","UTILITY","MFM")
        self.assertEqual(bundle, [load(f"QED_{name}_4.0.json") for name in names])

if __name__ == "__main__":
    unittest.main()
