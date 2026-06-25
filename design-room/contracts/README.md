# design-room conformance contracts

Declarative contracts the generic engine (`scripts/verify_design_room.py`)
auto-discovers and checks against the skill at `$DESIGN_ROOM_SKILL_DIR`
(default: the in-repo `skill/` dir). The engine reads the actually-loaded
copy, not a separate mirror (load-path proof), and **fails closed** if that dir is
absent.

Each `*.json` file in this dir is one contract:

```json
{
  "name": "lenses",
  "target_file": "SKILL.md",          // path relative to the skill dir
  "assertions": [ { "kind": "...", ... }, ... ]
}
```

## Assertion kinds (all implemented in W0; later contracts are data-only)

- `present` — every regex in `patterns` MUST match the target (or `section`).
  `{ "kind": "present", "patterns": ["..."], "section": "## Heading" (optional), "reason": "..." }`
- `absent` — no regex in `patterns` may match the target (or `section`).
  `{ "kind": "absent", "patterns": ["..."], "section": "## Heading" (optional), "reason": "..." }`
- `registry_ids_present` — load a sibling JSON, pull values at `json_path`
  (dotted, `[]` = each list item), each value MUST appear in the target.
  `{ "kind": "registry_ids_present", "registry": "lens-registry.json", "json_path": "lenses[].id" }`

`section` slices the target to the markdown section under that heading (up to the
next same-or-higher heading) before matching — used to assert a property holds
*within* one phase (e.g. "the per-run phase contains no WebFetch").

Run all: `verify_design_room.py conform`. One: `conform --only <name>`.
