# AGENTS.md Audit Rubric (A1–A16)

Scoring guide for evaluating repository-level `AGENTS.md` files.

---

## Scoring Scale
- **2 (Pass):** Fully compliant. Clear evidence present in the file.
- **1 (Partial):** Partially compliant or ambiguous. Room for improvement.
- **0 (Fail):** Absent, violating, or exhibits known anti-patterns.
- **★ Must-Have Items:** A1, A2, A3, A4. If any ★ item scores below 2, the overall verdict cannot be PASS.

---

## Checklist Rubric

### A1 ★ Exact Commands
- **2:** Lists exact, runnable shell commands for build, lint/typecheck, full test suite, and the specific syntax to run a *single test* file or test method.
- **1:** Commands are listed, but single-test syntax is missing, or commands rely on placeholders without examples.
- **0:** Missing build/test commands, or tells the agent to "run tests" without specifying the CLI tool.

### A2 ★ The Mistake Test
- **2:** Every line addresses an observed, non-trivial requirement. Zero filler or generic documentation.
- **1:** Mostly relevant, but contains a few lines that could be pruned without risk of agent error.
- **0:** Packed with speculative instructions, generic advice, or obvious statements.

### A3 ★ No Inferable Information
- **2:** Zero directory trees, file layout diagrams, or descriptions of standard framework features.
- **1:** Contains a brief layout summary that is mostly harmless but redundant with filesystem exploration tools.
- **0:** Contains a large ASCII directory tree or extensive summaries of package manifests that the agent can read directly.

### A4 ★ No Linter / Formatter Duplication
- **2:** Zero rules about indentation, semicolons, import sorting, or formatting. Relies purely on deterministic linters and formatters.
- **1:** Mentions formatting standards in natural language, but directs the agent to run the linter.
- **0:** English instructions prescribing code style (e.g. "use 2 spaces", "never use semicolons", "sort imports alphabetically").

### A5 Negative Replacement Formatting
- **2:** Behavioral guardrails are phrased as explicit negative replacements: *"Do not X; use Y instead."*
- **1:** Rules specify what not to do, but omit the permitted alternative, leaving the solution space ambiguous.
- **0:** Rules are framed as bare, open-ended prohibitions without direction.

### A6 No Generic Platitudes
- **2:** Zero vague advice (*"write clean code"*, *"handle errors gracefully"*, *"follow best practices"*).
- **1:** Contains 1–2 minor platitudes within otherwise specific sections.
- **0:** Heavily padded with generic software engineering platitudes.

### A7 Size & Token Budget
- **2:** File is under 100 lines (ultra-lean).
- **1:** File is between 101 and 200 lines, but organized cleanly.
- **0:** Exceeds 200 lines (triggers instruction fatigue and context bloat).

### A8 Separation of Procedural Workflows
- **2:** Procedural, multi-step workflows are offloaded to skills (`.agents/skills/`); path-specific rules are offloaded to nested directory files.
- **1:** Contains a long multi-step procedure that is only relevant occasionally, but otherwise well-structured.
- **0:** Inlines multi-step operational runbooks directly into root `AGENTS.md`.

### A9 Documentation Pointers
- **2:** Uses a compact reference table or file links pointing to `docs/` for deep architecture/APIs instead of inlining text.
- **1:** Links to docs exist but are scattered informally in prose.
- **0:** Pastes large markdown documentation or API specs directly into `AGENTS.md`.

### A10 Human Approval Boundaries
- **2:** Explicitly lists high-risk or irreversible actions requiring human confirmation (e.g. dropping tables, modifying deployment pipelines, modifying protected configs).
- **1:** Mentions asking for approval generally, but lacks a specific list of protected actions or paths.
- **0:** No safety boundaries defined.

### A11 Security & Performance Guardrails
- **2:** Contains explicit, project-relevant security or performance constraints (e.g. secret handling, rate limit boundaries, query limits).
- **1:** Mentions security in passing without concrete constraints.
- **0:** Completely omits non-functional security and performance guardrails.

### A12 Concise Rationales for Non-Obvious Rules
- **2:** Rules that override standard conventions include a concise *"because..."* clause; standard idioms remain terse imperatives.
- **1:** Explanations are present but slightly verbose, or a non-obvious rule lacks an explanation.
- **0:** Explanations attached to completely obvious rules, or complex quirks left unexplained.

### A13 Calm Emphasis (No Shouting)
- **2:** Uses calm, declarative phrasing. Avoids ALL CAPS, exclamation points, and repeated `MUST` / `CRITICAL` keywords.
- **1:** Contains occasional `MUST` or `ALWAYS`, but without aggressive shouting.
- **0:** Heavy use of ALL CAPS, exclamation points, or penalty threats.

### A14 Single Source of Truth & Precedence
- **2:** Clean, un-duplicated configuration; no contradictory rules across files or tools.
- **1:** Minor overlap with tool-specific files (e.g. `CLAUDE.md`), but directives align.
- **0:** Conflicting directives between root and nested files or parallel tool configs.

### A15 Git Versioned & Maintained
- **2:** File is tracked in version control and shows evidence of intentional curation alongside code changes.
- **1:** Version controlled, but appears unmaintained or contains slightly dated command syntax.
- **0:** Untracked or abandoned file.

### A16 Quality Gates / Definition of Done
- **2:** Explicit quality gates defined before completing tasks (e.g. tests pass, lint clean, typecheck green).
- **1:** Mentions running tests before finishing, but lacks full quality gate criteria.
- **0:** No verification or completion criteria specified.
