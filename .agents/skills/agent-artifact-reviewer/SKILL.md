---
name: agent-artifact-reviewer
description: Audits agent artifacts—including AGENTS.md, Agent Skills (SKILL.md), custom rules, and reference documents—and reports rule violations with exact fixes. Use when reviewing an existing AGENTS.md, evaluating a skill, or auditing agent instructions.
---

## Universal Writing Checks

Flag any line in the target artifact (or its linked reference files) that violates these rules:
1. **Generic Platitudes:** Contains general advice (*"write clean code"*, *"handle errors gracefully"*, *"follow best practices"*) instead of a specific rule, tool, or step.
2. **Ambiguous or Hedged Sentences:** Uses hedge words (*"try to"*, *"ideally"*, *"when appropriate"*), subjective words (*"short"*, *"proper"*), or packs multiple unrelated rules into one sentence.
3. **Invented Terminology:** Uses made-up labels, buzzwords, or compound phrases where a common, standard term exists.
4. **Bare Prohibitions:** States what not to do (`"Do not <X>"` or `"Never <X>"`) without stating the allowed alternative (`"use <Y> instead"`), or attaches a verbose `"because..."` rationale to a standard rule.
5. **Aggressive Shouting:** Uses `ALL CAPS` emphasis (`MUST`, `CRITICAL`, `IMPORTANT`, `ALWAYS`) or exclamation marks instead of calm imperative sentences.

## Reference Checklists

Read the checklist that matches the target artifact:
- **Skills (`SKILL.md`):** Read [references/skills_checklist.md](references/skills_checklist.md).
- **Instructions (`AGENTS.md`, rules, reference docs):** Read [references/instructions_checklist.md](references/instructions_checklist.md).

## Audit Steps

1. **Run Deterministic Linter:**
   - For a skill: `python .agents/skills/agent-artifact-reviewer/scripts/lint_agent_config.py <path/to/skill-dir>`
   - For instructions: `python .agents/skills/agent-artifact-reviewer/scripts/lint_agent_config.py <path/to/root-instruction-file>`
2. **Evaluate Checklists:** Check the target file (and any linked reference files) against `## Universal Writing Checks` and the loaded reference checklist. Do not modify the target files during the review.
3. **Output Audit Report:** Output the report using this exact template (omit the `## Violations & Fixes` section if `Verdict` is `PASS`):

```markdown
# Audit Report: <Target>

**Verdict:** <PASS | FAIL>
**Linter:** <PASS | FAIL (list errors)>

## Violations & Fixes

| Location | Rule Violated | Current Text / Issue | Proposed Fix |
| :--- | :--- | :--- | :--- |
| `<file>:<line>` | <Rule Name> | `<quoted text or issue>` | `<exact replacement text or action>` |
```
