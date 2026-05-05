# Ontology: {{topic}}
*{{client}} | analyst-depth concept map | {{date}}*

This file goes deeper than the brief. It is the working knowledge graph: how the
key concepts connect, what each one means precisely, and what we don't yet know.

## Concept map

```mermaid
graph TD
    A[{{root_concept}}] --> B[{{branch1}}]
    A --> C[{{branch2}}]
    A --> D[{{branch3}}]
    B --> B1[{{leaf1a}}]
    B --> B2[{{leaf1b}}]
    C --> C1[{{leaf2a}}]
    C --> C2[{{leaf2b}}]
    D --> D1[{{leaf3a}}]
    D --> D2[{{leaf3b}}]
    B1 -.->|drives| C1
    C2 -.->|enables| D1
```

## Glossary

| Term | Definition | Why it matters here |
|---|---|---|
| {{term1}} | {{def1}} | {{why1}} |
| {{term2}} | {{def2}} | {{why2}} |
| {{term3}} | {{def3}} | {{why3}} |
| {{term4}} | {{def4}} | {{why4}} |
| {{term5}} | {{def5}} | {{why5}} |
| {{term6}} | {{def6}} | {{why6}} |

## Relationships

| From | -> | To | Mechanism | Strength | Source |
|---|---|---|---|---|---|
| {{rel1_from}} | {{rel1_verb}} | {{rel1_to}} | {{rel1_mech}} | {{rel1_strength}} | [{{rel1_src}}] |
| {{rel2_from}} | {{rel2_verb}} | {{rel2_to}} | {{rel2_mech}} | {{rel2_strength}} | [{{rel2_src}}] |
| {{rel3_from}} | {{rel3_verb}} | {{rel3_to}} | {{rel3_mech}} | {{rel3_strength}} | [{{rel3_src}}] |
| {{rel4_from}} | {{rel4_verb}} | {{rel4_to}} | {{rel4_mech}} | {{rel4_strength}} | [{{rel4_src}}] |

Strength scale: **strong** (causal & quantified), **moderate** (correlated, plausible mechanism), **weak** (anecdotal / single-source).

## Key debates / disagreements in the literature
- **{{debate1_topic}}** - {{debate1_camp_a}} vs. {{debate1_camp_b}}. {{debate1_resolution_or_open}}
- **{{debate2_topic}}** - {{debate2_camp_a}} vs. {{debate2_camp_b}}. {{debate2_resolution_or_open}}

## Open questions
1. {{open_q1}}
2. {{open_q2}}
3. {{open_q3}}
4. {{open_q4}}

## Adjacent topics worth a future pass
- {{adjacent1}}
- {{adjacent2}}
- {{adjacent3}}

---

*This ontology was synthesized from `sources/feynman/` plus verifier-cleared cross-references. Each numbered citation maps to a `.provenance.md` entry in that folder.*
