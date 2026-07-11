# Structured Audit Handoff Package

Use this package to hand off a consistent repo audit to another tool.

## 1) Audit Objective

- **Goal:** Evaluate current-state architecture, strengths, risks, tech debt, and roadmap gaps.
- **Scope:** Deployed portfolio RAG system only.
- **Out of scope:** Legacy SaaS artifacts in `docs/archive/` and `legacy/*`.

## 2) Required Read Order (exact)

Read these files in this order:

1. `/home/runner/work/portfolio-ai/portfolio-ai/README.md`
2. `/home/runner/work/portfolio-ai/portfolio-ai/CLAUDE.md`
3. `/home/runner/work/portfolio-ai/portfolio-ai/DEPLOYMENT.md`
4. `/home/runner/work/portfolio-ai/portfolio-ai/OPERATIONS.md`
5. `/home/runner/work/portfolio-ai/portfolio-ai/cloud/api-proxy.py`
6. `/home/runner/work/portfolio-ai/portfolio-ai/cloud/guardrails.py`
7. `/home/runner/work/portfolio-ai/portfolio-ai/eval/golden_set.yaml`
8. `/home/runner/work/portfolio-ai/portfolio-ai/scripts/eval_graded.py`
9. `/home/runner/work/portfolio-ai/portfolio-ai/red-lines.md`
10. `/home/runner/work/portfolio-ai/portfolio-ai/invariants.md` *(flag legacy SaaS sections as historical and non-running-system context)*

## 3) Required Outputs (5)

Return all five sections:

1. **What this system is / is not** (current production truth)
2. **What is working well** (architecture, reliability, retrieval quality, ops discipline)
3. **What should be improved** (ranked by impact/risk)
4. **What should be rewritten or retired** (docs drift, legacy SaaS leftovers, weak spots)
5. **What still needs planning/building** (next 30/60/90 priorities)

## 4) Evidence and Reporting Rules

For every finding:

- Include **severity** and **confidence**.
- Include exact **file path + line reference(s)**.
- Label each claim as:
  - **Proven by code/docs**, or
  - **Assumption/speculation**.
- Distinguish:
  - **Production issue**, or
  - **Documentation-only issue**.

## 5) Evaluation Lenses

Evaluate through these lenses:

- Architecture correctness vs stated design
- Retrieval quality and grounding reliability
- Security/privacy guardrails (especially no content logging)
- Operability (deploy gating, monitoring, fail-open behavior)
- Documentation alignment with reality

## 6) Immediate Focus Checks

Confirm or refute:

- Legacy SaaS language still present in `red-lines.md` and `invariants.md`
- Drift between historical docs and deployed architecture details
- Whether tests/eval cover highest-risk failure modes
- Whether roadmap/plans are clearly separated from shipped behavior

## 7) Decision-Ready Summary Format

End with four decision lists:

- **Keep** (do not change)
- **Fix now** (small high-value updates)
- **Plan next** (larger roadmap items)
- **Do not do** (changes that would regress proven behavior)
