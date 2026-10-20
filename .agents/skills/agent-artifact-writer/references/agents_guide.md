# AGENTS.md Authoring Guide & Template

Guidance and canonical structure for authoring repository-level `AGENTS.md` files.

---

## Canonical AGENTS.md Template

```markdown
# Agent Instructions: <Project Name>

## Essential Commands

| Purpose | Command |
| :--- | :--- |
| **Run / Dev** | `<exact command to start local dev/server>` |
| **Build** | `<exact build command>` |
| **Lint & Format** | `<exact linter / formatter command>` |
| **Typecheck** | `<exact typechecker command>` |
| **Full Test Suite** | `<exact full test command>` |
| **Single Test** | `<exact single test execution syntax, e.g. pytest path/to/file.py::test_name>` |

---

## Repository Invariants

- **<Domain Area>:** Do not `<banned action or dependency>`; use `<approved alternative>` instead. [Optional: because <concise non-obvious reason>].
- **<Domain Area>:** <Specific architectural invariant or non-standard convention>.

---

## Human Approval Boundaries

Always request explicit human confirmation before performing any of the following:
- Modifying production infrastructure, environment secrets, or deployment pipelines.
- Dropping or truncating database tables/collections.
- Modifying protected files: `<list specific paths, e.g. .github/workflows/*, compose.yaml>`.

---

## Quality Gates

Before marking any task as complete or preparing a commit:
1. Verify that all modified code passes linting and typechecking cleanly.
2. Run relevant unit and integration tests and ensure 100% pass rate.
3. Show the command execution and passing output in the session.

---

## Documentation Pointers

For domain-specific architecture and contracts, consult these references rather than guessing:

| Domain | Location | Description |
| :--- | :--- | :--- |
| **Architecture** | `docs/architecture.md` | Core system design and subsystem boundaries. |
| **API Contracts** | `docs/api.md` | Endpoint definitions and payload schemas. |
| **Database** | `docs/schema.md` | Data models and entity relationships. |
```

---

## Formatting & Content Rules

1. **Size Limit:** The resulting `AGENTS.md` must be kept strictly under 200 lines (target: 40–100 lines).
2. **Commands First:** Always place the commands table near the top. Coding agents prioritize command tables to prevent trial-and-error shell failures.
3. **Negative Replacement Format:** When defining invariants, always pair the prohibition with the allowed alternative: `"Do not X; use Y instead."`
4. **No Codebase Trees:** Do not paste static directory trees or ASCII maps. Agents explore dynamic directory structures via native tools far more accurately.
5. **No Style Platitudes:** Do not include rules that can be handled by formatters or linters (tabs vs spaces, semicolons, import sorting).
6. **No Shouting:** Avoid `MUST`, `CRITICAL`, and `ALL CAPS`. Newer frontier models over-index on aggressive emphasis, which can cause erratic tool calls or false-positive refusal loops. Reserve strong wording only for irreversible invariants.
