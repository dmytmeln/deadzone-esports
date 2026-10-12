Product Phase
Definition: Translating raw user problems and business objectives into unambiguous functional boundaries and expected behavioral states.
Purpose: Prevent AI scope creep and misalignment before any architectural or code-level decision is made.

- What: The functional scope, boundaries, and tangible deliverable.
Prevents agents from building adjacent, unrequested features.
- Why: The business rationale and user motivation.
Provides the intent agents need when encountering ambiguity during implementation.
- Acceptance Criteria (AC): Verifiable conditions that mark the feature complete.
 Usually best written in strict Given/When/Then format so agents can generate test cases directly from them.
- HTML mocks: Lightweight, layout-accurate representations of UI states
- Explicit Non-Goals ("Out of Scope")
- Edge Case & State Matrix
- User Persona & RBAC Permissions Matrix: Explicitly declare who can trigger what action (e.g., Admin vs Member vs Guest),
 preventing retrofitting permission checks later.

System Architecture:
Definition: Defining the macro-level boundaries, communication contracts, persistence models, and data lifecycles across external services, APIs, and datastores.
Purpose: Ensure strict modular decoupling, idempotent state changes, and schema invariants across system boundaries.

- In this phase we align on how the services, endpoints, schemas, queues, and stores talk to each other
- Sequence diagram
- Contract / endpoint shapes: Exact OpenAPI / JSON Schema for inputs, payloads, headers, query params, and status codes.
- Data models and transformations: Entity-relationship schemas, primary/foreign keys, indices, and pipeline mapping functions
 (input DTO $\to$ domain entity $\to$ storage model).
 - Failure Modes & Fallback Strategies
 - Idempotency & Concurrency Strategy
 - Observability & Telemetry Signatures

Program design:
Definition: Translating architecture into local codebase reality: modular organization, in-memory execution paths, state transformations, and static types.
Purpose: Anchor the agent's edits to exact file paths and internal signatures, eliminating context drift and file-system collisions.

- Call-stack trees for any orchestration or control-flow change
- File-tree diffs - so you can stay in touch with the layout of your codebase and where stuff lives
- Types and method signatures for the key new functions
- Pure Functions vs. Side-Effect Separation: Distinguish pure domain logic (business math, validation, transforms) from impure operations (I/O, database writes, clock checks).
- Define preconditions and postconditions for each function

Vertical slices instead of horizontal slices:

- Don't build the whole feature in once - split it up into smaller vertical pieces
- Vaguely: Slicing by "Behavioral Scenarios"Instead of splitting the stack into slices, split the feature's user 
journeys into vertical slices where each slice is complete end-to-end (Database $\to$ Backend $\to$ UI).

Operation Phase

Review Phase