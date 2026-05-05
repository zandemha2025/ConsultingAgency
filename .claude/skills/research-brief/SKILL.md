---
name: research-brief
description: McKinsey/BCG-grade research on any topic. Produces a 1-3 page brief (md+pdf+docx), a deeper ontology (mermaid concept map + glossary), a slide deck (md+html+pdf+pptx), and PNG charts with citations - all organized under ~/Desktop/consulting/<client>/. Built on the Feynman multi-agent research toolchain (researcher / verifier / reviewer / writer agents with provenance-tracked sources). Use whenever the user asks for "research on X", "a brief on X", "MBB / consulting / strategy analysis of X", or anything that should ship as a polished consulting deliverable.
---

# research-brief

Run a strategy-consultant-grade research workflow for the user's topic and ship a full deliverable bundle (brief + ontology + deck + charts + sources) into `~/Desktop/consulting/<client>/<topic>-<date>/`.

The skill directory ships with helper scripts and templates - **use them**, don't reinvent the wheel.

```
.claude/skills/research-brief/
├── SKILL.md                 # this file
├── scripts/
│   ├── bootstrap.sh         # idempotent: installs Feynman + marp-cli + python deps + pandoc
│   ├── new_run.sh           # creates the run dir under ~/Desktop/consulting/
│   ├── run_feynman.sh       # invokes feynman deepresearch, harvests outputs/
│   ├── slugify.sh           # URL-safe slug helper
│   ├── chart_engine/        # JSON-spec -> PNG (matplotlib) / PNG+HTML (plotly)
│   ├── make_charts.py       # CLI wrapper around chart_engine
│   ├── render_brief.sh      # brief.md -> brief.pdf + brief.docx
│   └── render_deck.sh       # deck.md -> deck.html + deck.pdf + deck.pptx
├── templates/               # brief / ontology / deck / chart-spec skeletons
└── references/              # mbb_style.md, chart_idioms.md - read these before drafting
```

## Workflow (what to do every time)

### 1. Parse the request

- Extract `<topic>` from the user's message (the substantive subject - "EV charging in Germany", "vertical SaaS for HVAC", etc.).
- Extract `<client>` from a `--client X` flag, prior conversation context (the engagement this is for), or `AskUserQuestion` once if absent. Never invent a client name.
- If the user supplied additional scoping (timeframe, geography, audience), capture it - it goes into the templates' `{{scope}}` slots.

### 2. Bootstrap the environment

Run `bash .claude/skills/research-brief/scripts/bootstrap.sh` from the repo root. It is idempotent and silent on subsequent runs. **Feynman is a hard dependency** - if the binary is missing the script auto-installs it via `curl -fsSL https://feynman.is/install | bash`. Do not skip this step. If the script exits non-zero, surface its stderr and stop - do not pretend to research without Feynman.

### 3. Provision the run directory

```bash
RUN_DIR="$(bash .claude/skills/research-brief/scripts/new_run.sh "<client>" "<topic>")"
```

Captures the absolute path of `~/Desktop/consulting/<client-slug>/<topic-slug>-YYYYMMDD/`. The script creates `charts/`, `sources/`, `deck/` inside it.

### 4. Run Feynman deep research

```bash
bash .claude/skills/research-brief/scripts/run_feynman.sh "<topic>" "$RUN_DIR"
```

This invokes `feynman deepresearch "<topic>"` which runs Feynman's researcher / verifier / reviewer agents. It copies all `outputs/*` (cited brief + `.provenance.md` sidecar) into `$RUN_DIR/sources/feynman/`. **Read every file Feynman produced before writing your synthesis** - those are your ground-truth citations. If the script exits non-zero, surface the error and stop.

### 5. Synthesize MBB-style

Before writing anything, **read** these two reference files:
- `.claude/skills/research-brief/references/mbb_style.md` (MECE, SCQA, action titles, So-What test)
- `.claude/skills/research-brief/references/chart_idioms.md` (which chart for which insight)

Then produce four files inside `$RUN_DIR/`, each based on the matching template:

| Output | Template | Notes |
|---|---|---|
| `brief.md` | `templates/brief.md.tpl` | 1-3 pages. Action-title exec summary at top. SCQA framing. MECE 3-bucket analysis. Recommendations. Risks. Citations footer keyed `[1]`, `[2]`... back to `sources/feynman/*.provenance.md` |
| `ontology.md` | `templates/ontology.md.tpl` | Mermaid `graph TD` of key concepts + relationships. Glossary table. Open-questions list. Goes deeper than the brief - this is for the analyst, not the partner. |
| `deck.md` | `templates/deck.md.tpl` | 8-12 Marp slides: cover, exec summary, situation, complication, key insight, one slide per MECE bucket, recommendations, next steps, appendix. Action titles only - never topic titles. |
| `charts/spec.json` | `templates/chart_spec.example.json` | Array of chart specs. Pick chart types per `chart_idioms.md`. Every chart MUST have `"source"` populated. |

**Citation discipline**: every numeric claim, market size, growth rate, or third-party assertion in `brief.md` and `deck.md` must carry a footnote pointing to a Feynman provenance entry. If Feynman did not cover something, do not assert it.

### 6. Render the deliverables

Run these three in parallel (they're independent):

```bash
python3 .claude/skills/research-brief/scripts/make_charts.py "$RUN_DIR/charts/spec.json"
bash   .claude/skills/research-brief/scripts/render_brief.sh "$RUN_DIR"
bash   .claude/skills/research-brief/scripts/render_deck.sh  "$RUN_DIR"
```

`make_charts.py` writes PNGs (and `.html` for any chart whose backend is `plotly` with `interactive_html: true`) into `$RUN_DIR/charts/`. The brief and deck reference these by relative path - keep filenames stable (use the chart's `id`).

### 7. Report back to the user

Print:
- Absolute path of `$RUN_DIR`
- A short tree of the files generated
- One-paragraph executive summary (the action-title sentence from `brief.md`)
- A note that the user can re-render charts with a different backend via `make_charts.py --backend plotly` if they want interactive HTML

Offer to open the deck PDF if you have a way to do so.

## Anti-patterns to avoid

- **Don't fabricate citations.** If Feynman didn't surface a source, say so or omit the claim.
- **Don't skip the templates.** They encode the MBB structure. Filling them in is the job.
- **Don't write topic titles** ("Market overview"). Use action titles ("EV charger demand outpaces grid investment 3:1 through 2030").
- **Don't dump the Feynman brief verbatim** into `brief.md`. Synthesize it through the SCQA + MECE structure.
- **Don't invent client names.** Ask once if missing.
- **Don't bypass `bootstrap.sh`** even if Feynman is "probably" installed - the script is idempotent and free.

## Re-running

The skill is one-shot per invocation. To refresh a run, delete the dated subdir and re-invoke. To compare two angles on the same topic, use a different `<topic>` phrasing - each gets its own dated folder under the same client.
