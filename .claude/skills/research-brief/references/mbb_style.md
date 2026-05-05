# MBB writing style cheatsheet

Keep this open while drafting `brief.md` and `deck.md`. Every section / slide should pass these tests.

## 1. Action titles, never topic titles

A topic title says **what the slide is about**. An action title says **what we want the reader to conclude**.

| Topic (BAD) | Action (GOOD) |
|---|---|
| "Market overview" | "EV charger demand outpaces grid investment 3:1 through 2030" |
| "Customer segmentation" | "Two segments - fleet operators and highway travelers - drive 70% of value" |
| "Regulatory landscape" | "EU AFIR mandates create a 4-year window before saturation closes the gap" |

**Rule of thumb:** if the title contains a verb and a number, you're probably close. If it ends in "...overview", "...landscape", or "...analysis", rewrite it.

## 2. SCQA - the brief's spine

Every brief opens with:

- **Situation**: the stable, agreed reality. Reader nods.
- **Complication**: the disrupting force. Reader leans in.
- **Question**: the governing question. Reader needs the answer.
- **Answer**: the key insight, stated as an action title.

Then the body proves the answer with three MECE buckets.

## 3. MECE - the body structure

Buckets must be:

- **Mutually Exclusive** - no overlap between buckets.
- **Collectively Exhaustive** - together they cover the answer space.

Three is the magic number. Two feels thin; four feels diffuse. Common decompositions:

- **Demand / Supply / Regulation**
- **Customer / Competitor / Company** (3Cs)
- **Where to play / How to win / What to invest** (strategy stack)
- **Now / 2-3 years / 5+ years** (time horizons)
- **Build / Buy / Partner** (M&A choice)

If your three buckets overlap or leave gaps, **redo the cut** before drafting prose.

## 4. The Pyramid Principle

Every assertion is supported by exactly the points one level below it. Read top-down, the brief makes sense without the appendix; read bottom-up, every fact ladders up to the bottom-line sentence.

When you write a bucket header, ask: *"Which 3 sub-points support this and only this?"* If you can't name them, the header is wrong.

## 5. The "So what?" test

After every paragraph, ask: *"What do I want the reader to do with this?"* If the answer is "...nothing, just know it", cut the paragraph. Every claim earns its space by changing a decision, narrowing an option, or sizing a bet.

## 6. Numbers carry their own citation

Every number that isn't a derivation must carry a footnote `[n]` mapping to a source in `sources/feynman/*.provenance.md`. Round numbers ("~$420B", "roughly 3:1") are fine - false precision ("$418.7B") is not, unless the source supports the digits.

## 7. Recommendations are commands

Recommendations are written as imperatives with an owner and a horizon, not as observations.

| Observation (BAD) | Command (GOOD) |
|---|---|
| "Consider partnerships" | "Sign 2 fleet-depot exclusives by Q3; Head of BD owns" |
| "There is opportunity in software" | "Build OS-layer charger management; CTO; 12-month horizon" |

## 8. Risks are real, not hedges

A risk slide that lists "execution risk, market risk, regulatory risk" adds nothing. List specific risks with the trigger, the indicator to watch, and the mitigation:

> **Grid interconnect lead-time slips past 18 months.** Trigger: 2 of next 5 sites delayed. Watch: utility queue length monthly. Mitigate: pre-buy substations from top-3 vendors.

## 9. Deck != brief

The deck is a billboard, not the brief reformatted. Each slide has:

- One action title
- 3-5 bullets max OR one chart
- A footer footnoting the source

If you need 8 bullets, you have 2 slides.

## 10. Structure first, polish second

Get the action titles right, then the structure right, then the prose. Polishing prose under a wrong structure is the most common waste.
