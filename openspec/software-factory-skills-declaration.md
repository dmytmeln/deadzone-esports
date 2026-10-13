# Software Factory: Skills Declaration Catalog

**Purpose:** Canonical catalog of skill declarations required across the OpenSpec-based Software Factory. Each entry defines the interface, triggers, inputs, outputs, and human/AI pairing boundaries for skills to be implemented.

---

## 1. Problem Solving Phase

### 1.1 Universal Cognitive Meta-Loop (The Hammock Engine)

#### `socratic-problem-framing`
- **Phase:** Problem Solving $\to$ Meta-Loop (Stage 1: State the Problem & Preparation)
- **Purpose:** Conduct rigorous Socratic grilling on raw user or business requests to unmask the underlying problem, eliminate misconceptions, distinguish real problems from feature requests, and define bounded unknowns.
- **Trigger:** Upstream Phase 0 entry, or anytime a vague feature request, XY problem, or ungrounded architectural assumption is introduced.
- **Inputs:**
  - Raw user/stakeholder request, initial issue ticket, or ambiguous project objective.
  - Known system boundaries or domain context.
- **Outputs:**
  - Grounded Problem Statement (stated in plain, non-solution language).
  - Explicit Known Facts & Invariants.
  - Hard Constraints (SLA, hardware, business, compliance).
  - Open Unknowns & Critical Question Agenda.
- **Key Techniques:** Socratic Grilling, Hickey's Problem of Misconception analysis, Polya's Unknowns vs. Data separation.
- **AI vs. Human Pairing:**
  - *AI Role:* Relentless Socratic interrogator; challenges buzzwords, premature solutions, and ungrounded assumptions; reformulates problem statements.
  - *Human Role:* Intent and priority owner; articulates real business stakes and organizational constraints; signs off on the final problem statement.

---

#### `prior-art-research`
- **Phase:** Problem Solving $\to$ Meta-Loop (Stage 2: Preparation) & Cross-Cutting Architecture
- **Purpose:** Conduct deep external literature, open-source, and architectural research on similar problems; deliver comparative critiques with primary source links so humans can quickly digest prior art.
- **Trigger:** Preparation stage whenever tackling non-trivial architectures, distributed protocols, algorithmic designs, or unfamiliar domain models.
- **Inputs:**
  - Grounded Problem Statement and key target unknowns.
  - System constraints and existing technology stack.
- **Outputs:**
  - Prior Art Dossier with a comparative taxonomy table.
  - Critical analysis of each existing solution (strengths, trade-offs, documented failure modes, rationale for their design choices).
  - Curated executive summaries with direct clickable primary source links (whitepapers, engineering blogs, RFCs, GitHub repos).
- **Key Techniques:** Comparative architectural analysis, literature review, secondary-to-primary source tracing.
- **AI vs. Human Pairing:**
  - *AI Role:* Intelligence researcher; scours documentation, repositories, and technical literature; synthesizes structured dossiers with source links.
  - *Human Role:* Evaluator and learner; reads curated summaries and selected source links to load context into working memory (respecting 4–7 chunk limits).

---

#### `alternative-solution-explorer`
- **Phase:** Problem Solving $\to$ Meta-Loop (Stage 4: Illumination) & Cross-Cutting Design
- **Purpose:** Synthesize multiple ($\ge 2$) distinct, plausible candidate architectures, models, or algorithms across competing paradigms to break premature local-maxima anchoring.
- **Trigger:** Illumination stage when moving from problem understanding into candidate solution design in Architecture or Program Design.
- **Inputs:**
  - Grounded Problem Statement, facts, and constraints.
  - Prior Art Dossier.
- **Outputs:**
  - Candidate Solution A vs. Candidate Solution B proposals (radically different paradigms, e.g., Event-driven vs. Synchronous, Relational vs. Document, State-machine vs. Pure functional).
  - Paradigm comparison matrix highlighting differing assumptions, complexity profiles, and structural impacts.
- **Key Techniques:** Divergent thinking, paradigm inversion, morphological analysis.
- **AI vs. Human Pairing:**
  - *AI Role:* Collaborative ideation partner; rapidly flushes out alternative concrete models and design sketches on demand.
  - *Human Role:* Conceptual gatekeeper; spots genuine architectural simplicity, rejects superficial or cliché suggestions, and selects candidate paths to incubate.

---

#### `tradeoff-evaluator`
- **Phase:** Problem Solving $\to$ Meta-Loop (Stage 5: Verification & Trade-off Gate)
- **Purpose:** Evaluate competing candidate solutions against grounded facts and constraints, manage the Dual-Tier Trade-off Gate, and formulate the human Recall Test.
- **Trigger:** Verification stage prior to locking down architecture, product specs, or implementation plans.
- **Inputs:**
  - Competing candidate specs or throwaway spike findings.
  - Established system facts, invariants, and constraints.
- **Outputs:**
  - Side-by-Side Trade-off Decision Matrix (explicitly recording gains, losses, and residual risks for each candidate).
  - Discarded Options Log (capturing rejected paths and why they were abandoned).
  - Human Recall Test Prompt (targeted questions verifying the engineer's unprompted mental model).
  - Settled Invariants & Handoff Contract for downstream phases.
- **Key Techniques:** Dual-Tier Trade-off Gate (Spec review for standard risk; Throwaway empirical spikes for high-uncertainty risk), Hickey's Recall Verification, Multi-Criteria Decision Analysis.
- **AI vs. Human Pairing:**
  - *AI Role:* Adversarial red-teamer; checks candidate solutions against known constraints, enumerates edge cases and concurrency race paths, drafts trade-off tables.
  - *Human Role:* Must pass the Recall Test (reconstructing the design from memory without notes); makes the final subjective trade-off decision and accepts residual risks.

---

### 1.2 Tactical Problem Routes

#### `polya-synthesis-explorer`
- **Phase:** Problem Solving $\to$ Tactical Route 1 (Exploration & Synthesis)
- **Purpose:** Guide the systematic exploration of high-ambiguity domain models, novel capabilities, or mathematical/algorithmic problems using George Pólya's heuristics.
- **Trigger:** Route 1 triage triggered by high ambiguity, greenfield domains, or lack of a clear path from input data to target output.
- **Inputs:**
  - Grounded Problem Statement, target unknown entity/output, initial conditions/inputs, hard constraints.
- **Outputs:**
  - Backward Dependency Chain (tracing prerequisites backward by assuming the working end-state exists).
  - Decomposed Sub-Element Analysis (isolating the hardest core sub-problem from peripheral concerns).
  - Simplified / Toy Case Solution (minimal working model solving the isolated core element).
  - Generalized Synthesis Blueprint (scaling the toy solution back to full domain complexity).
- **Key Techniques:** Working Backward, Decomposition & Recombination, Toy Problem Reduction, Mathematical Induction / Generalization.
- **AI vs. Human Pairing:**
  - *AI Role:* Generates backward dependency graphs, formulates minimal toy problems, and writes isolated prototype logic for sub-elements.
  - *Human Role:* Verifies that the toy case addresses the genuine domain difficulty and ensures generalization back to the whole retains real-world validity.

---

#### `causal-root-cause-analyzer`
- **Phase:** Problem Solving $\to$ Tactical Route 2 (Root-Cause Diagnosis)
- **Purpose:** Drive hypothesis-driven root-cause investigation for defects, regressions, and production anomalies, preventing premature guessing and patch-work coding.
- **Trigger:** Route 2 triage triggered by observed system behavior deviating from expected system invariants.
- **Inputs:**
  - Defect description, error logs, stack traces, metrics, system telemetry.
  - Expected vs. actual system invariants.
- **Outputs:**
  - Causal Tree / Graph mapping symptom back to physical and systemic root causes.
  - Ishikawa (Fishbone) Category Diagram (Infrastructure, Algorithm, Data, Environment, Configuration).
  - Ranked Hypotheses with falsification criteria.
  - Minimal Reproduction Plan (reproduction test script or telemetry query).
- **Key Techniques:** Five Whys, Ishikawa (Fishbone) Analysis, Hypothesis-Driven Elimination, Causal Tree Mapping.
- **AI vs. Human Pairing:**
  - *AI Role:* Ingests logs and traces, maps potential causal branches across code paths, formulates testable falsification hypotheses.
  - *Human Role:* Executes reproduction tests in the real environment, verifies empirical proof, and validates the underlying root cause before approving fixes.

---

#### `toc-bottleneck-optimizer`
- **Phase:** Problem Solving $\to$ Tactical Route 3 (Bottleneck Optimization)
- **Purpose:** Execute bottleneck identification and throughput optimization using Eliyahu Goldratt's Theory of Constraints (TOC) and Amdahl's Law.
- **Trigger:** Route 3 triage triggered by resource exhaustion, latency degradation, or throughput saturation under load.
- **Inputs:**
  - Empirical profiler data (flamegraphs, allocation dumps, thread contention profiles, query execution plans).
  - System throughput/latency SLA targets.
- **Outputs:**
  - Single Identified System Constraint (the true bottleneck).
  - Five Focusing Steps Action Plan:
    1. *Exploit:* Immediate waste-elimination on the constraint.
    2. *Subordinate:* Aligning non-bottleneck workloads to pace with the constraint.
    3. *Elevate:* Structural redesign, resource scaling, or algorithm optimization to break the constraint.
  - Next Bottleneck Projection (preventing inertia).
- **Key Techniques:** Goldratt's Five Focusing Steps, Amdahl's Law, Critical Path Analysis, Resource Saturation Profiling (USE/RED methods).
- **AI vs. Human Pairing:**
  - *AI Role:* Analyzes flamegraphs and query plans, calculates mathematical constraint boundaries, proposes exploitation and subordination patterns.
  - *Human Role:* Mandates and collects empirical profiling data (forbids AI guessing bottlenecks); decides where capital and infrastructure investments are made to elevate constraints.

---

#### `triz-contradiction-resolver`
- **Phase:** Problem Solving $\to$ Tactical Route 4 (Contradiction & Dilemma Resolution)
- **Purpose:** Eliminate architectural and systemic contradictions without accepting false compromises, using Altshuller's TRIZ inventive principles.
- **Trigger:** Route 4 triage triggered when two essential system requirements directly clash (e.g., speed vs. memory, strong consistency vs. high availability) and standard trade-offs are unacceptable.
- **Inputs:**
  - Conflicting requirements and clashing system parameters.
  - Domain constraints that prevent standard compromises.
- **Outputs:**
  - Formalized Technical Contradiction (Parameter A vs. Parameter B).
  - Applicable TRIZ Separation Principles:
    - Separation in Time (e.g., event sourcing, batching vs. streaming).
    - Separation in Space (e.g., CQRS, read/write replicas, memory tiering).
    - Separation by Condition / Between Parts and Whole (e.g., federated consensus, local autonomy).
  - Non-compromising Invariant Synthesis (win-win architecture model).
- **Key Techniques:** TRIZ Contradiction Matrix, 40 Inventive Principles, Physical/Systemic Separation Principles, Dialectic Invariant Synthesis.
- **AI vs. Human Pairing:**
  - *AI Role:* Catalogs clashing parameters against TRIZ principles, generates inventive cross-domain analogies and architectural separation options.
  - *Human Role:* Assesses real-world viability, operational complexity, and domain maintainability of the proposed separation.

---

## 2. Downstream Phases (Future Declarations)

> *Note: Skills for downstream phases will be declared as each phase's workflow is formalized.*

### 2.1 Product Phase
- *(To be declared: e.g., `scope-boundary-validator`, `state-matrix-generator`, `persona-rbac-designer`)*

### 2.2 System Architecture Phase
- *(To be declared: e.g., `contract-shape-generator`, `persistence-modeler`, `concurrency-strategy-reviewer`)*

### 2.3 Program Design Phase
- *(To be declared: e.g., `pure-impure-boundary-enforcer`, `file-tree-diff-planner`, `pre-post-condition-verifier`)*

### 2.4 Operation & Review Phase
- *(To be declared: e.g., `vertical-slice-verifier`, `telemetry-contract-tester`)*
