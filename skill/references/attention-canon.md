# Attention canon — the cited principles the lenses read

This is the codified literature the `cited` lenses reason from. The room reads
THIS, not a live web search. Each principle: a name, a real source, what it says,
and the one **testable rule** it implies for a page. The `id` in backticks is what
`lens-registry.json` references and what `verify_design_room.py` checks for.

Modernity (what's trendy this month) lives in `build-palette.md`, refreshed by the
weekly pulse. This canon is the slow-moving, evidence-based layer — it does not
chase trends.

---

## `lindgaard-2006-50ms` — 50ms first impression
- **Source:** Lindgaard, Fernandes, Dudek & Brown (2006), "Attention web designers:
  You have 50 milliseconds to make a good first impression," *Behaviour & Information
  Technology* 25(2).
- **Says:** Visual-appeal judgments of a page form in ~50ms and correlate with
  judgments made after long exposure. The gut reaction precedes any reading.
- **Testable rule:** The page's visual gestalt (color, layout, type) must read as
  credible at a 50ms glance, before any copy is read. Test: blink-test a screenshot.

## `fz-scan-pattern` — F and Z reading paths
- **Source:** Nielsen Norman Group, F-pattern eye-tracking (2006, reaffirmed 2017);
  Z-pattern layout convention.
- **Says:** On text-dense pages eyes trace an F (two horizontal sweeps + a vertical);
  on sparse pages a Z. Top-left is read first, bottom-right last.
- **Testable rule:** The what-is-this and the primary action sit on the F/Z path —
  top-left weighted, primary action reachable in the first screen.

## `visual-hierarchy` — one dominant element per view
- **Source:** Gestalt grouping principles; typographic hierarchy (Müller-Brockmann).
- **Says:** Size, weight, color, and whitespace encode an importance order the eye
  follows; competing equal-weight elements flatten attention.
- **Testable rule:** Exactly one dominant element per viewport. Squint test: the most
  important thing is still the most prominent.

## `fitts-law` — target size and distance
- **Source:** Fitts (1954), "The information capacity of the human motor system."
- **Says:** Time to acquire a target grows with distance and shrinks with size.
- **Testable rule:** Primary targets are large and close to the user's path; minimum
  44px touch target; the main CTA is never stranded in a far corner.

## `hicks-law` — choice cost
- **Source:** Hick (1952) & Hyman (1953), the Hick–Hyman law.
- **Says:** Decision time grows with the number and complexity of choices.
- **Testable rule:** One primary action per screen; bounded nav choices; don't offer
  five equal CTAs.

## `von-restorff` — the isolation effect
- **Source:** von Restorff (1933), the isolation (von Restorff) effect.
- **Says:** The item that breaks the pattern is the one remembered.
- **Testable rule:** Spend the ONE bold, pattern-breaking moment on the thing you
  most want remembered. If everything is bold, nothing is. (This is the
  `boldness-feasibility` fork: where to spend it.)

## `aesthetic-usability` — beauty buys trust
- **Source:** Kurosu & Kashimura (1995); Nielsen Norman Group, "The Aesthetic-Usability
  Effect."
- **Says:** Users perceive more-beautiful interfaces as more usable and more
  trustworthy, and forgive minor friction.
- **Testable rule:** Polish raises perceived trust — so it must be honoured, not
  faked. A beautiful page that then mishandles the user breaks the trust it bought.

## `recognition-over-recall` — show, don't make them remember
- **Source:** Nielsen (1994), usability heuristic #6, "Recognition rather than recall."
- **Says:** Minimize memory load by making options and context visible; recognition
  is cheaper than recall.
- **Testable rule:** Describe the buyer's situation so they recognize it; don't make
  them recall or decode. (Pairs with `decision-psychology`: recognition, not diagnosis.)

## `krug-dont-make-me-think` — self-evidence
- **Source:** Krug (2000), *Don't Make Me Think*.
- **Says:** Every element should be self-evident; cognitive effort spent decoding the
  UI is effort not spent on the offer.
- **Testable rule:** Each element is self-evident without a label explaining it. If it
  needs an explanation, redesign it.

## `nielsen-heuristics` — the 10 usability heuristics
- **Source:** Nielsen (1994), "10 Usability Heuristics for User Interface Design."
- **Says:** Ten general heuristics (status visibility, match to the real world, user
  control, consistency, error prevention, recognition, flexibility, minimalist
  design, error recovery, help).
- **Testable rule:** No page element violates a heuristic; each violation is a named,
  fixable defect.

---

## How the lenses use this
- A `cited` lens emits: "principle `<id>` implies rule R; the page does / does not
  satisfy R." It never asserts a UX claim that isn't anchored here.
- If a needed judgment isn't covered by a canon principle, it is a **fork** for the
  founder, not an invented rule.
