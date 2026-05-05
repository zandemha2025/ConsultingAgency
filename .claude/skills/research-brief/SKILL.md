---
name: research-brief
description: McKinsey/BCG-grade research on any topic. Produces a 1-3 page brief (md+pdf+docx), a deeper ontology (mermaid concept map + glossary), a slide deck (md+html+pdf+pptx), and PNG charts with citations - all organized under ~/Desktop/consulting/<client>/. Uses a reverse-engineered Feynman-style multi-agent flow (researcher / verifier / reviewer subagents) executed natively inside Claude with WebSearch + WebFetch, so it works in any sandbox without external LLM auth. Use whenever the user asks for "research on X", "a brief on X", "MBB / consulting / strategy analysis of X", or anything that should ship as a polished consulting deliverable.
---

# research-brief

Run a strategy-consultant-grade research workflow for the user's topic and ship a full deliverable bundle (brief + ontology + deck + charts + sources) into `~/Desktop/consulting/<client>/<topic>-<date>/`.

The skill **reverse-engineers** Feynman's multi-agent research pattern (researcher → verifier → reviewer with provenance tracking) and executes it natively inside Claude using `Agent` subagents and `WebSearch` / `WebFetch`. No external LLM auth needed - this works in any Claude Code session.

If the `feynman` binary is installed AND authed, `scripts/run_feynman.sh` can augment the run with Feynman's own outputs. It's optional, not required.

```
.claude/skills/research-brief/
├── SKILL.md                 # this file
├── scripts/
│   ├── bootstrap.sh         # idempotent: installs marp-cli + python deps + pandoc; tries Feynman (optional)
│   ├── new_run.sh           # creates the run dir under ~/Desktop/consulting/
│   ├── run_feynman.sh       # OPTIONAL: invokes feynman deepresearch if installed+authed
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
- If the user supplied additional scoping (timeframe, geography, audience, budget), capture it and feed it into the templates' `{{scope}}` slots.
- If the user attached source documents (briefs, RFPs, prior decks), treat those as **primary sources** - the researcher agent must cross-reference everything against external evidence, not just rephrase the brief.

### 2. Bootstrap the environment

Run `bash .claude/skills/research-brief/scripts/bootstrap.sh` from the repo root. Installs marp-cli + python deps + pandoc. Tries to install Feynman opportunistically (npm first, then curl|bash) - if that fails, the skill still works because the multi-agent flow runs inside Claude.

### 3. Provision the run directory

```bash
RUN_DIR="$(bash .claude/skills/research-brief/scripts/new_run.sh "<client>" "<topic>")"
```

Captures `~/Desktop/consulting/<client-slug>/<topic-slug>-YYYYMMDD/`. The script creates `charts/`, `sources/`, `deck/` inside it. Inside `sources/`, you will create:
- `sources/researcher/` - raw findings + URLs (one md file per question)
- `sources/verifier/` - claim-by-claim cross-check notes
- `sources/reviewer/` - MBB-style critique of the draft
- `sources/feynman/` (only if feynman ran) - outputs harvested by `run_feynman.sh`

### 4. Run the multi-agent research flow (NATIVE)

This is the Feynman pattern, replicated:

#### 4a. Researcher (parallel, breadth-first)

Spawn **2-3 Explore subagents in parallel** (single message, multiple `Agent` tool calls). Each gets a slice of the question space. Every agent receives:

- The user's full request and any attached briefs (verbatim).
- A specific sub-question to answer.
- Instructions to use `WebSearch` and `WebFetch` to gather real, citable evidence.
- Instructions to **return a structured findings file** containing: claim, supporting source URL, source publication date, exact quote or stat, confidence (high/medium/low).
- The output path: `<RUN_DIR>/sources/researcher/<sub-question-slug>.md`.

Typical sub-question split for an audience/market question:
1. Market sizing + comparable benchmarks (TAM, audience size, comp campaigns)
2. Audience behavior + channel mix (where the audience actually consumes)
3. Risks + dissent + counter-evidence (what the brief might be missing)

For other topic types adjust accordingly (e.g., tech research: state-of-art / methods / open problems).

#### 4b. Verifier (single agent, claim-level cross-check)

After the researchers return, spawn ONE `general-purpose` Agent. Give it:

- Every researcher findings file path.
- Instructions to read each one, then for each claim: re-fetch the source URL with `WebFetch`, confirm the claim is actually supported, downgrade confidence if not, flag any source that 404s, paywalled, or doesn't say what was claimed.
- Output path: `<RUN_DIR>/sources/verifier/cross-check.md` with a verdict (verified / weak / refuted) per claim.

#### 4c. Synthesis (Claude main agent, NOT a subagent)

You (the main agent) read everything in `sources/researcher/` and `sources/verifier/` and draft `brief.md`, `ontology.md`, `deck.md`, and `charts/spec.json` per the templates. **Only verified or "weak-but-acknowledged" claims may appear in the final brief.** Refuted claims are dropped.

#### 4d. Reviewer (single agent, MBB style critique)

After the synthesis, spawn ONE `general-purpose` Agent. Give it:
- The drafted `brief.md` and `deck.md`.
- The contents of `references/mbb_style.md`.
- Instructions to critique against MBB principles (action titles, SCQA, MECE, So-What, citation discipline) and to write the critique to `<RUN_DIR>/sources/reviewer/critique.md`.

You then incorporate the critique into a revision pass before rendering.

#### 4e. (Optional) Feynman augmentation

If `feynman` is on PATH AND authed (check `feynman doctor 2>&1 | grep -q "default model: not set" && SKIP=1`), invoke `bash scripts/run_feynman.sh "<topic>" "$RUN_DIR"`. Treat its outputs as additional researcher findings - still pass them through the verifier.

### 5. Read the references before drafting

- `.claude/skills/research-brief/references/mbb_style.md` (MECE, SCQA, action titles, So-What test)
- `.claude/skills/research-brief/references/chart_idioms.md` (which chart for which insight)

### 6. Produce the four files (using the templates)

| Output | Template | Notes |
|---|---|---|
| `brief.md` | `templates/brief.md.tpl` | 1-3 pages. Action-title exec summary at top. SCQA framing. MECE 3-bucket analysis. Recommendations with owners and horizons. Risks. Citations footer keyed `[1]`, `[2]`... back to `sources/verifier/cross-check.md`. |
| `ontology.md` | `templates/ontology.md.tpl` | Mermaid `graph TD` of key concepts + relationships. Glossary table. Open-questions list. Goes deeper than the brief - this is for the analyst, not the partner. |
| `deck.md` | `templates/deck.md.tpl` | 8-12 Marp slides: cover, exec summary, situation, complication, key insight, one slide per MECE bucket, recommendations, next steps, appendix. Action titles only - never topic titles. |
| `charts/spec.json` | `templates/chart_spec.example.json` | Array of chart specs. Pick chart types per `chart_idioms.md`. Every chart MUST have `"source"` populated and traceable to verifier output. |

**Citation discipline**: every numeric claim, market size, growth rate, or third-party assertion in `brief.md` and `deck.md` must carry a footnote to a verifier-confirmed source. If the verifier marked it weak/refuted, drop it or hedge it explicitly.

### 7. Render the deliverables

Run these three in parallel (independent):

```bash
python3 .claude/skills/research-brief/scripts/make_charts.py "$RUN_DIR/charts/spec.json"
bash   .claude/skills/research-brief/scripts/render_brief.sh "$RUN_DIR"
bash   .claude/skills/research-brief/scripts/render_deck.sh  "$RUN_DIR"
```

`make_charts.py` writes PNGs (and `.html` for any chart whose backend is `plotly` with `interactive_html: true`) into `$RUN_DIR/charts/`. The brief and deck reference these by relative path - keep filenames stable (use the chart's `id`).

### 8. Report back to the user

Print:
- Absolute path of `$RUN_DIR`
- A short tree of the files generated
- One-paragraph executive summary (the action-title sentence from `brief.md`)
- The top 2-3 risks/caveats the verifier flagged
- A note that the user can re-render charts with a different backend via `make_charts.py --backend plotly` if they want interactive HTML

## Anti-patterns to avoid

- **Don't fabricate citations.** If the verifier couldn't confirm a source, drop the claim or hedge.
- **Don't skip the templates.** They encode the MBB structure. Filling them in is the job.
- **Don't write topic titles** ("Market overview"). Use action titles ("EV charger demand outpaces grid investment 3:1 through 2030").
- **Don't dump researcher findings verbatim** into `brief.md`. Synthesize through SCQA + MECE.
- **Don't invent client names.** Ask once if missing.
- **Don't bypass the verifier step.** It's the difference between "claims with citations" and "claims with citations that actually say what we said".
- **Don't skip the reviewer step.** A second pass against `mbb_style.md` catches the topic-title slide and the buried action-title every time.

## Re-running

The skill is one-shot per invocation. To refresh a run, delete the dated subdir and re-invoke. To compare two angles on the same topic, use a different `<topic>` phrasing - each gets its own dated folder under the same client.
