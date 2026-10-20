---
name: agent-artifact-reviewer
description: Audits and grades repository AGENTS.md files and Agent Skills (SKILL.md) against context engineering quality checklists. Use when reviewing an existing AGENTS.md, evaluating a skill before merging, or running a comprehensive repository agent configuration audit.
---

# Agent Artifact Reviewer

Deterministic and qualitative auditor for repository instructions (`AGENTS.md`) and Agent Skills (`SKILL.md`).

---

## Operating Protocol

1. **Deterministic Verification First:** Always execute `python scripts/lint_agent_config.py <target>` before qualitative scoring. Any deterministic failure (e.g. file too long, invalid regex, missing TOC) is recorded immediately.
2. **Progressive Disclosure:**
   - If reviewing `AGENTS.md` $\to$ Read `references/agents_rubric.md` (Items A1–A16).
   - If reviewing a skill $\to$ Read `references/skills_rubric.md` (Items S1–S15).
3. **Objective Scoring Only:** Score each criterion strictly on a 0–2 scale:
   - `2` = Fully compliant (all requirements met with evidence).
   - `1` = Partially compliant (partially present or ambiguous).
   - `0` = Non-compliant (absent, violating, or anti-pattern).

---

## Workflow

### Step 1: Identify Target Scope
Determine the target specified by the user:
- **Single File / Skill:** E.g., `AGENTS.md` or `.agents/skills/<name>`.
- **Full Repository (`all`):** Finds root `AGENTS.md` and all skill directories inside `.agents/skills/` (and `.claude/skills/` if present) to audit the entire repository in a batch.

### Step 2: Execute Deterministic Linter
Run:
```bash
python scripts/lint_agent_config.py <target_path>
```
Record any deterministic syntax, regex, or sizing errors.

### Step 3: Qualitative Checklist Evaluation
Read the corresponding reference rubric (`references/agents_rubric.md` or `references/skills_rubric.md`). Inspect the target file and evaluate every item.

### Step 4: Calculate Verdict (Gated Tiering)
Compute the total score percentage: $\frac{\text{Sum of earned points}}{\text{Total possible points}} \times 100\%$.

Determine the verdict:
- **PASS:** Overall score $\ge 85\%$ **AND** $100\%$ on all Must-Have ($\bigstar$) items (all $\bigstar$ items scored 2/2).
- **NEEDS WORK:** Overall score is $70\% - 84\%$, **OR** any Must-Have ($\bigstar$) item scored partial (1/2).
- **FAIL:** Overall score $< 70\%$, **OR** any Must-Have ($\bigstar$) item scored zero (0/2).

### Step 5: Generate the Audit Report
Output the report using the following structure:

```markdown
# Agent Configuration Audit: <Target Name>

**Verdict:** <PASS | NEEDS WORK | FAIL>  
**Score:** <Earned Points> / <Max Points> (<Percentage>%)  
**Deterministic Linter:** <PASS | FAIL (list errors)>

---

## Scorecard

| Item | Status | Score | Finding |
| :--- | :---: | :---: | :--- |
| **A1 ★ Exact Commands** | ✅ | 2/2 | Build, lint, full test, and single test commands present. |
| **A2 ★ Mistake Test** | ⚠️ | 1/2 | Contains boilerplate framework overview that could be pruned. |
| ... | ❌ | 0/2 | ... |

---

## Priority Improvements

1. **[Critical / Must-Have]** <Specific actionable change needed to unblock a PASS verdict>
2. **[Improvement]** <Actionable suggestion for partial or failed items>
```
