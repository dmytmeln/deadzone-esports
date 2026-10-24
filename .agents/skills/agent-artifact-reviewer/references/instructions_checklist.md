# Instructions Audit Checklist

Flag any section or line in the target instruction file (or its linked reference files) that exhibits these issues:

## General Instruction Checks

1. **Tool-Enforceable Rules:** Contains rules in natural language that can be checked deterministically by a compiler, linter, formatter, or test.
2. **Restated Standard Practices:** Restates standard language or framework practices that the agent already follows by default, rather than fixing a flawed habit or blocking a deprecated pattern.
3. **Inferable Low-Frequency Details:** Includes project details the agent only needs occasionally and can inspect on demand (such as directory trees, file lists, or summaries of package manifests).
4. **Multi-Topic Reference Files:** Mixes multiple distinct topics in a single reference file or uses a Table of Contents inside a reference file instead of putting each topic in its own file.

## Root Instruction File Checks (`AGENTS.md` / `CLAUDE.md`)

1. **Inlined Workflows or Domain Docs:** Inlines repeatable multi-step task procedures (which belong in a `SKILL.md`) or domain-specific rules (which belong in linked reference files) directly inside the root instruction file.
2. **Missing Exact Commands or Single-Test Syntax:** If the repository has build, lint, or test tools, omits the exact shell commands near the top of the root file or omits the syntax to run a single test file or method.
