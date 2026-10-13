# Software Factory

## Research 

---

## Problem Solving

- What do you know? (facts, context, constraints)
- Understand the unknown: Distinguish sharply between the unknown, the data given, and the condition/constraints. "the unknown" is the exact output or target entity that the problem asks you to produce
- Find related problems. Probably you are not the only one dealing with this kind of problem and probably there is a solution to similiar problem. Try to find it, analyze it.
- Get a lot of input, you can't connect things you don't know. Read around your space
- Work backward: Assume the solution exists and trace the necessary prerequisites backwards to the starting conditions.
- Decompose and recombine: Isolate the difficult sub-element, solve a simplified or specialized case, then generalize back to the whole.
- Be critical about the solution, especially your own one.
- What are solution tradeoffs? In order to have tradeoff - there must be at least two solutions and you have to figure out what is good and bad about those solutions.
- You MUST have questions. You can't know everything.
- Focus! Go away from computer and try to focus on the problem
- Use waking mind for critical thinking - analysis, criticising, tactics. Cons: prone to finding local maxima; use background mind for making connections, strategy, abstractions, synthesis
- In order to use complex non-trivial problems - sleep!
- We can't hold more than 4-7 items in our head. Focus shift so you have covered all the space but at any given point you had only 4-7 items in head.
- 4-stage creative process: Preparation (loading data into working memory), Incubation (letting subconscious associations form without conscious strain), Illumination (the "aha!" moment), and Verification (rigorous checking).
- Return back to the solution - try to find gaps, alternative / better approaches.
- Five Whys & Causal Trees
- Ishikawa (Fishbone) Analysis
- Theory of Constraints & Bottleneck Analysis: The Five Focusing Steps: 1) Identify the system's constraint; 2) Exploit the constraint (ensure it works at 100% efficiency with no waste); 
3) Subordinate everything else to the constraint (align all non-bottleneck activities to serve the bottleneck); 4) Elevate the constraint (invest resources to break through it); 5) Repeat (prevent inertia; the bottleneck will move)
- Contradiction elimination: Most bad designs compromise (e.g., make it stronger, but it becomes heavier). TRIZ demands you eliminate the contradiction entirely (make it stronger and lighter)

---

## Product Phase

**Definition:** Translating raw user problems and business objectives into unambiguous functional boundaries and expected behavioral states.  
**Purpose:** Prevent AI scope creep and misalignment before any architectural or code-level decision is made.

- **What:** The functional scope, boundaries, and tangible deliverable. Prevents agents from building adjacent, unrequested features.
- **Why:** The business rationale and user motivation. Provides the intent agents need when encountering ambiguity during implementation.
- **Acceptance Criteria (AC):** Verifiable conditions that mark the feature complete. Usually best written in strict Given/When/Then format so agents can generate test cases directly from them.
- HTML mocks: Lightweight, layout-accurate representations of UI states
- Explicit Non-Goals ("Out of Scope")
- Edge Case & State Matrix
- User Persona & RBAC Permissions Matrix: Explicitly declare who can trigger what action (e.g., Admin vs Member vs Guest), preventing retrofitting permission checks later.

---

## System Architecture

**Definition:** Defining the macro-level boundaries, communication contracts, persistence models, and data lifecycles across external services, APIs, and datastores.  
**Purpose:** Ensure strict modular decoupling, idempotent state changes, and schema invariants across system boundaries.

- In this phase we align on how the services, endpoints, schemas, queues, and stores talk to each other
- Sequence diagram
- Contract / endpoint shapes: Exact OpenAPI / JSON Schema for inputs, payloads, headers, query params, and status codes.
- Data models and transformations: Entity-relationship schemas, primary/foreign keys, indices, and pipeline mapping functions (input DTO $\to$ domain entity $\to$ storage model).
- Failure Modes & Fallback Strategies
- Idempotency & Concurrency Strategy
- Observability & Telemetry Signatures

---

## Program Design

**Definition:** Translating architecture into local codebase reality: modular organization, in-memory execution paths, state transformations, and static types.  
**Purpose:** Anchor the agent's edits to exact file paths and internal signatures, eliminating context drift and file-system collisions.

- Call-stack trees for any orchestration or control-flow change
- File-tree diffs - so you can stay in touch with the layout of your codebase and where stuff lives
- Types and method signatures for the key new functions
- Pure Functions vs. Side-Effect Separation: Distinguish pure domain logic (business math, validation, transforms) from impure operations (I/O, database writes, clock checks).
- Define preconditions and postconditions for each function

---

## Vertical Slices Instead of Horizontal Slices

- Don't build the whole feature in once - split it up into smaller vertical pieces
- Vaguely: Slicing by "Behavioral Scenarios" - Instead of splitting the stack into slices, split the feature's user journeys into vertical slices where each slice is complete end-to-end (Database $\to$ Backend $\to$ UI).

---

## Operation Phase

---

## Review Phase

