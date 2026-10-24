# Skills Authoring Guide

## What to Include

1. **Task-Specific Scope Only:** Do not put general project rules that apply across unrelated tasks into a skill; put general rules into the project's instruction files (such as `AGENTS.md`, `CLAUDE.md`, or their reference files), and include in `SKILL.md` only what is needed for that specific task.
2. **Pre-Resolve Environment and Tool Choices:** Do not write a skill that tells the agent to check at runtime which platform, CLI tool, or MCP server the project uses; inspect the project while writing the skill and specify the exact tool and command to run.
3. **Omit Standard Tool Tutorials:** Do not explain standard CLI flags, language syntax, or general concepts the model already knows; include only the specific commands, arguments, and rules required for the workflow.

## Frontmatter Rules

1. **State What It Does and When to Use It:** Do not write only what the skill does or use broad descriptions (*"helps with code"*); state in `description` both the exact capability and the specific tasks, file types, or user phrases that should trigger it (and state what *not* to use it for if it overlaps with another skill).
2. **Third-Person Verbs:** Do not write `description` in first person (*"I can..."*) or second person (*"You can..."*, *"Use this to..."*); start with third-person verbs (*"Writes..."*, *"Explains..."*) instead.

## How to Write the Skill Body

1. **Sequence Only What Is Sequential:** Do not force non-sequential rules into fake numbered steps; use numbered steps (`Step 1`, `Step 2`) only when actions must run in a strict order, and use constraint lists when order does not matter.
2. **Use Tables or `If/Then` for Branching:** Do not bury conditional choices in prose paragraphs; use a routing table (`Condition | Action`) or `If <condition>, <do action>` rules when the agent must choose between paths.
3. **Show Templates Instead of Describing Formats:** Do not describe a required output format in prose; provide the exact template in a fenced code block instead.
4. **Cap Rules Per Step:** Do not pack more than 6 rules into a single step or section; split complex procedures into smaller steps or move detailed domain rules to `references/`.

## Scripts and References

1. **Offload Deterministic Work to `scripts/`:** Do not write natural-language instructions for operations that have a deterministic, algorithmic outcome (such as parsing, validation, or fixed CLI sequences); put an executable script in `scripts/` and instruct the agent to run it instead.
2. **Handle Errors Inside Scripts:** Do not let bundled scripts crash with raw stack traces or silently ignore bad inputs; validate arguments, catch errors, and print a clear error message with a non-zero exit code instead.
3. **Keep `SKILL.md` Under 500 Lines:** Do not inline long domain guides or branch-specific checklists that bloat `SKILL.md` past 500 lines; move them into `references/` and load them only when needed.
4. **Single-Hop Reference Files:** Do not link from one reference file to another, mix multiple topics in one file, or exceed 300 lines per reference file; put each topic in its own file under 300 lines inside `references/` and link to it directly from `SKILL.md`.
