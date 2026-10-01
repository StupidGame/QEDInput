# QED Input 4.0 Ergonomic Proposal

This proposal keeps QED Input 3.0's features and tab structure, while changing only the parts that materially affect thumb travel and migration from conventional kana flick.

## KANA

```text
い   か   し   ⌫
と   の   は   空白
ん   よ   る   123
ABC  ま   小゛゜ 改行
```

The right-side control column stays fixed. `ん` moves from the bottom row into the active 3x3 typing area; `ま` takes its old bottom-row position.

### Flick directions

The center-tap optimization is preserved, but the remaining kana are placed closer to conventional flick direction memory:

- か: ←き ↑く →け ↓こ
- し: ←さ ↑す →せ ↓そ
- と: ←ち ↑つ →て ↓た
- の: ←に ↑な →ね ↓、
- は: ←ひ ↑ふ →へ ↓ほ
- ま: ←み ↑む →め ↓も
- る: ←り ↑ら →れ ↓ろ

Existing behavior for `い`, `よ`, `ん`, `小゛゜`, deletion, space, cursor movement, clipboard, long-press voiced sounds, automatic small ゃゅょ, and tab switching is retained.

## Other tabs

ABC, ABC+, CAPS, 123, UTILITY, and MFM preserve their 3.0 key geometry and actions. Their identifiers and links are updated to v4 so the proposal can coexist with 3.0.

## Rationale

- Frequency-first center taps are inspired by the same principle used by Ogura-style layouts.
- Conventional directional memory is preserved where possible to reduce relearning.
- Editing and mode-switch controls remain in stable locations.
- The proposal intentionally avoids optimizing for only left- or right-handed use.
