---
name: explain
description: Explains functions, methods, classes, algorithms, and code logic using concrete real-world input/output examples, calling context, tiered visual schematics, execution traces, side-effects, and failure modes. Use when the user asks "explain how does function X work", "how does this method work", "explain this code", "walk me through this function", "what does this code do", "how does X work under the hood", or requests an explanation of any programming mechanism or codebase symbol.
---

# Code & Programming Explainer

Explains any code component - whether a function in the local codebase, a third-party library API, an algorithm, or a language feature - with maximum clarity and zero fluff. Every explanation is grounded in real calling context, realistic input/output examples, and structural schematics.

---

## Scope & Tool Routing

- **Codebase Functions & Classes:** When explaining code within the workspace:
  - In indexed repositories (`.codegraph/` exists), use `codegraph_explore` or `codegraph explore "<symbol>"` to inspect callers, callees, and symbol source.
  - In other repositories, use `ast-grep --lang <lang> -p '<pattern>'` to locate definitions and call sites before reading files.
  - Link all referenced symbols and files with clickable links using forward slashes (e.g. `[ClassName](file:///path/to/file.ext#L10-L25)`).
- **General Programming Concepts & Algorithms:** When explaining general language constructs, standard libraries, or algorithms not in the repository, explain conceptually using the exact same 7-part template with realistic production scenarios.

---

## Visual Presentation Tiers

Select the lightest tier that produces a clean visual:

| Tier | When to Use | Output Destination |
|---|---|---|
| **Tier 1: Inline ASCII** (Default) | Linear flows, compact state transitions, caller-to-callee handoffs, or pipelines with $\le 7$ nodes | Inline in chat inside a `text` code block |
| **Tier 2: Mermaid Markdown File** | Complex branching, recursive call trees, bidirectional loops, or $> 7$ nodes | Write to `./explain/explain-{symbol-name}.md` and provide a clickable link |

*Rules for Visuals:*
- Never dump raw Mermaid syntax inline into terminal chat. Tier 2 Mermaid must always be written to a `./explain/*.md` file.
- Node labels must be hybrid: clean names with short qualifiers in parentheses (e.g. `Validate Token (JWT signature)`).

---

## The 7-Part Explanation Template

Every code explanation must strictly follow this exact 7-part sequence:

### 1. Core Concept & Mental Model
- State in 1–2 sentences what the component accomplishes, why it exists, and its primary responsibility.
- Provide a Tier 1 ASCII schematic (or link to a Tier 2 Mermaid file in `./explain/`) illustrating the core data or control flow.

### 2. Signature & Contract
- Provide the full function or class signature with explicit parameter and return types.
- **Preconditions:** What requirements must hold true before a function starts.
- **Postconditions:** What conditions must be true after a function finishes.
- **Invariants:** What conditions must stay true during the life of a component.

### 3. Calling Context & Motivation
- Explain *where*, *when*, and *why* this component is called in real-world systems.
- Include a realistic call-site code snippet demonstrating how an actual caller invokes it (e.g. an HTTP route handler, background worker, or lifecycle hook).

### 4. Concrete Input / Output Examples
- **No placeholder values:** Never use `foo`, `bar`, `test`, `temp`, or meaningless integers like `123` unless strictly numeric.
- **Happy Path:** Provide a realistic input payload and the exact corresponding return value.
- **Failure Path:** Provide an invalid or edge-case input payload and the resulting error, exception, or rejection return.

### 5. Execution Trace (Logic Walkthrough)
- Break down the internal execution into an ordered numbered list.
- Highlight key branch decisions, loops, and helper invocations.
- In workspace code, reference exact line ranges with clickable markdown links for each key step.

### 6. Side Effects & State Mutations
List every side effect produced outside the local call frame.
*If pure:* Explicitly state *"Pure function: No side effects or state mutations."*

### 7. Failure Modes & Edge Cases
- List concrete exceptions thrown, error codes returned, or rejection promises.
- Document edge cases (e.g. empty lists, concurrent invocation races, timeout scenarios, boundary overflows) and how the caller is expected to handle them.

---

## Authoring Invariants

1. **Concrete Over Abstract:** Use production-grade domain values (e.g. user IDs, UUIDs, ISO timestamps, realistic JWT strings, database entity names) in all examples.
2. **Deterministic Context Gathering:** Never guess or hallucinate a function's behavior. Read the full source file, identify call sites, and inspect imported helpers before drafting the explanation.
3. **Instruction Economy:** Keep text direct, sharp, and focused on causal mechanics. Omit polite filler, conversational preamble, and generic conclusions.
