---
name: agent-artifact-writer
description: Writes and updates agent artifacts, including AGENTS.md, Agent Skills (SKILL.md), custom rules, subagent prompts, and reference documents. Use when creating or editing AGENTS.md, authoring or updating a skill, drafting agent rules, or adding instructions after an agent mistake.
---

## Goal

Increase agent success rate and efficiency across two types of artifacts:
- **Skills (`SKILL.md`):** Narrow the agent's execution path for a specific task so it follows a fixed, repeatable procedure instead of wasting turns and tokens figuring out tools, environments, or steps from scratch.
- **Instructions (`AGENTS.md`, rules, reference docs):** Correct flawed default behavior and provide information the agent cannot infer from its context or would otherwise have to rediscover in every session.

## Universal Writing Rules

1. **No Generic Platitudes:** Do not write general advice (*"write clean code"*, *"handle errors gracefully"*, *"follow best practices"*); state the specific rule, tool, or step that changes what the agent does by default.
2. **Single-Meaning Sentences:** Do not use hedge words (*"try to"*, *"ideally"*, *"when appropriate"*) or subjective words (*"short"*, *"proper"*); write one rule per sentence using a direct verb (or `If <condition>, <do action>`) with exact commands, paths, or limits.
3. **Standard Terminology:** Do not invent custom labels, buzzwords, or compound phrases; use common, established terms instead.
4. **Negative Replacement:** Do not write bare prohibitions; pair every prohibition with the allowed alternative (`"Do not <X>; use <Y> instead"`), and add a `"because..."` reason only when overriding standard practice.
5. **Calm Tone:** Do not use `ALL CAPS`, exclamation marks, or repeated `MUST` / `CRITICAL` emphasis; use plain imperative sentences instead.

## Reference Guides

Read the guide that matches the target artifact before writing:
- **Skills (`SKILL.md`):** Read [references/skills_guide.md](references/skills_guide.md).
- **Instructions (`AGENTS.md`, rules, reference docs):** Read [references/instructions_guide.md](references/instructions_guide.md).
