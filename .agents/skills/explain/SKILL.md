---
name: explain
description: Explains functions, methods, classes, algorithms, and code logic using concrete real-world input/output examples, calling context, tiered visual schematics, execution traces, side-effects, and failure modes. Use when the user asks "explain how does function X work", "how does this method work", "explain this code", "walk me through this function", "what does this code do", "how does X work under the hood", or requests an explanation of any software component or programming mechanism.
---

## Goal

Explain any software component using ASD-STE100 principles through a structured 7-part breakdown (mental model, contract, calling context, concrete I/O, execution trace, side effects, and failure modes) accompanied by a visual schematic.

---

## Constraints

1. **ASD-STE100 Compliance:** Write strictly according to ASD-STE100.
2. **Factual Grounding:** For workspace code, inspect caller and callee context and read the exact implementation before drafting the explanation; never guess behavior.
3. **Concrete Domain Data:** Never use synthetic placeholders (`foo`, `bar`, `test`, `temp`, or dummy numbers); all inputs, outputs, and call examples must use realistic domain values.
4. **Template Integrity:** Follow the 7-part breakdown in exact sequence without omitting sections.
5. **Visual Placement:** Render Tier 1 ASCII directly in chat; write Tier 2 Mermaid exclusively to `./explain/explain-{software-component-name}.md` with a clickable markdown link.
6. **Forward-Slash File Links:** Link all referenced workspace files and software components using clickable markdown links with forward slashes (`file:///path/to/file.ext#L10-L20`).

---

## Scope

- **Workspace Code:** Functions, methods, classes, and interfaces declared in the repository.
- **External APIs & Algorithms:** Third-party libraries, runtime APIs, language features, and standalone algorithms. Must follow the identical 7-part template using realistic production scenarios.

---

## Visual Presentation Tiers

Select the lightest tier that produces a clean visual:

| Tier | When to Use | Output Destination |
|---|---|---|
| **Tier 1: Inline ASCII** (Default) | Linear flows, compact state transitions, caller-to-callee handoffs, or pipelines with $\le 7$ nodes | Inline in chat inside a `text` code block |
| **Tier 2: Mermaid Markdown File** | Complex branching, recursive call trees, bidirectional loops, or $> 7$ nodes | Write to `./explain/explain-{software-component-name}.md` and provide a clickable link |

*Rules for Visuals:*
- Never dump raw Mermaid syntax inline into terminal chat. Tier 2 Mermaid must always be written to a `./explain/*.md` file.
- Node labels must be hybrid: clean names with short qualifiers in parentheses (e.g. `Validate Token (JWT signature)`).

---

## The 7-Part Explanation Template

Every code explanation must strictly follow this exact 7-part sequence:

### 1. Core Concept & Mental Model
- State the primary responsibility of the component in 1–2 sentences.
- Provide a schematic (Tier 1 ASCII inline or Tier 2 Mermaid link) showing data or control flow.

### 2. Signature & Contract
- Provide the complete declaration signature with explicit parameter and return types.
- State preconditions, postconditions, and invariants.

### 3. Calling Context & Motivation
- Explain where, when, and why this component is called in a real-world scenario.
- Provide a realistic call-site snippet showing caller invocation.

### 4. Concrete Input / Output Examples
- **Happy path:** Realistic input payload and the exact corresponding return value.
- **Failure path:** Invalid or edge-case input payload and the resulting error, exception, or return value.

### 5. Execution Trace
- Present the sequential execution flow as an ordered list.
- Identify key branch decisions, loops, and helper invocations.
- For workspace code, link each step to its source line range.

### 6. Side Effects & State Mutations
- List all state mutations and external side effects (I/O, database, network, shared memory).
- If none, explicitly state: "No side effects or state mutations."

### 7. Failure Modes & Edge Cases
- List specific exceptions thrown, error codes, and failure return values.
- Document boundary edge cases and expected caller handling.
