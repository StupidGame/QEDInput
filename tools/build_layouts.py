"""Build QED Input 3.0 from the original layouts with small, explicit fixes."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "archive" / "2.0"
ORDER = ("KANA", "ABC", "ABC_Plus", "CAPS", "123", "UTILITY")
QUOTE_KEYS = {"KANA": ((0, 3), (3, 2)), "ABC": ((11, 4),),
              "ABC_Plus": ((11, 4),), "CAPS": ((11, 4),),
              "123": ((11, 3),), "UTILITY": ((1, 3),)}


def load_original(name):
    data = json.loads((ARCHIVE / f"QED_{name}_2.0.json").read_text(encoding="utf-8-sig"))
    data["metadata"]["display_name"] = data["metadata"]["display_name"].removesuffix(" 2.0") + " 3.0"
    data["identifier"] = data["identifier"].removesuffix("_v20") + "_v30"

    def update_links(value):
        if isinstance(value, dict):
            if value.get("type") == "move_tab" and value.get("tab_type") == "custom":
                value["identifier"] = value["identifier"].removesuffix("_v20") + "_v30"
            for child in value.values():
                update_links(child)
        elif isinstance(value, list):
            for child in value:
                update_links(child)

    update_links(data)
    return data


def key_at(data, x, y):
    return next(k["key"] for k in data["interface"]["keys"]
                if (k["specifier"]["x"], k["specifier"]["y"]) == (x, y))


def add_flick(key, direction, text, *, one_shot=False, held_text=None):
    assert all(v["direction"] != direction for v in key["variations"])
    actions = [{"type": "input", "text": text}]
    if one_shot:
        actions.append({"type": "move_tab", "tab_type": "custom", "identifier": "qed_abc_v30"})
    key["variations"].append({
        "type": "flick_variation", "direction": direction,
        "key": {"design": {"label": {"text": text}}, "press_actions": actions,
                "longpress_actions": {"duration": "light" if held_text else "normal",
                    "start": [{"type": "input", "text": held_text}] if held_text else [], "repeat": []}},
    })


def fix_quote_holds(key):
    # Keep the original bracket alternatives, including [ -> 【.
    for part in [key] + [v["key"] for v in key.get("variations", [])]:
        press = part.get("press_actions", [])
        if len(press) == 1 and press[0].get("type") == "input":
            fullwidth = {"'": "＇", '"': "＂"}.get(press[0]["text"])
            if fullwidth:
                for action in part["longpress_actions"]["start"]:
                    if action.get("type") == "input" and action.get("text") in ("’", "”"):
                        action["text"] = fullwidth


def build():
    tabs = {name: load_original(name) for name in ORDER}
    key_at(tabs["KANA"], 1, 2)["design"]["label"]["sub"] = "←ゆ ↑や →？ ↓っ"
    key_at(tabs["KANA"], 2, 3)["design"]["label"]["sub"] = "←「 ↑ー →」 ↓ぬ"

    # Preserve left flick #; add fullwidth B only in unused slots.
    add_flick(key_at(tabs["ABC"], 11, 3), "right", "ｂ")
    add_flick(key_at(tabs["ABC_Plus"], 11, 3), "right", "Ｂ", one_shot=True)
    key_at(tabs["CAPS"], 11, 3)["design"]["label"]["directions"]["left"] = "#"
    for wrapper in tabs["123"]["interface"]["keys"]:
        if wrapper["key_type"] == "custom":
            fix_quote_holds(wrapper["key"])

    brackets = key_at(tabs["UTILITY"], 0, 1)
    brackets["design"]["label"]["sub"] = "「 〈"
    for variation in brackets["variations"]:
        hold = variation["key"]["longpress_actions"]
        assert not hold["start"] and not hold["repeat"]
        closing = {"left": "）", "top": "】", "right": "』", "bottom": "］"}[variation["direction"]]
        hold["start"] = [{"type": "input", "text": closing}]

    # One gesture for a quote without switching tabs or moving an existing input.
    for name, positions in QUOTE_KEYS.items():
        for x, y in positions:
            key = key_at(tabs[name], x, y)
            add_flick(key, "top", '"', held_text="＂")
            label = key["design"]["label"]
            main = label.get("main", label.get("text"))
            sub = " ".join(filter(None, [label.get("sub"), '↑"']))
            key["design"]["label"] = {"type": "main_and_sub", "main": main, "sub": sub}
    return [tabs[name] for name in ORDER]


def main():
    tabs = build()
    for name, data in zip(ORDER, tabs):
        (ROOT / f"QED_{name}_3.0.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "00_QED_Input_KANA_DEFAULT_3.0.json").write_text(json.dumps(tabs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Built QED Input 3.0: original layouts with small fixes only.")


if __name__ == "__main__":
    main()
