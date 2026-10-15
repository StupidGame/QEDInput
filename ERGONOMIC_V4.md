# QED Input 4.0 Ergonomic Proposal

This proposal keeps QED Input 3.0's features and tab structure, while changing only the parts that materially affect thumb travel and migration from conventional kana flick.

## KANA

```text
の   か   は   ⌫
い   と   よ   空白
ん   し   る   123
ABC  ま   小゛゜ 改行
```

The right-side control column stays fixed. This revision swaps whole `し`/`よ` and `と`/`の` key groups. `と` is now physically central, `し` is above `ま`, and `よ` is adjacent to `と`. Moving complete keys (rather than reassigning individual flick characters) preserves kana group learning and existing text shortcuts.

### Flick directions

The center-tap optimization is preserved, but the remaining kana are placed closer to conventional flick direction memory:

- か: ←き ↑く →け ↓こ
- し: ←さ ↑す →せ ↓そ
- と: ←ち ↑つ →て ↓た
- の: ←に ↑な →ね ↓、
- は: ←ひ ↑ふ →へ ↓ほ
- ま: ←み ↑む →め ↓も
- る: ←り ↑ら →れ ↓ろ

Existing behavior for `い`, `よ`, `ん`, `ま` (including the long-press `ます` shortcut), `小゛゜`, deletion, space, cursor movement, clipboard, long-press voiced sounds, automatic small ゃゅょ, and tab switching is retained. The `123` key gains a **left flick for full-width `！`** and a long-press of that flick for ASCII `!`, providing direct exclamation entry without removing the existing `よ →` question-mark / long-press exclamation shortcut. The `123` key label shows `←！ ↑"`.

## Other tabs

ABC, ABC+, and CAPS retain their 3.0 key geometry and letter actions, but move the half-width `@` shortcut from the far-left `1` key's left flick to **N ↓** near the right thumb. Long-pressing that flick still inputs full-width `＠`, and the N key visibly labels the new shortcut. All other key actions stay unchanged. The 123, UTILITY, and MFM tabs retain their 3.0 geometry and actions. All v4 identifiers and links coexist with 3.0.

## Rationale

- The Ogura layout emphasizes high-frequency taps and placing the **next key near the current flick's destination**. Read the original explanation https://note.com/jeebis_keyboard/n/n687c4aee3c6f and source https://github.com/JEEBIS27/azookey_ogura. QED keeps its phonetic clusters to preserve migration friendliness.
- Conventional directional memory is preserved where possible to reduce relearning.
- Editing and mode-switch controls remain in stable locations.
- The proposal intentionally avoids optimizing for only left- or right-handed use.
- The position changes here are a **hypothesis**, not a demonstrated typing-speed improvement. A small, hand-picked 72-phrase set (725 hiragana characters) was scored by distance from a previous tap/flick endpoint to the next key center with illustrative flick/long-press penalties. Previous positions scored 1,532.84 versus 1,347.87 arbitrary units after these swaps (~12.1% lower model cost). The model does NOT capture typing time, conversion, learning costs, error rate, or true Japanese usage frequency; phrases like この and なの can worsen when の leaves the center. Validate on a real keyboard before recommending this layout over the previous one.

## 連接と運指の追加検討

- 「し→ま」が隣接し、頻出の「します」で指を動かしやすくします（「ま」の長押し「ます」は維持）。
- 「と→し」が隣接し、「で→す」の移動距離が短くなります。
- 「し→よ」は斜め2キーの距離で、「しょう」などの入力に利用できます。
- 代償として「の」を中央から左上へ移したため、「この」「なの」などでは悪化する可能性があります。
- おぐら配列の『頻度＋フリック後の進行方向』を参考にしましたが、従来フリックと同じ母音方向、拗音の自動化、編集キー配置は維持しています。

注：上記のモデル値は代表性のある大規模コーパスではなく、実機速度試験の代用にはなりません。


## English / symbols ergonomic follow-up (2026-10-16)

The alphabetic keys stay QWERTY and the top digits, Shift, CAPS, punctuation, space, tab switching and N-down `@` are unchanged. QWERTY's familiarity is more valuable than an untested shuffle of the letter positions.

### One-gesture shortcuts (ABC / ABC+ / CAPS)

All three English modes give the same directions to the wide lower-row **記号** key, without switching to the 123 tab:

| Action on 記号 | Output | Hold at flick destination |
|---|---|---|
| left | `-` | fullwidth `－` |
| top (original) | `"` | fullwidth `＂` |
| right | `/` | fullwidth `／` |
| bottom | `'` | fullwidth `＇` |

The key still taps to 123 and long-presses to UTILITY. ABC Shift's original punctuation flicks, bottom-row punctuation `.,!?`, and the special B / N / M shortcuts are preserved.

### 123 symbol tab

- The `@` and `*` tap keys swap places in the 123 tab so `@` is central (x=8, y=1). The `1` key still has the old left-flick `@`, and the `*` tap has merely moved to the far-left slot; the `1` key's down-flick `*` is retained.
- The second-row `-` key gains **down-flick `_`** (hold: `＿`).
- The second-row `=` key gains **left `<`, up `==`, right `>`, down `!=`**. Hold on `<` and `>` gives `＜` / `＞`.
- The row of digits, every original symbol tap and long-press, quotes, brackets, backspace and bottom mode controls remain functional.

### UTILITY

- 開発 flick-and-hold shortcuts: `\\`→`＼`, `|`→`||`, `&`→`&&`, `_`→`＿`.
- 記号 flick-and-hold shortcuts: `・`→`･`, `〜`→`~`. Other symbol actions are unchanged.

### Ergonomics and caveats

This prioritizes frequently needed ASCII symbols closer to the bottom right-hand thumb reach, while keeping the QWERTY positions and numerical tap order. The new shortcuts require fewer mode changes or long top-row reaches but **do not constitute measured typing-speed improvements**. Fullwidth variants require a held flick as before. The 123 @/* swap adds relearning cost, and left-handed users may prefer the previous placement. All changes need an on-device Custard/azooKey import and touch test.
