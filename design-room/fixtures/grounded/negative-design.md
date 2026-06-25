# Negative — Design Spec (NEGATIVE fixture: one token has NO source)

This file MUST fail check_token_provenance.py. The `accent` token below was
originated by Claude with no grounding and no fork — exactly what grounded mode
forbids. If the checker passes this file, the checker is broken (false green).

## Tokens

### Color
- background: #0a0a0a  source: grounding/tokens.md#bg
- surface: #14141a  source: grounding/tokens.md#surface
- text: #f4f4f5  source: grounding/tokens.md#text
- accent: #ff00aa
- border: #27272a  source: grounding/tokens.md#border

### Type
- font-display: GT Sectra  source: grounding/teardown-stripe.md#display
- font-body: Söhne  source: grounding/teardown-stripe.md#body
