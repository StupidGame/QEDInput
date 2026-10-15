# QED Input 4.0 Ergonomic Proposal

This proposal keeps QED Input 3.0's features and tab structure, while changing only the parts that materially affect thumb travel and migration from conventional kana flick.

## KANA

```text
と   か   は   ⌫
い   の   し   空白
ん   よ   る   123
ABC  ま   小゛゜ 改行
```

The right-side control column stays fixed. As in v4's initial design, `ん` is in the active 3x3 typing area while `ま` stays in the bottom row. This revision swaps the whole `い`/`と` key groups vertically on the left and the `し`/`は` key groups vertically on the right. The high-frequency `い` and `し` are now on the easier-to-reach middle row; all their existing flick outputs, auto-replacements and long presses travel with the keys. This trades some conventional row-position familiarity for easier central-row access, without splitting a kana group.

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

- Frequency-first center taps are inspired by the same principle used by Ogura-style layouts.
- Conventional directional memory is preserved where possible to reduce relearning.
- Editing and mode-switch controls remain in stable locations.
- The proposal intentionally avoids optimizing for only left- or right-handed use.
- The two pairwise position swaps are a testable ergonomic hypothesis rather than a measured speed guarantee. Existing muscle memory may favor the original positions; iPhone typing tests should determine whether the changes improve everyday use.
