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

    def test_high_frequency_kana_are_in_middle_row(self):
        data = load("QED_KANA_4.0.json")
        keys = data["interface"]["keys"]
        positions = {main_label(w): (w["specifier"]["x"], w["specifier"]["y"])
                     for w in keys if w.get("key_type") == "custom"}
        self.assertEqual(positions["い"], (0, 1))
        self.assertEqual(positions["し"], (2, 1))
        self.assertEqual(positions["と"], (0, 0))
        self.assertEqual(positions["は"], (2, 0))
        self.assertEqual(positions["の"], (1, 1))
        self.assertEqual(positions["よ"], (1, 2))
        # All legacy long-press shortcuts and contracted-syllable rules survive.
        ma = next(w["key"] for w in keys if main_label(w) == "ま")
        self.assertEqual(ma["longpress_actions"]["start"], [{"type": "input", "text": "ます"}])
        yo = next(w["key"] for w in keys if main_label(w) == "よ")
        self.assertEqual(yo["press_actions"][0], {"type": "input", "text": "よ"})
        self.assertEqual(yo["press_actions"][1]["table"]["しよ"], "しょ")

    def test_kana_exclamation_shortcut(self):
        data = load("QED_KANA_4.0.json")
        number_key = next(w["key"] for w in data["interface"]["keys"] if main_label(w) == "123")
        flicks = {v["direction"]: v["key"] for v in number_key["variations"]}
        self.assertEqual(flicks["left"]["press_actions"], [{"type": "input", "text": "！"}])
        self.assertEqual(flicks["left"]["longpress_actions"]["start"], [{"type": "input", "text": "!"}])
        self.assertEqual(flicks["top"]["press_actions"], [{"type": "input", "text": '"'}])
        self.assertIn("←！", number_key["design"]["label"]["sub"])

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

    def test_english_at_shortcut_near_thumb(self):
        # English v4 uses the same one-flick @ shortcut in all letter modes.
        for name in ("ABC", "ABC_Plus", "CAPS"):
            with self.subTest(name=name):
                data = load(f"QED_{name}_4.0.json")
                keys = data["interface"]["keys"]
                one = next(w["key"] for w in keys if w["specifier"]["x"] == 0 and w["specifier"]["y"] == 0)
                n = next(w["key"] for w in keys if w["specifier"]["x"] == 13 and w["specifier"]["y"] == 3)
                one_flicks = {v["direction"]: v["key"] for v in one["variations"]}
                n_flicks = {v["direction"]: v["key"] for v in n["variations"]}
                self.assertNotIn("left", one_flicks)
                self.assertEqual(n_flicks["bottom"]["press_actions"], [{"type": "input", "text": "@"}])
                self.assertEqual(n_flicks["bottom"]["longpress_actions"]["start"], [{"type": "input", "text": "＠"}])
                self.assertEqual(n["design"]["label"]["directions"]["bottom"], "@")
                self.assertEqual(sum(
                    action.get("text") == "@"
                    for wrapper in keys
                    for key in [wrapper["key"]] + [v["key"] for v in wrapper["key"].get("variations", [])]
                    for action in key.get("press_actions", [])
                ), 1)

    def test_bundle_matches_individuals(self):
        bundle = load("00_QED_Input_KANA_DEFAULT_4.0.json")
        names = ("KANA","ABC","ABC_Plus","CAPS","123","UTILITY","MFM")
        self.assertEqual(bundle, [load(f"QED_{name}_4.0.json") for name in names])

if __name__ == "__main__":
    unittest.main()
