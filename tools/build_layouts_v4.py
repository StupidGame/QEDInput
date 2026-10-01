"""Build QED Input 4.0 ergonomic proposal from the checked-in 3.0 layouts.

Design goals:
- preserve QED Input's compact 4x4 KANA structure and all existing actions
- keep the right-side control column stable
- move high-frequency ん into the active 3x3 typing area
- keep tap-optimized kana keys while making flick directions closer to conventional kana flick
- keep ABC / ABC+ / CAPS / 123 / UTILITY / MFM behavior unchanged apart from v4 IDs
"""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("KANA", "ABC", "ABC_Plus", "CAPS", "123", "UTILITY", "MFM")

DIRECTION_MAPS = {
    "か": {"き": "left", "く": "top", "け": "right", "こ": "bottom"},
    "し": {"さ": "left", "す": "top", "せ": "right", "そ": "bottom"},
    "と": {"ち": "left", "つ": "top", "て": "right", "た": "bottom"},
    "の": {"に": "left", "な": "top", "ね": "right", "、": "bottom"},
    "は": {"ひ": "left", "ふ": "top", "へ": "right", "ほ": "bottom"},
    "ま": {"み": "left", "む": "top", "め": "right", "も": "bottom"},
    "る": {"り": "left", "ら": "top", "れ": "right", "ろ": "bottom"},
}
DIR_ORDER = {"left": 0, "top": 1, "right": 2, "bottom": 3}

def walk_ids(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "identifier" and isinstance(child, str):
                value[key] = child.replace("_v30", "_v40")
            else:
                walk_ids(child)
    elif isinstance(value, list):
        for child in value:
            walk_ids(child)

def main_label(wrapper):
    label = wrapper.get("key", {}).get("design", {}).get("label", {})
    return label.get("main", label.get("text"))

def remap_flicks(wrapper, mapping):
    key = wrapper["key"]
    for variation in key.get("variations", []):
        label = variation.get("key", {}).get("design", {}).get("label", {})
        text = label.get("text", label.get("main"))
        if text in mapping:
            variation["direction"] = mapping[text]
    key["variations"].sort(key=lambda v: DIR_ORDER.get(v.get("direction"), 9))
    inverse = {direction: text for text, direction in mapping.items()}
    label = key.get("design", {}).get("label", {})
    if label.get("type") == "main_and_sub":
        label["sub"] = (
            f"←{inverse.get('left','')} ↑{inverse.get('top','')} "
            f"→{inverse.get('right','')} ↓{inverse.get('bottom','')}"
        )

def build():
    tabs = {}
    for name in NAMES:
        data = json.loads((ROOT / f"QED_{name}_3.0.json").read_text(encoding="utf-8"))
        data["metadata"]["display_name"] = data["metadata"]["display_name"].replace("3.0", "4.0")
        data["identifier"] = data["identifier"].replace("_v30", "_v40")
        walk_ids(data)
        tabs[name] = data

    kana = tabs["KANA"]
    wrappers = kana["interface"]["keys"]
    ma = next(w for w in wrappers if main_label(w) == "ま")
    nn = next(w for w in wrappers if main_label(w) == "ん")
    ma["specifier"], nn["specifier"] = copy.deepcopy(nn["specifier"]), copy.deepcopy(ma["specifier"])

    for label, mapping in DIRECTION_MAPS.items():
        wrapper = next(w for w in wrappers if main_label(w) == label)
        remap_flicks(wrapper, mapping)

    return [tabs[name] for name in NAMES]

def main():
    tabs = build()
    for name, data in zip(NAMES, tabs):
        (ROOT / f"QED_{name}_4.0.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    (ROOT / "00_QED_Input_KANA_DEFAULT_4.0.json").write_text(
        json.dumps(tabs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("Built QED Input 4.0 ergonomic proposal.")

if __name__ == "__main__":
    main()
