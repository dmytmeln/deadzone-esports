---
name: agent-artifact-writer
description: Scaffolds, authors, and refines repository-level AGENTS.md files and modular Agent Skills (SKILL.md) using an interactive grill-me interview or by updating rules from observed agent mistakes. Use when creating a new AGENTS.md, authoring a new skill, converting a recurring workflow into a skill, or adding rules after an agent error.
---

# Agent Artifact Writer

Interactive authoring assistant for repository instructions (`AGENTS.md`) and procedural capability packages (`SKILL.md`).

---

## Core Invariants

1. **Determinism First:** If a rule can be enforced deterministically (by a compiler, linter, formatter, typechecker, or hook), enforce it there rather than in English instructions.
2. **Non-Inferable Only:** Include only what an agent cannot deduce by inspecting codebase files, package manifests, or directory layouts.
3. **Concrete Verifiability:** Every rule, skill procedure, or quality gate must have an explicit, testable verification check or command.
4. **Ban Generic Platitudes:** Forbid general advice (*"write clean code"*, *"handle errors gracefully"*). Standard priors already exist; platitudes consume attention budget without altering behavior.

---

## Workflow Modes

Identify the user's intent:
- **Mode 1: Create New Artifact (AGENTS.md or Skill)** $\to$ Proceed to Section 1.
- **Mode 2: Update Artifact from Mistake or Feedback** $\to$ Proceed to Section 2.

---

### Section 1: Create New Artifact

Conduct a `/grill-me` style interview with recommended answers based on repository analysis.

#### Branch A: Creating `AGENTS.md`
Read `references/agents_guide.md` for structure and templates. Walk through this grilling sequence:

1. **Commands:** Ask for exact terminal commands for:
   - Development / run server
   - Build command
   - Lint & typecheck commands
   - Full test suite execution
   - Single test file / test method syntax
2. **Project Invariants:** Identify project-specific deviations from standard conventions or banned patterns (formatted as: *"Do not use X; use Y instead"*).
3. **Human Approval Boundaries:** Identify high-risk or irreversible actions that require explicit human confirmation before execution (e.g. dropping database tables, publishing packages, modifying protected production configs).
4. **Quality Gates:** Define mandatory prerequisites before concluding tasks or pushing code (e.g. all unit tests pass, zero type errors).
5. **Documentation Reference Table:** Map domain-specific areas to local Markdown docs (e.g. `docs/architecture.md`, `docs/api.md`) instead of inlining long text.
6. **Deterministic Verification:** Write the file and run `python scripts/lint_agent_config.py AGENTS.md`.

#### Branch B: Creating a `SKILL.md`
Read `references/skills_guide.md` for schema, templates, and script guidelines. Walk through this grilling sequence:

1. **Workflow / Task Scope:** What recurring task or multi-step workflow does this skill automate?
2. **Determinism vs. Judgment:**
   - *Deterministic Operations:* Offload data extraction, file parsing, regex manipulation, or fixed CLI commands to an executable script in `scripts/`. Scripts handle error conditions internally ("solve, don't defer").
   - *Contextual Judgment:* Structure steps that require architectural reasoning, subjective evaluation, or code review as clear Markdown checklists.
3. **Routing Frontmatter:**
   - `description`: Written strictly in third person. Must specify *what the skill does* and *when to use it*, packing high-signal trigger keywords.
4. **Deterministic Verification:** Write `.agents/skills/<name>/SKILL.md` and run `python scripts/lint_agent_config.py .agents/skills/<name>/SKILL.md`.
5. **Subagent Dry-Run Verification:**
   - Launch a test subagent with a positive trigger query. Inspect the subagent's execution trace/transcript to verify that it loaded or executed the target skill `<name>` (or called its bundled scripts).
   - If the skill is designed to produce or modify specific files, assert that the output files exist and match expected schemas.
   - Launch a test subagent with an adjacent negative query to verify it does not touch or invoke the skill `<name>`.
   - **Notice:** Inform the user: *"Depending on your agent CLI harness, you may need to restart your session for the new skill to be indexed in the system prompt."*

---

### Section 2: Update Artifact from Mistake or Feedback

When the user wants to update `AGENTS.md` or an existing skill after an agent error or PR comment:

1. **Two-Strike Check:**
   - Is this an isolated stochastic glitch or prompt ambiguity? (Strike 1 $\to$ resolve in-session; do not modify persistent rules).
   - Is it a recurring failure or project-specific trap? (Strike 2 $\to$ add a permanent rule).
2. **Deterministic Triage:**
   - If the mistake can be caught by a compiler, linter, formatter, typechecker, or hook, configure that tool. Do not write a prompt rule.
3. **Rule Formulation:**
   - Format strictly as a **Negative Replacement**: `"Do not <mistake>; use <correct pattern> instead."`
   - **The Non-Obvious Test:** Attach a concise *"because..."* rationale *only* if the rule overrides standard industry practices or introduces an unusual local quirk. If the invariant is standard or obvious, omit the rationale to conserve token budget.
4. **Verification:** Apply the edit and run `python scripts/lint_agent_config.py <target-file>`.
