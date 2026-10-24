# Skills Audit Checklist

Flag any section, line, or file in the target skill directory that exhibits these issues:

## Scope & Content Checks

1. **Global Rules in Skill:** Includes general project rules that apply across unrelated tasks and belong in the project's instruction files (`AGENTS.md`, `CLAUDE.md`, or their references) instead.
2. **Unresolved Runtime Discovery:** Tells the agent to figure out at runtime which platform, CLI tool, or MCP server the project uses when the project setup is already known.
3. **Standard Tool Tutorials:** Explains standard CLI flags, language syntax, or general concepts the model already knows.

## Frontmatter Checks

1. **Incomplete or Broad `description`:** States only what the skill does without stating *when* to use it (specific tasks, file types, or user phrases), or uses broad triggers (*"helps with code"*) without exclusions where overlap with another skill exists.

## Skill Body Checks

1. **Mismatched Step Structure:** Forces non-sequential rules into fake numbered steps (`Step 1`, `Step 2`), or uses unordered lists for actions that must run in a strict order.
2. **Prose Branching:** Buries conditional choices in prose paragraphs instead of using a routing table (`Condition | Action`) or `If <condition>, <do action>` rules.
3. **Prose Format Descriptions:** Describes a required output format in prose instead of providing the exact template in a fenced code block.
4. **Overloaded Steps:** Packs more than 6 rules into a single step or section instead of splitting into smaller steps or moving domain rules to `references/`.

## Scripts & References Checks

1. **Inlined Deterministic Operations:** Uses natural-language instructions for operations that have a deterministic, algorithmic outcome (such as parsing, validation, or fixed CLI sequences) instead of an executable script in `scripts/`.
2. **Unhandled Script Errors:** Bundled scripts in `scripts/` lack argument validation or crash with raw stack traces instead of printing a clear error message with a non-zero exit code.
3. **Multi-Topic Reference Files:** Mixes multiple distinct topics in a single file inside `references/` or uses a Table of Contents instead of putting each topic in its own file.
