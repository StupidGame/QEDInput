"""Regression checks for fidelity to the original QED layouts, not an iOS test."""

from collections import deque
from copy import deepcopy
import json
from pathlib import Path
import string
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("KANA", "ABC", "ABC_Plus", "CAPS", "123", "UTILITY")
QUOTE_POSITIONS = {"KANA": {(0, 3), (3, 2)}, "ABC": {(11, 4)},
                   "ABC_Plus": {(11, 4)}, "CAPS": {(11, 4)},
                   "123": {(11, 3)}, "UTILITY": {(1, 3)}}


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def position(wrapper):
    return wrapper["specifier"]["x"], wrapper["specifier"]["y"]


def at(data, x, y):
    return next(k["key"] for k in data["interface"]["keys"] if position(k) == (x, y))


def variations(key):
    return {v["direction"]: v["key"] for v in key.get("variations", [])}


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def normalize_version(data):
    data = deepcopy(data)
    data["metadata"]["display_name"] = data["metadata"]["display_name"].replace(" 2.0", " 3.0")
    data["identifier"] = data["identifier"].replace("_v20", "_v30")
    for value in walk(data):
        if value.get("type") == "move_tab" and value.get("tab_type") == "custom":
            value["identifier"] = value["identifier"].replace("_v20", "_v30")
    return data


def apply(actions, text=""):
    for action in actions:
        if action["type"] == "input":
            text += action["text"]
        elif action["type"] == "replace_last_characters":
            for suffix in sorted(action["table"], key=len, reverse=True):
                if text.endswith(suffix):
                    text = text[:-len(suffix)] + action["table"][suffix]
                    break
        else:
            raise AssertionError(f"Unexpected action in text scenario: {action}")
    return text


class LayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tabs = {name: read(ROOT / f"QED_{name}_3.0.json") for name in NAMES}
        cls.originals = {name: normalize_version(read(ROOT / "archive/2.0" / f"QED_{name}_2.0.json")) for name in NAMES}

    def test_bundle_versions_and_reproducibility(self):
        sys.path.insert(0, str(ROOT / "tools"))
        from build_layouts import build
        bundle = read(ROOT / "00_QED_Input_KANA_DEFAULT_3.0.json")
        self.assertEqual(bundle, list(self.tabs.values()))
        self.assertEqual(build(), bundle)
        self.assertEqual(len({t["identifier"] for t in bundle}), 6)
        for name, tab in self.tabs.items():
            self.assertEqual(tab["metadata"]["display_name"], f"QED {name.replace('_Plus', '+')} 3.0")
            self.assertEqual(tab["metadata"]["custard_version"], "1.2")

    def test_all_original_key_positions_sizes_and_taps_preserved(self):
        for name, data in self.tabs.items():
            original = self.originals[name]
            self.assertEqual(data["input_style"], original["input_style"])
            self.assertEqual(data["language"], original["language"])
            self.assertEqual(data["interface"]["key_layout"], original["interface"]["key_layout"])
            self.assertEqual(data["interface"]["key_style"], original["interface"]["key_style"])
            self.assertEqual(len(data["interface"]["keys"]), len(original["interface"]["keys"]))
            for old, new in zip(original["interface"]["keys"], data["interface"]["keys"]):
                for field in ("specifier", "specifier_type", "key_type"):
                    self.assertEqual(old[field], new[field], (name, position(old), field))
                if old["key_type"] == "system":
                    self.assertEqual(old["key"], new["key"])
                    continue
                self.assertEqual(old["key"]["press_actions"], new["key"]["press_actions"], (name, position(old)))
                old_flicks, new_flicks = variations(old["key"]), variations(new["key"])
                self.assertTrue(old_flicks.keys() <= new_flicks.keys())
                for direction, flick in old_flicks.items():
                    self.assertEqual(flick["press_actions"], new_flicks[direction]["press_actions"], (name, position(old), direction))
                expected = {"top"} if position(old) in QUOTE_POSITIONS[name] else set()
                if name in ("ABC", "ABC_Plus") and position(old) == (11, 3):
                    expected.add("right")
                self.assertEqual(set(new_flicks) - set(old_flicks), expected)

    def test_only_documented_keys_differ_from_original(self):
        # Guard against accidentally reintroducing a broad redesign.
        allowed = {"KANA": {(1, 2), (2, 3)}, "ABC": {(11, 3)},
                   "ABC_Plus": {(11, 3)}, "CAPS": {(11, 3)},
                   "123": {(6, 2), (8, 2), (14, 2)}, "UTILITY": {(0, 1)}}
        for name, data in self.tabs.items():
            for old, new in zip(self.originals[name]["interface"]["keys"], data["interface"]["keys"]):
                if position(old) not in allowed[name] | QUOTE_POSITIONS[name]:
                    self.assertEqual(old, new, (name, position(old)))
                elif position(old) in QUOTE_POSITIONS[name]:
                    old, new = deepcopy(old), deepcopy(new)
                    old["key"].pop("design")
                    new["key"].pop("design")
                    new["key"]["variations"] = [v for v in new["key"]["variations"] if v["direction"] != "top"]
                    self.assertEqual(old, new)
                elif name in ("KANA", "CAPS"):
                    old, new = deepcopy(old), deepcopy(new)
                    old["key"].pop("design")
                    new["key"].pop("design")
                    self.assertEqual(old, new)

    def test_geometry_and_links(self):
        ids = {t["identifier"] for t in self.tabs.values()}
        graph = {}
        for data in self.tabs.values():
            layout = data["interface"]["key_layout"]
            occupied = set()
            for wrapper in data["interface"]["keys"]:
                s = wrapper["specifier"]
                self.assertGreater(s["width"], 0)
                self.assertGreater(s["height"], 0)
                for x in range(s["x"], s["x"]+s["width"]):
                    for y in range(s["y"], s["y"]+s["height"]):
                        self.assertTrue(0 <= x < layout["row_count"] and 0 <= y < layout["column_count"])
                        self.assertNotIn((x, y), occupied)
                        occupied.add((x, y))
                directions = [v["direction"] for v in wrapper["key"].get("variations", [])]
                self.assertEqual(len(directions), len(set(directions)))
            links = {v["identifier"] for v in walk(data) if v.get("type") == "move_tab" and v.get("tab_type") == "custom"}
            self.assertTrue(links <= ids)
            graph[data["identifier"]] = links
        for start in ids:
            seen, pending = {start}, deque([start])
            while pending:
                for destination in graph[pending.popleft()] - seen:
                    seen.add(destination)
                    pending.append(destination)
            self.assertEqual(seen, ids)

    def test_kana_automation_and_original_editing_are_restored(self):
        kana = self.tabs["KANA"]
        yo = at(kana, 1, 2)
        self.assertEqual(apply(yo["press_actions"], "き"), "きょ")
        self.assertEqual(apply(yo["longpress_actions"]["start"], "き"), "きよ")
        self.assertEqual(apply(yo["press_actions"], "に"), "によ")
        self.assertEqual(apply(variations(yo)["top"]["press_actions"], "み"), "みや")
        small = at(kana, 2, 3)
        self.assertEqual(apply(small["press_actions"], "あり"), "ありがとう")
        self.assertEqual(apply(small["press_actions"], "ば"), "ぱ")
        self.assertEqual(apply(variations(small)["bottom"]["press_actions"]), "ぬ")
        self.assertEqual(apply(variations(small)["left"]["press_actions"]), "「")
        self.assertEqual(apply(variations(small)["left"]["press_actions"], "「"), "（")
        for pos in ((3, 0), (3, 1)):
            self.assertEqual(at(kana, *pos), at(self.originals["KANA"], *pos))

    def test_b_shortcuts_and_caps_label(self):
        for name in ("ABC", "ABC_Plus", "CAPS"):
            key = at(self.tabs[name], 11, 3)
            self.assertEqual(variations(key)["left"]["press_actions"], [{"type": "input", "text": "#"}])
            self.assertEqual(variations(key)["left"]["longpress_actions"]["start"], [{"type": "input", "text": "＃"}])
        self.assertEqual(variations(at(self.tabs["ABC"], 11, 3))["right"]["press_actions"], [{"type": "input", "text": "ｂ"}])
        self.assertEqual(variations(at(self.tabs["ABC_Plus"], 11, 3))["right"]["press_actions"], [
            {"type": "input", "text": "Ｂ"},
            {"type": "move_tab", "tab_type": "custom", "identifier": "qed_abc_v30"},
        ])
        self.assertEqual(at(self.tabs["CAPS"], 11, 3)["design"]["label"]["directions"]["left"], "#")

    def test_numeric_row_and_quote_widths(self):
        for name in ("ABC", "ABC_Plus", "CAPS", "123"):
            for index, digit in enumerate("1234567890"):
                self.assertEqual(at(self.tabs[name], index*2, 0)["press_actions"], [{"type": "input", "text": digit}])
        count = 0
        for wrapper in self.tabs["123"]["interface"]["keys"]:
            key = wrapper["key"]
            for part in [key] + list(variations(key).values()):
                actions = part.get("press_actions", [])
                if len(actions) == 1 and actions[0].get("text") in ("'", '"'):
                    expected = {"'": "＇", '"': "＂"}[actions[0]["text"]]
                    self.assertEqual(apply(part["longpress_actions"]["start"]), expected)
                    count += 1
        self.assertEqual(count, 7)

    def test_quotes_are_one_gesture_without_switching_tabs_or_pairing(self):
        for name, positions in QUOTE_POSITIONS.items():
            for pos in positions:
                key = at(self.tabs[name], *pos)
                self.assertIn('↑"', key["design"]["label"]["sub"])
                quote = variations(key)["top"]
                self.assertEqual(quote["press_actions"], [{"type": "input", "text": '"'}])
                self.assertEqual(quote["longpress_actions"]["start"], [{"type": "input", "text": "＂"}])

    def test_utility_brackets_complete_without_changing_existing_shortcuts(self):
        key = at(self.tabs["UTILITY"], 0, 1)
        self.assertEqual(apply(key["press_actions"]), "「")
        self.assertEqual(apply(key["longpress_actions"]["start"]), "〈")
        for direction, pair in {"left": "（）", "top": "【】", "right": "『』", "bottom": "［］"}.items():
            flick = variations(key)[direction]
            self.assertEqual(apply(flick["press_actions"]), pair[0])
            self.assertEqual(apply(flick["longpress_actions"]["start"]), pair[1])
        outputs = {v["text"] for tab in self.tabs.values() for v in walk(tab) if v.get("type") == "input"}
        self.assertTrue(set(string.ascii_letters + string.digits + string.punctuation) <= outputs)


if __name__ == "__main__":
    unittest.main()
