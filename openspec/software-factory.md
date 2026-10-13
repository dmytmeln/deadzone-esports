# Software Factory

## Research 

---

## Problem Solving

**Definition:** A disciplined cognitive and tactical protocol for understanding root issues, exploring solution spaces, and validating invariants before writing specs or code.  
**Purpose:** Prevent problems of misconception, avoid building premature features, and systematically resolve hard engineering roadblocks across the lifecycle.  
**Lifecycle Invocation:** Operates in dual-mode:
- *Phase 0 (Upstream Entry):* Executed prior to the Product Phase for new initiatives to anchor the problem space and prove viability before drafting user stories or specs.
- *On-Demand Sub-routine (Downstream Callback):* Invoked dynamically from downstream phases (Architecture, Design, Operation) whenever an engineer or agent hits an architectural impasse, conflicting constraints, or unknown failure modes.

### 1. The Universal Cognitive Meta-Loop (The Hammock Engine)

*A cross-cutting cognitive operating system operating fractally across all factory phases (Problem Solving, System Architecture, Program Design, and Operation).*

Universal cognitive stages that govern all non-trivial thinking, regardless of problem type:

1. **State the Problem:**
   - Explicitly articulate the problem out loud or in writing before proposing solutions.
   - Focus on root user/system problems, not requested "features" (features are attributes, not the objective).
   - Distinguish problems of misconception from mere implementation defects.

2. **Preparation (Loading Working Memory):**
   - **Facts & Context:** Ground the problem in known system realities, architecture, and historical context.
   - **Constraints:** Explicitly capture hard limits (hardware, SLAs, latency, business rules).
   - **Unknowns & Questions:** Differentiate sharply between what is given, what is missing, and what is target output. You *must* have open questions.
   - **Prior Art Analysis & Critique:** Read around the space; study existing solutions to similar problems. Critically analyze their designs, strengths, trade-offs, and failure modes to understand why they made those choices before starting from scratch.
   - **Externalize & Chunk (4–7 Items):** Human working memory caps at 4–7 items. Shift focus sequentially across bounded sub-spaces, externalizing notes and informal diagrams (avoid bureaucratic UML).

3. **Incubation (Feeding the Background Mind):**
   - Step away from the computer. Detach from keyboard-driven trial-and-error.
   - Leverage the background mind for holistic connections, cross-domain synthesis, and global strategy.
   - Sleep on complex, non-trivial problems to allow subconscious associations to form without strain.
   - **Human/AI Boundary:** Incubation is strictly human biological detachment; AI does not participate and must complete all retrieval and candidate preparation beforehand.

4. **Illumination (Candidate Synthesis):**
   - Capture candidate solutions and "aha!" insights without rushing into immediate implementation.

5. **Verification & Critical Skepticism (The Waking Mind):**
   - **Verification Against Facts:** Rigorously verify proposed candidate solutions directly against the grounded facts, constraints, and invariants established during Preparation.
   - **System-Specific Evaluation:** Focus critical analysis on solutions tailored to this system's problem context, picking candidate designs apart to expose hidden assumptions.
   - **Recall Test:** Step away and attempt to reconstruct the core solution from memory. Unrecalled areas expose gaps in understanding.
   - **Dual-Tier Trade-off Gate:**
     - In order to have a trade-off, there must be at least two distinct candidate solutions.
     - *Tier 1 (Design Review):* Structured comparative evaluation of alternatives (gains, losses, residual risks) for standard-complexity tasks.
     - *Tier 2 (Empirical Spikes):* Throwaway prototype / spike experiments for high-uncertainty or performance-critical unknowns before committing to production.

---

### 2. Route Triage Rubric

When facing a roadblock, classify the symptom to enter the appropriate tactical route:

| Symptom / Challenge | Tactical Route | Core Objective |
| :--- | :--- | :--- |
| High ambiguity, greenfield capability, or unknown domain model | **Route 1: Exploration & Synthesis** | Discover the unknown and compose viable models |
| Observed behavior deviates from expected system invariants | **Route 2: Root-Cause Diagnosis** | Trace backwards to find fundamental causal origins |
| Resource saturation, throughput degradation, or latency bottleneck | **Route 3: Bottleneck Optimization** | Maximize system throughput via constraint elevation |
| Mutually conflicting requirements where standard trade-offs are unacceptable | **Route 4: Contradiction Resolution** | Eliminate architectural compromises without penalty |

---

### 3. Tactical Problem Routes

#### Route 1: Exploration & Synthesis (Pólya Heuristics)
- **Target Unknowns:** Clarify the exact target entity/output that the problem asks to produce.
- **Work Backward:** Assume the solution already exists; trace the necessary prerequisites backwards to starting conditions.
- **Decompose and Recombine:** Isolate the hardest sub-element, solve a simplified/specialized case, then generalize back to the whole.
- **Analogous Systems:** Find and adapt patterns from related problems already solved elsewhere.

#### Route 2: Root-Cause Diagnosis (Causal Analysis)
- **Five Whys & Causal Trees:** Iteratively ask "Why?" to drill through immediate symptoms to underlying structural and organizational causes.
- **Ishikawa (Fishbone) Analysis:** Systematically categorize potential causes across system dimensions (Machine/Infrastructure, Method/Algorithm, Data/Payload, Environment, Human/Config).

#### Route 3: Bottleneck Optimization (Theory of Constraints)
- **Goldratt's Five Focusing Steps:**
  1. *Identify* the system's single constraint (the true bottleneck).
  2. *Exploit* the constraint (ensure it works at 100% capacity with zero waste).
  3. *Subordinate* everything else (align all non-bottleneck processes to strictly pace with the constraint).
  4. *Elevate* the constraint (invest resources/hardware/optimizations to break through it).
  5. *Repeat* (prevent organizational inertia; locate the next bottleneck).

#### Route 4: Contradiction & Dilemma Resolution (TRIZ & Dialectic)
- **Contradiction Elimination:** Reject false compromises (e.g., "to make it stronger, we must accept it being heavier"). Use TRIZ inventive principles to eliminate the contradiction entirely (achieve strength *without* weight penalty).
- **Invariant Synthesis:** Reframe competing architectural demands (e.g., strong consistency vs. high availability) into higher-level invariants or domain partitioning.

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

