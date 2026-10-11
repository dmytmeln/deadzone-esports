# `deadzone-esports` — Architecture & Implementation Blueprint

> **A PUBG Esports Tournament Engine & Telemetry Analyzer**  
> Built with **Spring Boot (Java 27)** + **React (Vite/TypeScript)**  
> Architectural Patterns: **Hexagonal Architecture (Ports & Adapters)** + **Functional Core, Imperative Shell (FCIS)**

---

## 1. Executive Summary & Philosophy

`deadzone-esports` is a tournament management, statistics calculation, and 2D match replay platform inspired by [Twire.gg](https://twire.gg).

* **Functional Core**: 100% pure Java 27 (`record`s, pure functions, sealed types). Zero Spring, zero JPA, zero network/disk I/O, zero mocks needed in tests.
* **Imperative Shell**: The outer application orchestration that loads data via inbound ports, invokes the functional core, persists results via outbound ports, and coordinates side effects.
* **Hexagonal Architecture**: Enforced at the compiler level using a multi-project Gradle build (`:domain`, `:application`, and `:infrastructure` inside `backend/`).

---

## 2. System Architecture

```
                                  HEXAGONAL ARCHITECTURE
                                  
   DRIVING / INBOUND ADAPTERS                        DRIVEN / OUTBOUND ADAPTERS
   
  ┌─────────────────────────┐                       ┌─────────────────────────┐
  │   React UI (REST API)   │                       │  PostgreSQL (Docker)    │
  │   - Standings Dashboard │                       │  - Spring Data JPA      │
  │   - 2D SVG Replay Map   │                       │  - Entity <-> Record    │
  └───────────┬─────────────┘                       └───────────▲─────────────┘
              │                                                 │
              ▼                                                 │
  ┌─────────────────────────┐                       ┌───────────┴─────────────┐
  │   FileUploadController  │                       │ TournamentRepositoryPort│
  │   - Drag & Drop JSON    │                       │ MatchRepositoryPort     │
  └───────────┬─────────────┘                       └───────────▲─────────────┘
              │                                                 │
              ▼                                                 │
    ┌───────────────────────────────────────────────────────────┴───────┐
    │                      APPLICATION LAYER (Shell)                    │
    │  - IngestMatchUseCase                                             │
    │  - CalculateTournamentStandingsUseCase                            │
    │  - GetMatchReplayUseCase                                          │
    │                                                                   │
    │            ┌─────────────────────────────────────────┐            │
    │            │          FUNCTIONAL CORE (Pure)         │            │
    │            │  * SUPER Rule Engine & Tie-Breakers     │            │
    │            │  * Telemetry Stream Reducer             │            │
    │            │  * Zone Phase & Damage Invariants       │            │
    │            │  * Immutable Java 27 Records            │            │
    │            └─────────────────────────────────────────┘            │
    └───────────────────────────────────────────────────────────────────┘
              ▲                                                 ▲
              │                                                 │
  ┌───────────┴─────────────┐                       ┌───────────┴─────────────┐
  │ BundledFixtureLoader    │                       │ [Future] Krafton API    │
  │ (3-5 PGC Pro Matches)   │                       │ Live Match Poller / WS  │
  └─────────────────────────┘                       └─────────────────────────┘
```

---

## 3. Module Structure (Monorepo Layout)

```
deadzone-esports/
├── backend/                         # JAVA 27 / GRADLE BACKEND
│   ├── build.gradle (or .kts)       # Root backend build config & dependency management
│   ├── settings.gradle (or .kts)    # Includes ':domain', ':application', ':infrastructure'
│   │
│   ├── domain/                      # 1. FUNCTIONAL CORE: Pure Java 27 (Zero Spring, Zero JPA, Zero I/O)
│   │   └── src/
│   │       ├── main/java/com/deadzone/domain/
│   │       │   ├── model/           # Immutable records: Team, Player, Match, TelemetryEvent
│   │       │   ├── rules/           # Pure functions: SuperRuleEngine, TieBreakerSolver, SmashRuleEngine
│   │       │   └── telemetry/       # Pure reducers: MatchEventReducer, CirclePhaseCalculator
│   │       └── test/java/           # Ultra-fast unit tests (Zero Spring context, zero mocks)
│   │
│   ├── application/                 # 2. IMPERATIVE SHELL: Use-Case Orchestration & Transaction Boundaries
│   │   └── src/
│   │       ├── main/java/com/deadzone/application/
│   │       │   ├── port/in/         # Inbound interfaces (Use Cases: IngestMatchUseCase, etc.)
│   │       │   ├── port/out/        # Outbound interfaces (SPI: TournamentRepositoryPort, etc.)
│   │       │   └── service/         # Orchestrators (@Service, @Transactional, TransactionTemplate)
│   │       └── test/java/           # Service orchestration tests (Zero Spring context, fast stubs)
│   │
│   └── infrastructure/              # 3. ADAPTERS & RUNTIME: Spring Boot Application, Web, JPA, Security
│       └── src/
│           ├── main/java/com/deadzone/infra/
│           │   ├── DeadzoneApplication.java # Spring Boot entry point
│           │   ├── adapter/in/web/          # REST Controllers (Upload, Standings, Replay)
│           │   ├── adapter/out/jpa/         # JPA Entities, Mappers, Spring Data Repositories
│           │   ├── adapter/out/fixture/     # Bundled JSON loader
│           │   └── config/                  # SecurityConfig, WebConfig, OpenAPIConfig
│           └── test/java/                   # Integration tests (Testcontainers + PostgreSQL)
│
└── frontend/                        # REACT (Vite + TypeScript + Tailwind CSS)
    └── src/
        ├── components/
        │   ├── leaderboard/          # SUPER Standings Table with tie-break tooltips
        │   ├── replay/               # 2D SVG Map, Phase Timeline Slider, Kill Feed
        │   └── upload/               # Match JSON Drag-and-Drop dropzone
        └── api/                      # Fetch client for backend REST API
```

---

## 4. The Functional Core: Domain Models & Rules

### 4.1 S.U.P.E.R. Point System (Official Rules)
* **Kill Points**: 1 point per confirmed kill.
* **Placement Points**:
  * 1st: 10 pts
  * 2nd: 6 pts
  * 3rd: 5 pts
  * 4th: 4 pts
  * 5th: 3 pts
  * 6th: 2 pts
  * 7th: 1 pt
  * 8th: 1 pt
  * 9th–16th: 0 pts
* **Tie-Breaker Hierarchy (Strict Order — Official S.U.P.E.R.)**:
  1. Total accumulated Placement Points across all matches in the series.
  2. Total Match Points (Placement + Kills) scored in the most recent match.
  3. Placement position in the most recent match.
  4. Total damage dealt in the most recent match.

### 4.2 Core Invariants & Reducers
* **Telemetry Event Reducer**: A pure function folding raw timestamped telemetry events into a clean `MatchReplayState`:
  $$\text{fold}(\text{InitialState}, [\text{Event}_1, \text{Event}_2, \dots]) \longrightarrow \text{MatchReplay}$$
* **Coordinates**: Normalized PUBG game units ($0 \dots 816{,}000$ cm for $8\times 8$ km maps).

---

## 5. Non-Functional Requirements & Technical Constraints

All technical constraints previously tracked across requirements are formalized here:

* **NFR-1 (Compiler-Enforced Hexagonal Architecture)**:
  * Strict compile-time DAG: `:infrastructure` $\longrightarrow$ `:application` $\longrightarrow$ `:domain`.
  * `:domain` module contains zero Spring, zero JPA, and zero network/filesystem dependencies.
  * `:application` module manages orchestration, use-case workflows, and transaction boundaries (`@Service`, `TransactionTemplate`) without polluting domain models.
  * All domain models (`Tournament`, `Stage`, `Match`, `Team`, `Player`, `MatchReplay`) are immutable Java 27 `record`s.
  * All scoring rules, tie-breaker solvers, and telemetry stream reducers are 100% pure functions.
* **NFR-2 (Performance Targets)**:
  * Telemetry ingestion and reduction of a 40MB file (`telemetry.json` / `.json.gz`): $\le 3.0$ seconds via Jackson Streaming [`FR-3.3`].
  * Standings, Team Stats, and Player Stats REST response latency: $\le 100$ms under normal load [`FR-4.4`, `FR-5.1`, `FR-6.1`].
  * 2D Replay canvas rendering: $\ge 60$ FPS in modern browsers [`FR-8.1` - `FR-8.8`].
* **NFR-3 (Data Storage & Migration)**:
  * Relational persistence via PostgreSQL 16+ using Spring Data JPA.
  * Database schema and DDL managed strictly via Liquibase migrations (`src/main/resources/db/changelog`).

---

## 6. Implementation Roadmap & Traceability

### Phase 1: Functional Core & Scoring Rules (`:domain`)
1. Define immutable domain models: `Team`, `Player`, `MatchResult`, `TeamMatchScore`.
2. Implement pure `SuperRuleEngine` and `TieBreakerSolver` [`FR-4.1`, `FR-4.2`].
3. Implement `SmashRuleEngine` with threshold tracking and win condition [`FR-4.3`].
4. Write comprehensive, data-driven JUnit 5 tests modeling real PGC tie-break situations (zero mocks).

### Phase 2: Telemetry Parser & Stream Reducer (`:domain`)
1. Define raw telemetry records (`PlayerKnocked`, `PlayerKilled`, `DamageDealt`, `CircleShrunk`).
2. Build pure `MatchEventReducer` to stream and extract [`FR-3.2`, `FR-3.3`]:
   * Team eliminations and final placements.
   * Circle phases (White safe zone & Blue zone coordinates + radius).
   * Kill vectors (killer location, victim location, weapon name, knocks).

### Phase 3: Application Use Cases & Infrastructure Adapters (`:application` & `:infrastructure`)
1. Define Inbound/Outbound ports (`TournamentRepositoryPort`, `MatchTelemetryPort`).
2. Configure PostgreSQL via Docker Compose (`docker-compose.yml`) with Liquibase migrations.
3. Build Spring Data JPA adapter with clean `Domain Record <-> JPA Entity` mappers.
4. Implement `BundledFixtureAdapter` (loading 3 pre-packaged PGC Grand Finals matches) [`FR-3.5`].
5. Implement REST endpoints per [`docs/api-specification.md`](file:///D:/MyProjects/Java/deadzone-esports/docs/api-specification.md).

### Phase 4: React UI & 2D SVG Map (`frontend`)
1. Setup Vite + React + TypeScript + Tailwind CSS using design tokens from [`docs/ui-ux-specification.md`](file:///D:/MyProjects/Java/deadzone-esports/docs/ui-ux-specification.md).
2. Build Tournament Discovery Hub & Stages Roadmap [`FR-1.1`, `FR-1.2`, `FR-2.3`].
3. Build Leaderboard Component with projected vs locked cut-offs and rank deltas [`FR-4.4` - `FR-4.6`].
4. Build Team & Player Stats tables and Player Drill-Down Modal with Teammate Switcher [`FR-5.1` - `FR-6.3`].
5. Build 2D Interactive Replay with synchronized kill feed, timeline slider, and pulse beacons [`FR-8.1` - `FR-8.8`].

### Phase 5 (Future Milestone): Live Mode
* Add a `KraftonApiClient` outbound adapter and a scheduled poller.
* Add Spring WebSockets / SSE for live leaderboard pushes.

