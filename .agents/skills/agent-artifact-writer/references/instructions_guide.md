# Instructions Authoring Guide

## What to Include

1. **Fix Default Agent Behavior:** Do not restate standard practices the agent already follows by default; write behavioral rules only to change a default model habit that is wrong in general or wrong for this project.
2. **Block Wrong Patterns:** Do not leave deprecated or disallowed patterns unmarked; explicitly forbid standard or legacy patterns in the codebase that are wrong for this project and state the approved pattern instead.
3. **Uninferable or High-Frequency Information Only:** Do not include project details the agent only needs occasionally and can inspect on demand; include only information the agent cannot deduce from the project files, or information it needs in most sessions and would otherwise waste turns inferring every time.

## General Instruction Rules

1. **Deterministic Checks First:** Do not write instructions in natural language for anything that can be checked deterministically; enforce it with an automated tool (such as a compiler, linter, formatter, or test) instead.
2. **Do Not Guess Human-Only Context:** Do not invent behavioral rules or guess which codebase patterns are legacy; extract only obvious high-frequency facts (such as build and test commands) and competing code patterns from the repo, and ask the user for recurring agent mistakes, deprecated patterns, and uninferable facts.
3. **Single-Hop Reference Files:** Do not link from one reference file to another, mix multiple topics in one file, or exceed 300 lines per reference file; put each topic (or sub-topic) in its own file under 300 lines and link to it directly from the root instruction file (such as `AGENTS.md`).

## Root Instruction File (AGENTS.md)

1. **Keep Under 200 Lines:** Do not inline multi-step task workflows or deep domain docs into the root instruction file; move repeatable task procedures into skills (`SKILL.md`) and domain-specific rules into linked reference files instead.
2. **Include Single-Test Command Syntax:** Do not list only full-suite test commands; place exact shell commands for build, lint, full test suite, and running a single test file or method near the top of the file.
