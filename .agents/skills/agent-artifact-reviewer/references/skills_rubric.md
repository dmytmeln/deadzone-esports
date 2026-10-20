# Agent Skills Audit Rubric (S1–S15)

Scoring guide for evaluating modular Agent Skills (`SKILL.md` and associated directories).

---

## Scoring Scale
- **2 (Pass):** Fully compliant. Clear evidence present in the skill package.
- **1 (Partial):** Partially compliant or ambiguous. Room for improvement.
- **0 (Fail):** Absent, violating, or exhibits known anti-patterns.
- **★ Must-Have Items:** S1, S2, S3, S4. If any ★ item scores below 2, the overall verdict cannot be PASS.

---

## Checklist Rubric

### S1 ★ Valid Name & Directory Slug
*(Mechanical validation enforced by `lint_agent_config.py`: length $\le 64$, lowercase/hyphen regex, matching directory slug).*
- **2:** Deterministic linter passes. Name clearly conveys the skill's primary domain.
- **1:** Passes linter, but name is vague or generic.
- **0:** Deterministic linter fails.

### S2 ★ Description & Trigger Quality
*(Length $\le 1,024$ chars and XML stripping enforced by `lint_agent_config.py`).*
- **2:** Description clearly answers both *what the skill does* and *when to use it*, packing concrete trigger keywords, user phrases, or file types.
- **1:** Describes what it does, but lacks explicit trigger conditions (*when to use it*).
- **0:** Missing description, or uses an over-broad platitude (*"helps with code"*).

### S3 ★ Procedural Justification
- **2:** Justified as an episodic, multi-step workflow or specialized capability needed for only a subset of tasks.
- **1:** Borderline: provides procedural structure, but could arguably be handled by a simple script or universal rule.
- **0:** Unjustified: packs universal rules that belong in root `AGENTS.md`, or duplicates basic LLM training priors.

### S4 ★ Evaluated Against Baseline / Clear Gap
- **2:** Built to solve an observed, documented agent failure or structured workflow gap. Has verifiable success criteria or evaluation scenarios.
- **1:** Has plausible utility, but lacks concrete test scenarios or clear baseline evaluation.
- **0:** Speculative manual documenting hypothetical capabilities without testing.

### S5 Third-Person Phrasing & Calm Routing
*(First/second person prefix check enforced by `lint_agent_config.py`).*
- **2:** Written strictly in third person (*"Extracts data and..."*). Avoids aggressive shouting (*"CRITICAL"*, *"YOU MUST ALWAYS USE THIS"*).
- **1:** Third person, but includes pushy phrasing.
- **0:** Written in first person (*"I can help you..."*) or second person (*"You should use this..."*).

### S6 Body Conciseness & Signal
*(Body ceiling $\le 500$ lines enforced by `lint_agent_config.py`).*
- **2:** Instructions are compact, high-signal, and free of token-wasting filler (target: 50–250 lines).
- **1:** Between 250 and 500 lines, but organized cleanly.
- **0:** Exceeds 500 lines (deterministic linter failure), or padded with conversational fluff.

### S7 Reference Quality & Structure
*(Single-level depth and TOC for files >200 lines enforced by `lint_agent_config.py`).*
- **2:** Reference files are tightly focused, directly linked from `SKILL.md`, and contain clear navigation headers.
- **1:** References pass deterministic checks, but text is slightly unfocused.
- **0:** Deterministic linter fails (nested references or missing TOC on files >200 lines).

### S8 Focused Modular Scope
- **2:** Focused on a tight, cohesive domain (1–3 related workflows). Avoids exhaustive documentation dumping.
- **1:** Covers a slightly broad domain, but maintains clear subsection boundaries.
- **0:** Sprawling encyclopedia attempting to cover dozens of unrelated tools or procedures in one skill.

### S9 Determinism vs. Judgment Separation
- **2:** Mechanical, sequence-critical, or data parsing steps are offloaded to executable scripts in `scripts/`. Contextual judgment steps are structured as checklists.
- **1:** Relies primarily on prompt prose for steps that would be more reliably handled by a deterministic script.
- **0:** Asks the LLM to perform complex mathematical, binary parsing, or deterministic tasks probabilistically on the fly.

### S10 Script Reliability ("Solve, Don't Defer")
- **2:** Bundled scripts in `scripts/` handle errors, check arguments, and exit cleanly with informative messages. (Score 2 if no scripts required).
- **1:** Scripts exist but have minimal error handling or crash with raw unhandled exceptions.
- **0:** Scripts are broken, missing dependencies, or unexecutable.

### S11 Constraint Density
- **2:** Step-by-step instructions limit simultaneous active constraints to 5–6 items per phase, avoiding instruction saturation.
- **1:** 7–9 concurrent rules in a single step, creating moderate risk of constraint drops.
- **0:** Dumps dozens of simultaneous rules into a single step, causing adherence collapse.

### S12 Trigger Isolation (Positive & Negative Cases)
- **2:** Clearly defined positive trigger examples and adjacent negative trigger examples (cases that must *not* activate the skill).
- **1:** Positive trigger cases are clear, but negative boundary cases are implied.
- **0:** High risk of applicability poisoning; description triggers on generic, unrelated queries.

### S13 Model Adaptability
- **2:** Instructions are calibrated: provides enough structure for smaller models without over-constraining frontier reasoning models.
- **1:** Slightly biased toward one model tier, but functions across frontier models.
- **0:** Fails on smaller models due to missing steps, or completely deadlocks reasoning models with rigid contradictions.

### S14 Hand-Curated & Pruned
- **2:** Cleanly authored, edited, and verified by an engineer. Zero raw unreviewed LLM boilerplate.
- **1:** Minor boilerplate remnants, but mostly customized and clean.
- **0:** Unedited auto-generated `/init` dump or raw LLM stream with verbose apologies/chatter.

### S15 Environment & Compatibility
*(Unix forward slashes in links enforced by `lint_agent_config.py`).*
- **2:** Clearly documents OS, binary CLI, or runtime prerequisites in `compatibility` frontmatter.
- **1:** Passes linter, but omits dependency requirements in frontmatter.
- **0:** Contains Windows backslashes (`\`) in paths, breaking across containerized or Unix agent environments.
