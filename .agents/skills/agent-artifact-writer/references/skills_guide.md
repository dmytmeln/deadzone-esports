# Agent Skills Authoring Guide & Specification

Guidance and canonical structure for authoring modular Agent Skills (`SKILL.md`).

---

## Standard Skill Directory Layout

```text
my-skill/
├── SKILL.md                 # Required: Frontmatter + core procedures
├── scripts/                 # Optional: Executable utilities (Python, Node, Bash)
├── references/              # Optional: Deep reference docs
└── assets/                  # Optional: Templates, sample payloads, fixtures
```

---

## Frontmatter Specification

```yaml
---
name: my-skill-name
description: <3rd-person description of capabilities and trigger conditions>
compatibility: <Optional: e.g. "Requires Python 3.10+ and git CLI">
license: <Optional: e.g. MIT, Apache-2.0>
---
```

### `description` (The Critical Routing Signal)
The `description` is the **only token set loaded into the agent's system prompt during discovery** (~50–100 tokens). It governs whether the skill triggers or stays dormant.

**The Two-Part Formula:**
1. **What it does:** The specific capability, transformations, and output format.
2. **When to use it:** Concrete user intents, operational contexts, and trigger keywords.

* **Third-Person Imperative:** Always use third person (*"Extracts data and generates..."*). Never use first person (*"I can help..."*) or second person (*"You should use this..."*). Inconsistent point-of-view degrades router matching.
* **Avoid Under-Triggering:** Pack high-signal domain keywords, acronyms, and common phrases users actually type.
* **Avoid Over-Triggering:** Do not use overly generic phrasing (*"Helps write clean code"*, *"Analyzes files"*), which hijacks unrelated queries.

---

## Two Core Skill Patterns

### Pattern A: Deterministic Script Runner
Use when an operation has a single correct algorithmic outcome (e.g., parsing formats, validating schemas, complex regexes, or fixed multi-flag CLI sequences).

- **Principle: "Solve, don't defer."** The script in `scripts/` must catch exceptions, handle missing parameters, and format output cleanly rather than crashing and expecting the LLM to interpret raw stack traces.
- **Context Economy:** A script on disk costs 0 context tokens until executed. Letting an agent generate script code on the fly consumes output tokens during generation and input tokens on every subsequent turn.

### Pattern B: Contextual Checklist
Use when an operation requires semantic reasoning, code design trade-offs, or qualitative evaluation (e.g., code review, API usability audit).

- Structure as step-by-step numbered phases with binary checkable criteria.
- Limit concurrent constraints in any single phase to 5–6 items to prevent instruction saturation.
