# `deadzone-esports` — Architecture & Implementation Blueprint

> **A PUBG Esports Tournament Engine & Telemetry Analyzer**  
> Built with **Spring Boot (Java 27)** + **React (Vite/TypeScript)**  
> Architectural Patterns: **Hexagonal Architecture (Ports & Adapters)** + **Functional Core, Imperative Shell (FCIS)**

---

## 1. Executive Summary & Philosophy

`deadzone-esports` is a tournament management, statistics calculation, and 2D match replay platform inspired by [Twire.gg](https://twire.gg).

* **Functional Core**: 100% pure Java 27 (`record`s, pure functions, sealed types). Zero Spring, zero JPA, zero network/disk I/O, zero mocks needed in tests.
* **Imperative Shell**: The outer application orchestration that loads data via inbound ports, invokes the functional core, persists results via outbound ports, and coordinates side effects.
* **Hexagonal Architecture**: Enforced at the compiler level using a multi-project Gradle build (`:core` and `:infrastructure` inside `backend/`).

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
│   ├── settings.gradle (or .kts)    # Includes ':core' and ':infrastructure'
│   │
│   ├── core/                        # PURE JAVA 27. ZERO DEPENDENCIES (Zero Spring, Zero JPA)
│   │   └── src/
│   │       ├── main/java/com/deadzone/core/
│   │       │   ├── domain/          # Pure Functional Core
│   │       │   │   ├── model/       # Immutable records: Team, Player, Match, TelemetryEvent
│   │       │   │   ├── rules/       # Pure functions: SuperRuleEngine, TieBreakerSolver
│   │       │   │   └── telemetry/   # Pure reducer: MatchEventReducer, CirclePhaseCalculator
│   │       │   └── application/     # Imperative Shell / Orchestration
│   │       │       ├── port/in/     # Inbound interfaces (Use Cases: IngestMatchUseCase, etc.)
│   │       │       ├── port/out/    # Outbound interfaces (SPI: TournamentRepositoryPort, etc.)
│   │       │       └── service/     # Pure use-case orchestrators (100% free of Spring annotations)
│   │       └── test/java/           # Fast unit tests (Zero Spring context, zero mocks)
│   │
│   └── infrastructure/              # ADAPTERS & RUNTIME (Spring Boot, Web, JPA, Security)
│       └── src/
│           ├── main/java/com/deadzone/infra/
│           │   ├── adapter/in/web/       # REST Controllers (Upload, Standings, Replay)
│           │   ├── adapter/out/jpa/      # JPA Entities, Mappers, Spring Data Repositories
│           │   ├── adapter/out/fixture/  # Bundled JSON loader
│           │   └── config/               # Spring @Configuration & @Bean wiring for Core services
│           └── test/java/                # Integration tests (Testcontainers + PostgreSQL)
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
* **Tie-Breaker Hierarchy (Strict Order)**:
  1. Total accumulated Kill Points across all matches.
  2. Best single match Total Points (Placement + Kills).
  3. Best single match Kill Points.
  4. Kill Points scored in the most recent match.
  5. Placement position in the most recent match.

### 4.2 Core Invariants & Reducers
* **Telemetry Event Reducer**: A pure function folding raw timestamped telemetry events into a clean `MatchReplayState`:
  $$\text{fold}(\text{InitialState}, [\text{Event}_1, \text{Event}_2, \dots]) \longrightarrow \text{MatchReplay}$$
* **Coordinates**: Normalized PUBG game units ($0 \dots 816{,}000$ cm for $8\times 8$ km maps).

---

## 5. Implementation Roadmap

### Phase 1: Functional Core & SUPER Engine (`:core:domain`)
1. Define immutable domain models: `Team`, `Player`, `MatchResult`, `TeamMatchScore`.
2. Implement pure `SuperRuleEngine` and `TieBreakerSolver`.
3. Write comprehensive, data-driven JUnit 5 tests modeling real PGC tie-break situations (zero mocks).

### Phase 2: Telemetry Parser & Stream Reducer (`:core:domain`)
1. Define raw telemetry records (`PlayerKnocked`, `PlayerKilled`, `DamageDealt`, `CircleShrunk`).
2. Build pure `MatchEventReducer` to extract:
   * Team eliminations and final placements.
   * Circle phases (White safe zone & Blue zone coordinates + radius).
   * Kill vectors (killer location, victim location, weapon name).

### Phase 3: Application Use Cases & Infrastructure Adapters (`:core:application` & `:infrastructure`)
1. Define Inbound/Outbound ports (`TournamentRepositoryPort`, `MatchTelemetryPort`).
2. Configure PostgreSQL via Docker Compose (`docker-compose.yml`).
3. Build Spring Data JPA adapter with clean `Domain Record <-> JPA Entity` mappers.
4. Implement `BundledFixtureAdapter` (loading 3 pre-configured PGC Grand Finals matches).
5. Build REST endpoints:
   * `POST /api/matches/upload` (Upload telemetry JSON).
   * `GET /api/tournaments/{id}/standings` (Calculated SUPER leaderboard).
   * `GET /api/matches/{id}/replay` (2D circle phases & kill events).

### Phase 4: React UI & 2D SVG Map (`frontend`)
1. Setup Vite + React + TypeScript + Tailwind CSS.
2. Build **SUPER Leaderboard Component**:
   * Rank, Team Name, Matches Played, Kill Points, Placement Points, Total Points.
   * Tie-breaker indicators and breakdown.
3. Build **2D Interactive Replay Component**:
   * Erangel / Miramar map image background.
   * Scaled `<svg viewBox="0 0 816000 816000">`.
   * Circles (`<circle>` for White and Blue zones).
   * Kill markers (`<line>` and death icons with hover tooltips).
   * Phase slider (Phase 1 through Phase 8) to scrub through match progression.

### Phase 5 (Future Milestone): Live Mode
* Add a `KraftonApiClient` outbound adapter and a scheduled poller.
* Add Spring WebSockets / SSE for live leaderboard pushes.
