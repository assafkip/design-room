# Sample — Design Spec (POSITIVE fixture: every token sourced)

## Identity
- Name-first concept: notes that keep their source
- One-sentence test: "every highlight remembers where it came from"

## Tokens

### Color
- background: #0a0a0a  source: grounding/tokens.md#bg
- surface: #14141a  source: grounding/tokens.md#surface
- text: #f4f4f5  source: grounding/tokens.md#text
- primary: #5b8cff  source: fork:primary-hue
- border: #27272a  source: grounding/tokens.md#border

### Type
- font-display: GT Sectra  source: grounding/teardown-stripe.md#display
- font-body: Söhne  source: grounding/teardown-stripe.md#body
- scale: 1.250 major third, base 16px  source: grounding/tokens.md#scale

### Space & shape
- spacing: 4/8/16/32/64  source: grounding/tokens.md#space
- radius: 8px  source: fork:radius

### Motion
- signature: paper-design fluted-glass hero  source: fork:signature-moment
- scroll: lenis  source: grounding/teardown-stripe.md#scroll

## Rationale
- Every token above traces to a grounding teardown or a founder fork. Nothing
  was originated by Claude.
