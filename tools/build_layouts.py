"""Build QED Input 3.0 with Python's standard library only."""

from copy import deepcopy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "archive" / "2.0"
ORDER = ("KANA", "ABC", "ABC_Plus", "CAPS", "123", "UTILITY")
IDS = {"KANA": "kana", "ABC": "abc", "ABC_Plus": "abc_plus",
       "CAPS": "caps", "123": "123", "UTILITY": "util"}
DIRECTIONS = ("left", "top", "right", "bottom")
BOUNDARIES = list(dict.fromkeys('\n \t　.,?!。、？！「」（）(){}[]-_－＿/／\\＼|｜~〜・･¥￥$＄%％°℃+＋×÷√^＾*＊@＠&＆#＃※=＝<＜>＞:：;；\'＇"＂`｀…【】『』《》〈〉［］｛｝'))


def action(kind, **kwargs):
    return {"type": kind, **kwargs}


def inputs(text):
    return [action("input", text=text)]


def move(name):
    return action("move_tab", tab_type="custom", identifier=f"qed_{IDS[name]}_v30")


def hold(start=None, repeat=None, duration="normal"):
    return {"duration": duration, "start": start or [], "repeat": repeat or []}


def flick(direction, label, actions, longpress=None):
    return {"type": "flick_variation", "direction": direction,
            "key": {"design": {"label": {"text": label}},
                    "press_actions": actions,
                    "longpress_actions": longpress or hold()}}


def custom(main, actions, variations=(), longpress=None, color="normal"):
    variations = list(variations)
    label = {"text": main}
    if variations:
        label = {"type": "main_and_directions", "main": main,
                 "directions": {v["direction"]: v["key"]["design"]["label"]["text"]
                                for v in variations}}
    return {"design": {"label": label, "color": color}, "press_actions": actions,
            "longpress_actions": longpress or hold(), "variations": variations}


def place(x, y, key, width=1, height=1, system=False):
    return {"specifier_type": "grid_fit",
            "specifier": {"x": x, "y": y, "width": width, "height": height},
            "key_type": "system" if system else "custom", "key": key}


def tab(name, keys, width=5, height=4, language="ja_JP"):
    return {"input_style": "direct", "language": language,
            "metadata": {"custard_version": "1.2", "display_name": f"QED {name.replace('_Plus', '+')} 3.0"},
            "identifier": move(name)["identifier"],
            "interface": {"key_layout": {"type": "grid_fit", "row_count": width,
                                         "column_count": height},
                          "key_style": "tenkey_style", "keys": keys}}


def delete_key():
    back = action("delete", count=1)
    forward = action("delete", count=-1)
    word = action("smart_delete", direction="backward", targets=BOUNDARIES)
    return custom("⌫", [back], [
        flick("left", "区切", [word], hold([word])),
        flick("top", "前消", [forward], hold([forward], [forward])),
        flick("bottom", "閉じる", [move("KANA"), action("dismiss_keyboard")]),
    ], hold([back], [back]), "special")


def space_key():
    left, right = action("move_cursor", count=-1), action("move_cursor", count=1)
    history = action("move_tab", tab_type="system", identifier="clipboard_history_tab")
    return custom("空白", inputs(" "), [
        flick("left", "←", [left], hold([left], [left])),
        flick("top", "貼付", [action("paste")], hold([history])),
        flick("right", "→", [right], hold([right], [right])),
        flick("bottom", "全角", inputs("　")),
    ], hold([action("toggle_cursor_bar")]), "special")


def cursor_key(count):
    step = action("move_cursor", count=count)
    return custom("←" if count < 0 else "→", [step], [
        flick("left", "←", [action("move_cursor", count=-1)],
              hold([action("move_cursor", count=-1)], [action("move_cursor", count=-1)])),
        flick("top", "行頭", [action("smart_move_cursor", direction="backward", targets=["\n"])]),
        flick("right", "→", [action("move_cursor", count=1)],
              hold([action("move_cursor", count=1)], [action("move_cursor", count=1)])),
        flick("bottom", "行末", [action("smart_move_cursor", direction="forward", targets=["\n"])]),
    ], hold([step], [step]), "special")


def nav_key(main, target):
    return custom(main, [move(target)], [
        flick("left", "かな", [move("KANA")]),
        flick("top", "CAPS", [move("CAPS")]),
        flick("right", "ABC", [move("ABC")]),
        flick("bottom", "123", [move("123")]),
    ], hold([move("UTILITY")]), "special")


def utility_key(on_utility=False):
    return custom("戻る" if on_utility else "操作", [move("KANA" if on_utility else "UTILITY")], [
        flick("left", "かな", [move("KANA")]),
        flick("top", "幅", [action("enable_resizing_mode")]),
        flick("right", "ABC", [move("ABC")]),
        flick("bottom", "タブ", [action("toggle_tab_bar")]),
    ], hold([action("enable_resizing_mode")]), "special")


def side_keys(on_utility=False):
    return [place(0, 0, nav_key("ABC", "ABC")),
            place(0, 1, cursor_key(-1)), place(0, 2, cursor_key(1)),
            place(0, 3, utility_key(on_utility)), place(4, 0, delete_key()),
            place(4, 1, space_key()), place(4, 2, nav_key("123", "123")),
            place(4, 3, {"type": "enter"}, system=True)]


VOICED = dict(zip("かきくけこさしすせそたちつてとはひふへほう", "がぎぐげござじずぜぞだぢづでどばびぶべぼゔ"))
SMALL = dict(zip("あいうえおやゆよわ", "ぁぃぅぇぉゃゅょゎ"))


def kana_hold(char):
    alternative = VOICED.get(char, SMALL.get(char))
    alternative = {"ん": "ぬ", "、": "。", "。": "、", "？": "！", "っ": "つ"}.get(char, alternative)
    return hold(inputs(alternative), duration="light") if alternative else hold()


def kana_tab():
    # Ogura's central high-frequency keys and connecting flick directions.
    # Plain kana always remain literal; small kana are explicit long presses.
    rows = [
        [("う", "むわちせ"), ("か", "よつくら"), ("し", "ゆやじっ")],
        [("に", "ねそなも"), ("い", "きりまる"), ("た", "てすえめ")],
        [("の", "ろどさみ"), ("ん", "だがでを"), ("と", "こあ、れ")],
        [("お", "へほけぬ"), None, ("は", "ふひ？。")],
    ]
    keys = side_keys()
    for y, row in enumerate(rows):
        for x, entry in enumerate(row, 1):
            if entry is None:
                modifier = custom("小゛゜", [action("replace_default", replace_type="default", fallbacks=[])], [
                    flick("left", "「", inputs("「"), hold(inputs("（"), duration="light")),
                    flick("top", "ー", inputs("ー"), hold(inputs("〜"), duration="light")),
                    flick("right", "」", inputs("」"), hold(inputs("）"), duration="light")),
                    flick("bottom", "゜", [action("replace_default", replace_type="handakuten", fallbacks=[])]),
                ], hold(inputs("・"), duration="light"))
                keys.append(place(x, y, modifier))
            else:
                main, chars = entry
                variations = [flick(d, c, inputs(c), kana_hold(c)) for d, c in zip(DIRECTIONS, chars)]
                keys.append(place(x, y, custom(main, inputs(main), variations, kana_hold(main))))
    return tab("KANA", keys)


def fullwidth(text):
    return "".join(chr(ord(c) + 0xFEE0) if "!" <= c <= "~" else "　" if c == " " else c for c in text)


def old_tab(name):
    text = (ARCHIVE / f"QED_{name}_2.0.json").read_text(encoding="utf-8-sig")
    return json.loads(text.replace("_v20", "_v30").replace(" 2.0", " 3.0"))


def digit_keys():
    original = old_tab("123")["interface"]["keys"][:10]
    result = {}
    for wrapper in original:
        key = deepcopy(wrapper["key"])
        digit = key["press_actions"][0]["text"]
        # These directions represent width changes, not different brackets/quotes.
        for v in key["variations"]:
            value = v["key"]["press_actions"][0]["text"]
            if value in "[]{}'\"":
                v["key"]["longpress_actions"] = hold(inputs(fullwidth(value)), duration="light")
        result[digit] = key
    return result


def number_tab():
    digits = digit_keys()
    keys = side_keys()
    # Same editing keys and geometry as KANA; no tab change for arithmetic symbols.
    keys = [k for k in keys if (k["specifier"]["x"], k["specifier"]["y"]) != (4, 2)]
    keys.append(place(4, 2, custom("+", inputs("+"), [
        flick("left", "-", inputs("-")), flick("top", "*", inputs("*")),
        flick("right", "/", inputs("/")), flick("bottom", "=", inputs("=")),
    ], hold(inputs("＋"), duration="light"))))
    for n in range(1, 10):
        key = digits[str(n)]
        key["design"]["label"] = custom(str(n), inputs(str(n)), key["variations"])["design"]["label"]
        keys.append(place(1 + (n - 1) % 3, (n - 1) // 3, key))
    zero = digits["0"]
    zero["design"]["label"] = custom("0", inputs("0"), zero["variations"])["design"]["label"]
    keys.append(place(2, 3, zero))
    keys.append(place(1, 3, custom(".", inputs("."), [
        flick("left", ",", inputs(",")), flick("top", ":", inputs(":"), hold(inputs("："), duration="light")),
        flick("right", ";", inputs(";"), hold(inputs("；"), duration="light")),
        flick("bottom", "/", inputs("/")),
    ], hold(inputs("．"), duration="light"))))
    keys.append(place(3, 3, custom("-", inputs("-"), [
        flick("left", "_", inputs("_")), flick("top", "?", inputs("?"), hold(inputs("？"), duration="light")),
        flick("right", "!", inputs("!"), hold(inputs("！"), duration="light")),
        flick("bottom", "=", inputs("=")),
    ], hold(inputs("－"), duration="light"))))
    return tab("123", keys, language="en_US")


def english_tab(name):
    data = old_tab(name)
    digits = digit_keys()
    for wrapper in data["interface"]["keys"]:
        if wrapper["key_type"] == "system":
            continue
        key = wrapper["key"]
        x, y = wrapper["specifier"]["x"], wrapper["specifier"]["y"]
        first = key["press_actions"][0]
        char = first.get("text", "")
        if y == 0:
            wrapper["key"] = deepcopy(digits[char])
        elif len(char) == 1 and char.isascii() and char.isalpha():
            lower, upper = char.lower(), char.upper()
            one_shot = [move("ABC")] if name == "ABC_Plus" else []
            def type_letter(text):
                return inputs(text) + one_shot
            if name == "ABC":
                variants = [flick("left", fullwidth(lower), inputs(fullwidth(lower))),
                            flick("top", fullwidth(upper), inputs(fullwidth(upper)))]
                longpress = hold(inputs(upper), duration="light")
            else:
                variants = [flick("left", fullwidth(upper), type_letter(fullwidth(upper)))]
                if name == "CAPS":
                    variants.append(flick("right", fullwidth(lower), inputs(fullwidth(lower))))
                longpress = hold(type_letter(fullwidth(upper)), duration="light")
            if lower == "b":
                # Restore ｂ/Ｂ at left; # gets its own direction.
                variants.append(flick("bottom", "#", type_letter("#"), hold(type_letter("＃"), duration="light")))
            shortcut = {"q": "qu" if name == "ABC" else "QU", "w": "www.",
                        "m": ".com" if name == "ABC" else ".COM"}.get(lower)
            if shortcut:
                variants.append(flick("bottom", shortcut, type_letter(shortcut),
                                      hold(type_letter(fullwidth(shortcut)), duration="light")))
            wrapper["key"] = custom(char, type_letter(char), variants, longpress)
        elif first["type"] == "delete":
            wrapper["key"] = delete_key()
        elif char == " ":
            wrapper["key"] = space_key()
        elif y == 4 and x == 0:
            wrapper["key"] = nav_key("あA", "KANA")
        elif y == 4 and x == 11:
            wrapper["key"] = nav_key("123", "123")
        elif y == 4 and x == 15:
            wrapper["key"] = utility_key()
        elif y == 4 and x == 3:
            wrapper["key"] = custom(".", inputs("."), [
                flick("left", ",", inputs(",")), flick("top", "?", inputs("?"), hold(inputs("？"), duration="light")),
                flick("right", "!", inputs("!"), hold(inputs("！"), duration="light")),
                flick("bottom", ":", inputs(":"), hold(inputs(";"), duration="light")),
            ], hold(inputs("…"), duration="light"))
        elif y == 3 and x == 0:
            wrapper["key"] = custom("⇧" if name != "CAPS" else "⇪",
                [move("ABC_Plus" if name == "ABC" else "ABC")], [
                    flick("left", "`", inputs("`")), flick("top", "'", inputs("'")),
                    flick("right", '"', inputs('"')), flick("bottom", "_", inputs("_")),
                ], hold([move("ABC" if name == "CAPS" else "CAPS")]), "special")
    return data


def utility_tab():
    old = old_tab("UTILITY")["interface"]["keys"]
    named = {k["key"].get("design", {}).get("label", {}).get("main"): deepcopy(k["key"]) for k in old}
    keys = side_keys(on_utility=True)
    rows = [["挨拶", "返事", "丁寧"], ["開括弧", "閉括弧", "記号"],
            ["URL", "開発", "MD"], ["数式", "単位", "矢印"]]
    for y, row in enumerate(rows):
        for x, name in enumerate(row, 1):
            if name in ("開括弧", "閉括弧"):
                chars = "「（【『［〈" if name == "開括弧" else "」）】』］〉"
                key = custom(chars[0], inputs(chars[0]), [flick(d, c, inputs(c)) for d, c in zip(DIRECTIONS, chars[1:5])],
                             hold(inputs(chars[5]), duration="light"))
            else:
                key = named[name]
                if name == "返事":
                    # Explicit connective shortcuts replace implicit expansion on 小゛゜.
                    for v, text in zip(key["variations"], ["なので", "つまり", "たとえば", "ですが"]):
                        v["key"]["longpress_actions"] = hold(inputs(text))
                if name == "MD":
                    key["longpress_actions"] = hold(inputs("**"))
                    for v in key["variations"]:
                        if v["direction"] == "top":
                            v["key"]["press_actions"] = inputs("`")
                            v["key"]["longpress_actions"] = hold(inputs("```\n"))
                        elif v["direction"] in ("right", "bottom"):
                            text = v["key"]["press_actions"][0]["text"]
                            v["key"]["design"]["label"] = {"text": text.replace(" ", "␠")}
            keys.append(place(x, y, key))
    return tab("UTILITY", keys)


def build():
    tabs = {"KANA": kana_tab(), "123": number_tab(), "UTILITY": utility_tab()}
    tabs.update({name: english_tab(name) for name in ("ABC", "ABC_Plus", "CAPS")})
    for data in tabs.values():
        data["interface"]["keys"].sort(key=lambda k: (k["specifier"]["y"], k["specifier"]["x"]))
    return [tabs[name] for name in ORDER]


def main():
    tabs = build()
    for name, data in zip(ORDER, tabs):
        (ROOT / f"QED_{name}_3.0.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "00_QED_Input_KANA_DEFAULT_3.0.json").write_text(json.dumps(tabs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Built 6 QED Input 3.0 tabs and the combined import file.")


if __name__ == "__main__":
    main()
