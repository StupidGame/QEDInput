"""Validate exported Custards, navigation, and important editing/input behavior.

These tests model Custard actions; they do not run the iOS keyboard/IME.
Run: python -m unittest discover -s tests -v
"""

from collections import deque
from copy import deepcopy
import json
from pathlib import Path
import string
import unittest

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("KANA", "ABC", "ABC_Plus", "CAPS", "123", "UTILITY")


def read(name):
    return json.loads((ROOT / f"QED_{name}_3.0.json").read_text(encoding="utf-8"))


def keys(data):
    return [k["key"] for k in data["interface"]["keys"] if k["key_type"] == "custom"]


def gestures(key):
    yield "tap", key["press_actions"]
    if key["longpress_actions"]["start"]:
        yield "hold", key["longpress_actions"]["start"]
    for variation in key["variations"]:
        direction, value = variation["direction"], variation["key"]
        yield direction, value["press_actions"]
        if value["longpress_actions"]["start"]:
            yield direction + " hold", value["longpress_actions"]["start"]


def nested_actions(data):
    if isinstance(data, dict):
        if "type" in data:
            yield data
        for value in data.values():
            yield from nested_actions(value)
    elif isinstance(data, list):
        for value in data:
            yield from nested_actions(value)


def key_with_tap(data, text):
    return next(k for k in keys(data) if k["press_actions"][0] == {"type": "input", "text": text})


def variation(key, direction):
    return next(v["key"] for v in key["variations"] if v["direction"] == direction)


def run_actions(actions, text="", cursor=None, current_tab=""):
    """Small, independent action model for regression scenarios below."""
    cursor = len(text) if cursor is None else cursor
    for a in actions:
        kind = a["type"]
        if kind == "input":
            text = text[:cursor] + a["text"] + text[cursor:]
            cursor += len(a["text"])
        elif kind == "replace_last_characters":
            for suffix in sorted(a["table"], key=len, reverse=True):
                if text[:cursor].endswith(suffix):
                    replacement = a["table"][suffix]
                    text = text[:cursor-len(suffix)] + replacement + text[cursor:]
                    cursor += len(replacement)-len(suffix)
                    break
        elif kind == "delete":
            n = a["count"]
            if n > 0:
                start = max(0, cursor-n)
                text, cursor = text[:start] + text[cursor:], start
            else:
                text = text[:cursor] + text[cursor-n:]
        elif kind == "smart_delete":
            if a["direction"] != "backward":
                raise AssertionError("Only backward deletion is used in QED 3.0")
            start = cursor
            while start and text[start-1] not in a["targets"]:
                start -= 1
            text, cursor = text[:start] + text[cursor:], start
        elif kind == "move_cursor":
            cursor = max(0, min(len(text), cursor + a["count"]))
        elif kind == "move_tab":
            current_tab = a["identifier"]
        elif kind == "dismiss_keyboard":
            pass
        else:
            raise AssertionError(f"Action requires the real IME: {kind}")
    return text, cursor, current_tab


class LayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tabs = {name: read(name) for name in NAMES}

    def test_bundle_and_generator_match_individual_exports(self):
        import sys
        sys.path.insert(0, str(ROOT / "tools"))
        from build_layouts import build
        bundle = json.loads((ROOT / "00_QED_Input_KANA_DEFAULT_3.0.json").read_text(encoding="utf-8"))
        self.assertEqual(bundle, list(self.tabs.values()))
        self.assertEqual(build(), bundle)
        self.assertEqual(len({t["identifier"] for t in bundle}), 6)
        for name, t in self.tabs.items():
            self.assertEqual(t["metadata"]["display_name"], f"QED {name.replace('_Plus', '+')} 3.0")
            self.assertEqual(t["metadata"]["custard_version"], "1.2")

    def test_key_geometry_and_required_fields(self):
        for name, data in self.tabs.items():
            layout = data["interface"]["key_layout"]
            # Custard names horizontal count row_count, vertical column_count.
            width, height = layout["row_count"], layout["column_count"]
            occupied = set()
            for wrapper in data["interface"]["keys"]:
                self.assertEqual(wrapper["specifier_type"], "grid_fit")
                s = wrapper["specifier"]
                self.assertGreater(s["width"], 0)
                self.assertGreater(s["height"], 0)
                for x in range(s["x"], s["x"]+s["width"]):
                    for y in range(s["y"], s["y"]+s["height"]):
                        self.assertTrue(0 <= x < width and 0 <= y < height, (name, s))
                        self.assertNotIn((x, y), occupied, name)
                        occupied.add((x, y))
                if wrapper["key_type"] == "system":
                    self.assertEqual(wrapper["key"], {"type": "enter"})
            if name in ("KANA", "123", "UTILITY"):
                self.assertEqual(len(occupied), width*height, name)
            for key in keys(data):
                self.assertTrue(key["press_actions"])
                self.assertIn(key["design"]["color"], ("normal", "special", "selected", "unimportant"))
                directions = [v["direction"] for v in key["variations"]]
                self.assertEqual(len(directions), len(set(directions)))
                self.assertTrue(set(directions) <= {"left", "top", "right", "bottom"})
                for part in [key] + [v["key"] for v in key["variations"]]:
                    self.assertIn(part["longpress_actions"]["duration"], ("normal", "light"))
                    self.assertIsInstance(part["longpress_actions"]["start"], list)
                    self.assertIsInstance(part["longpress_actions"]["repeat"], list)

    def test_all_custom_tabs_are_reachable_and_close_returns_to_kana(self):
        ids = {data["identifier"] for data in self.tabs.values()}
        graph = {}
        for data in self.tabs.values():
            links = {a["identifier"] for a in nested_actions(data)
                     if a.get("type") == "move_tab" and a.get("tab_type") == "custom"}
            self.assertTrue(links <= ids)
            graph[data["identifier"]] = links
            for key in keys(data):
                for _, actions in gestures(key):
                    if any(a["type"] == "dismiss_keyboard" for a in actions):
                        self.assertEqual(actions[-2]["identifier"], "qed_kana_v30")
        for start in ids:
            seen, pending = {start}, deque([start])
            while pending:
                for target in graph[pending.popleft()] - seen:
                    seen.add(target)
                    pending.append(target)
            self.assertEqual(seen, ids)

    def test_kana_coverage_literal_words_and_explicit_small_kana(self):
        data = self.tabs["KANA"]
        all_inputs, plain = {}, {}
        for key in keys(data):
            for gesture, actions in gestures(key):
                if actions[0]["type"] == "input":
                    char = actions[0]["text"]
                    all_inputs[char] = actions
                    if "hold" not in gesture:
                        plain[char] = actions
        basic = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"
        self.assertTrue(set(basic) <= plain.keys())
        self.assertTrue(set("がぎぐげござじずぜぞだぢづでどばびぶべぼゔぁぃぇぉゃゅょっゎ") <= all_inputs.keys())
        for word in ["しよう", "ひよう", "きよう", "にやける", "による", "みやすい", "しやすい", "りよう", "ぬの", "こころ", "ーー", "「「"]:
            text = ""
            for char in word:
                text, _, _ = run_actions(plain[char], text)
            self.assertEqual(text, word)
        for word in ["きょう", "しゅっせき", "ちょっと", "ゔ"]:
            text = ""
            for char in word:
                text, _, _ = run_actions(all_inputs[char], text)
            self.assertEqual(text, word)
        modifier = next(k for k in keys(data) if k["press_actions"][0]["type"] == "replace_default")
        self.assertEqual(variation(modifier, "bottom")["press_actions"],
                         [{"type": "replace_default", "replace_type": "handakuten", "fallbacks": []}])

    def test_english_letters_widths_caps_and_one_shot(self):
        for name in ("ABC", "ABC_Plus", "CAPS"):
            for lower in string.ascii_lowercase:
                char = lower if name == "ABC" else lower.upper()
                key = key_with_tap(self.tabs[name], char)
                for actions, expected in [(key["press_actions"], char),
                        (variation(key, "left")["press_actions"], chr(ord(char)+0xFEE0))]:
                    text, _, target = run_actions(actions, current_tab=self.tabs[name]["identifier"])
                    self.assertEqual(text, expected)
                    self.assertEqual(target, "qed_abc_v30" if name == "ABC_Plus" else self.tabs[name]["identifier"])
            w = key_with_tap(self.tabs[name], "w" if name == "ABC" else "W")
            self.assertEqual(run_actions(variation(w, "bottom")["press_actions"])[0], "www.")

    def test_ascii_symbols_and_brackets_are_available(self):
        outputs = set()
        for data in self.tabs.values():
            for key in keys(data):
                for _, actions in gestures(key):
                    outputs.update(a["text"] for a in actions if a["type"] == "input")
        self.assertTrue(set(string.ascii_letters + string.digits + string.punctuation) <= outputs)
        self.assertTrue(set("「」（）【】『』［］〈〉｛｝＇＂") <= outputs)
        opening_to_closing = dict(zip("([{「（【『［〈｛", ")]}」）】』］〉｝"))
        for data in self.tabs.values():
            for key in keys(data):
                for _, actions in gestures(key):
                    for a in actions:
                        if a["type"] == "input":
                            for left, right in opening_to_closing.items():
                                self.assertNotEqual(a["text"], left+right)
                    self.assertFalse(any(a["type"] == "replace_last_characters" for a in actions))

    def test_number_pad_and_direct_decimal_input(self):
        data = self.tabs["123"]
        positions = {(k["specifier"]["x"], k["specifier"]["y"]): k["key"] for k in data["interface"]["keys"]}
        for n in range(1, 10):
            self.assertEqual(positions[(1+(n-1)%3, (n-1)//3)]["press_actions"][0]["text"], str(n))
        for digit in string.digits:
            key = key_with_tap(data, digit)
            self.assertEqual(run_actions(key["longpress_actions"]["start"])[0], chr(ord(digit)+0xFEE0))
        for sample in ["09012345678", "2026/09/18", "-1234.50", "3+2=5"]:
            routes = {}
            for key in keys(data):
                for gesture, actions in gestures(key):
                    if "hold" not in gesture and actions[0]["type"] == "input":
                        routes[actions[0]["text"]] = actions
            text = ""
            for char in sample:
                text, _, _ = run_actions(routes[char], text)
            self.assertEqual(text, sample)

    def test_flick_character_labels_match_inserted_text(self):
        for name, data in self.tabs.items():
            for key in keys(data):
                for v in key["variations"]:
                    value = v["key"]
                    label = value["design"]["label"].get("text", "")
                    first = value["press_actions"][0]
                    # A one-character label advertises that exact character.
                    if len(label) == 1 and first["type"] == "input":
                        self.assertEqual(label, first["text"], (name, label))

    def test_editing_is_consistent_and_preserves_word_boundary(self):
        baseline_delete, baseline_space = None, None
        for data in self.tabs.values():
            delete = next(k for k in keys(data) if k["press_actions"][0]["type"] == "delete")
            space = key_with_tap(data, " ")
            if baseline_delete is None:
                baseline_delete, baseline_space = deepcopy(delete), deepcopy(space)
            self.assertEqual(delete, baseline_delete)
            self.assertEqual(space, baseline_space)
            word_delete = variation(delete, "left")["press_actions"]
            self.assertEqual(run_actions(word_delete, "日本語 フリック")[0], "日本語 ")
            self.assertEqual(run_actions(word_delete, "日本語 ")[0], "日本語 ")
            self.assertEqual(run_actions(word_delete, "かな`ABC")[0], "かな`")
            self.assertEqual(run_actions(word_delete, "")[0], "")
            self.assertEqual(run_actions(variation(delete, "top")["press_actions"], "abc", 1)[0], "ac")
            self.assertEqual(delete["longpress_actions"]["repeat"], [{"type": "delete", "count": 1}])
            for direction, delta in [("left", -1), ("right", 1)]:
                hold = variation(space, direction)["longpress_actions"]
                self.assertEqual(hold["repeat"], [{"type": "move_cursor", "count": delta}])
                self.assertEqual(run_actions(hold["start"], "abc", 1)[1], 1+delta)


if __name__ == "__main__":
    unittest.main()
