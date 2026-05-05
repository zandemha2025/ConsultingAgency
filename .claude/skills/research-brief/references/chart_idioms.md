# Chart idioms - which chart for which insight

Pick the chart **after** you've written the action title. The chart's job is to make the title visually inevitable. If a reader has to study the chart to figure out the message, the chart (or the title) is wrong.

## Quick map

| If your action title is about... | Use | Why |
|---|---|---|
| Comparing magnitudes across categories | **bar** | Bars are the most accurate visual encoding of quantity. |
| Contributions adding up to a total across categories | **stacked_bar** | Shows mix and total simultaneously. |
| Change over time | **line** | Position-on-time is the most natural temporal encoding. |
| Cumulative growth or share-of-something over time | **area** | Conveys "stuff filling up". |
| Decomposition of a delta from start to end | **waterfall** | Each step's contribution is explicit. |
| Two attributes per item, looking for clusters/quadrants | **matrix2x2** | The classic strategy visual. |
| A 2D mix where both row & column have weights | **marimekko** | Width = market size; height = share. Use sparingly - dense. |
| A correlation or cloud of items | **scatter** | Look at clusters, outliers. |
| Few rows, mostly text, you want it to look like a figure | **table** | Sometimes the right chart is a table. |

## Anti-patterns

- **Pie charts**: avoid. Bar charts beat pies for every comparison task. Pies are okay only when there are exactly 2 slices and you want to evoke "share of a whole".
- **3D bars / 3D pies**: never. They distort area perception.
- **Dual-axis charts**: avoid unless the two series share a meaningful zero. Otherwise split into two charts.
- **Rainbow palettes**: pick 1 primary + 1 accent + grays. The deck palette is already wired.
- **Unlabeled axes**: every axis carries units. "($B)", "(% of revenue)", "(millions of users)".

## Chart spec checklist (before render)

- [ ] `title` is an action title (verb + number).
- [ ] `source` is filled in - tracks back to a `.provenance.md` entry.
- [ ] Units appear in `y_label` (or `x_label` if relevant).
- [ ] If using `series`, every series has a `name`.
- [ ] If the data is hard to read, you tried `interactive_html: true` with the plotly backend.
- [ ] Chart filename = chart `id` (kept stable for the deck and brief to reference).

## When to choose plotly over matplotlib

- The chart will be **explored** (zoom, hover) - send `backend: "plotly"`, `interactive_html: true`.
- Many series (>5) - plotly's legend and hover make it readable; matplotlib gets cluttered.
- The chart goes only in the deck or PDF - matplotlib is faster, smaller, and the styling is already MBB-clean.

The pluggable backend means you can flip a single chart by changing one JSON key - no code edits.
