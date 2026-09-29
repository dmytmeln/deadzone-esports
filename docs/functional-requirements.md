# `deadzone-esports` — Functional Requirements Specification (FRS)

> **Document Version**: 1.1.0  
> **Status**: Approved via Architectural Alignment  
> **Target Release**: MVP  
> **Reference Architecture**: [`docs/deadzone-esports-architecture.md`](file:///D:/MyProjects/Java/deadzone-esports/docs/deadzone-esports-architecture.md)  
> **UI/UX Reference Mockup**: [`docs/ui-mockup.html`](file:///D:/MyProjects/Java/deadzone-esports/docs/ui-mockup.html)

---

## 1. Executive Summary & Purpose

`deadzone-esports` is a dedicated PUBG Esports tournament engine, statistics calculation platform, and 2D match replay viewer inspired by [Twire.gg](https://twire.gg).

The system accepts official Krafton PUBG telemetry files (`telemetry.json` / `.json.gz`), processes them via a pure Java 27 Functional Core (FCIS + Hexagonal Architecture), persists the normalized state in PostgreSQL, and delivers:
1. **Tournament Stages Roadmap & Hub** (Visual overview of stage progression with `LIVE`, `COMPLETED`, and `UPCOMING` stage status tracking).
2. **Official Tournament Standings with Qualification Cut-Offs** (Standard S.U.P.E.R. & EWC Smash Rule, with visual cut-off lines and badges for teams advancing, dropping, or eliminated).
3. **Comprehensive Player Statistics** (Kills, Damage, Knocks, Headshots, Survival Time, and Match Breakdown).
4. **Interactive 2D Replay Map** (Full continuous timeline scrubbing, circle shrink animations, player movement vectors, and a synchronized interactive Kill Feed sidebar).

---

## 2. User Personas & Permissions

| Persona | Role | Capabilities |
| :--- | :--- | :--- |
| **Spectator / Analyst** | Public (Unauthenticated) | • View tournament stages roadmap and stage progression.<br>• View tournament leaderboards with cut-off lines and status badges.<br>• Search, filter, and sort player statistics.<br>• Open player drill-down performance cards.<br>• Play, pause, scrub, and inspect 2D match replays with the kill feed. |
| **Tournament Organizer / Admin** | Protected (Authenticated) | • Create and configure Tournaments, Stages, and Progression Cut-Off rules.<br>• Configure Stage Rosters and Lobby Slot Mappings (Slots 1–16).<br>• Select scoring rulesets (Standard S.U.P.E.R. vs. EWC Smash Rule).<br>• Upload and ingest match telemetry files.<br>• Load bundled fixture matches. |

---

## 3. Domain Model & Competition Hierarchy

The platform strictly implements a three-tier competition structure:

```
┌───────────────────────────────────────────────────────────────────────────┐
│                        TOURNAMENT (e.g. PGC 2024)                         │
│                                                                           │
│  STAGES ROADMAP HUB:                                                      │
│  ┌───────────────────────┐       ┌───────────────────────┐                │
│  │   STAGE 1: Group      │       │   STAGE 4: Finals     │                │
│  │   Status: COMPLETED   │ ───►  │   Status: LIVE NOW    │                │
│  │   Cut-offs: Top 8/Bot8│       │   Cut-offs: Champion  │                │
│  └───────────┬───────────┘       └───────────┬───────────┘                │
└──────────────┼───────────────────────────────┼────────────────────────────┘
               ▼                               ▼
      ┌─────────────────┐             ┌─────────────────┐
      │ Match 1 (Erangel)│             │ Match 1 (Erangel)│
      │ Match 2 (Miramar)│             │ Match 2 (Taego)  │
      │ ... Match 18     │             │ ... Match 18     │
      └─────────────────┘             └─────────────────┘
```

### 3.1 Domain Entities & Invariants
* **`Tournament`**: Overarching competition (e.g., *PUBG Global Championship 2024*, *Esports World Cup 2024*). Holds metadata: title, dates, location, prize pool, logo, and ordered stages.
* **`Stage`**: Discrete tournament phase (e.g., *Group Stage*, *Winners Bracket*, *Last Chance*, *Grand Finals*).
  * **`StageStatus`**: Lifecycle state enum (`UPCOMING`, `ONGOING`, `LIVE`, `COMPLETED`).
  * **`ScoringRule`**: Ruleset configuration (`SUPER_STANDARD` or `SMASH_RULE` with point threshold).
  * **`StageRoster`**: Maps custom match lobby slots (1–16) to official Team profiles.
  * **`ProgressionRules`**: Configured qualification zones defining promotion, demotion, and elimination cut-offs.
* **`QualificationZone`**: Defines tournament advancement boundaries for a stage:
  * `targetStage`: Name of destination stage or final disposition (`ADVANCE_FINALS`, `ADVANCE_WINNERS`, `DROP_LOSERS`, `ELIMINATED`).
  * `rankStart` and `rankEnd` (e.g. 1 to 8 vs 9 to 16).
  * `label` and `colorType` (Success/Green, Warning/Amber, Danger/Red).
* **`Team`**: Official team profile with `name`, `tag` (e.g. `TWIS`, `FAZE`, `17`), `colorHex` (e.g. `#A855F7`), and `logoUrl`.
* **`Player`**: Player account tied to a team roster. Identified by Krafton `accountId` and in-game nickname.
* **`Match`**: An individual competitive game belonging to a Stage. Holds sequence number (`matchNumber`), map name, duration, telemetry source metadata, and reduced state.

---

## 4. Functional Requirements

### 4.1 Feature Set 1: Tournament Roadmap & Stage Management

* **FR-1.1 (Tournament Creation)**: The system shall allow an Admin to create a `Tournament` with title, slug, season/year, dates, location, prize pool, and description.
* **FR-1.2 (Stage Creation & Sequencing)**: The system shall allow an Admin to create ordered `Stage`s under a Tournament, specifying sequence number, stage name, start/end dates, and estimated match count.
* **FR-1.3 (Stage Lifecycle Status)**: Each stage shall maintain a status:
  * `UPCOMING`: Scheduled for the future, no matches played.
  * `ONGOING`: Currently active stage, matches played but none currently live in-game.
  * `LIVE`: Currently has a match actively underway.
  * `COMPLETED`: All scheduled matches played and final standings locked.
* **FR-1.4 (Tournament Stages Hub / Roadmap View)**:
  * Navigating to a Tournament page (`/tournaments/{id}`) shall default to the **Stages Roadmap View**.
  * The hub shall display chronological stage cards highlighting status badges (`COMPLETED`, `LIVE NOW`, `UPCOMING`), dates, match progress (e.g. *15/18 Matches*), and the reigning stage leader/champion.
  * If a stage is `LIVE` or `ONGOING`, the top header shall display a high-visibility CTA button: *"Jump to Live Stage"* allowing 1-click access to the active competition.
* **FR-1.5 (Stage Progression Cut-Off Configuration)**:
  * The Admin shall be able to configure qualification cut-off zones for each stage:
    * E.g. Group Stage: Ranks 1–8 Advance to Winners Bracket (`ADVANCE_WINNERS`), Ranks 9–16 Drop to Losers Bracket (`DROP_LOSERS`).
    * E.g. Last Chance: Ranks 1–8 Advance to Grand Finals (`ADVANCE_FINALS`), Ranks 9–16 are Eliminated (`ELIMINATED`).
* **FR-1.6 (Roster Slot Mapping)**: The Admin shall configure the 16 participating teams for the Stage, binding each team to their custom match lobby slot (`slotNumber` 1 through 16).

---

### 4.2 Feature Set 2: Match Ingestion & Telemetry Processing

* **FR-2.1 (Official Telemetry Upload)**: The system shall accept uploads of official Krafton PUBG Developer API telemetry files in `.json` or compressed `.json.gz` format via `POST /api/tournaments/{tournamentId}/stages/{stageId}/matches/upload`.
* **FR-2.2 (Slot-to-Team Resolution)**: During ingestion, the pure `MatchEventReducer` shall map raw `teamId` (1–16) from telemetry events directly to the Stage's configured `Team` profile.
* **FR-2.3 (Direct Synchronous Processing)**: 
  * The server shall stream the uploaded JSON payload in-flight using Jackson Streaming without loading the full DOM into memory.
  * Processing shall complete within $\le 3.0$ seconds for standard 40MB telemetry files on reference hardware.
  * The UI shall display a loading state on the upload trigger and redirect to the ingested match upon HTTP 201 response.
* **FR-2.4 (Validation & Error Reporting)**: If the uploaded file is malformed, missing required match definition events, or does not match the configured stage slot count, the system shall reject the upload with an HTTP 400 status and a descriptive domain error message.
* **FR-2.5 (Bundled Fixtures)**: The system shall provide a built-in `BundledFixtureLoader` capable of loading at least 3 pre-packaged pro matches (PGC/EWC) with zero external network connectivity for offline testing and demonstration.

---

### 4.3 Feature Set 3: Scoring Engine, Leaderboards & Progression Cut-Offs

* **FR-3.1 (Points Calculation)**: For every match, the engine shall compute:
  * **Kill Points**: Exactly 1 point per confirmed kill.
  * **Placement Points**:
    * 1st: 10 pts, 2nd: 6 pts, 3rd: 5 pts, 4th: 4 pts, 5th: 3 pts, 6th: 2 pts, 7th: 1 pt, 8th: 1 pt, 9th–16th: 0 pts.
* **FR-3.2 (Official S.U.P.E.R. Tie-Breaker Solver)**: When teams are tied on total points, the engine shall evaluate ties using the strict 4-tier hierarchy:
  1. Total accumulated Placement Points across all matches in the stage.
  2. Total Match Points (Placement + Kills) scored in the most recent match.
  3. Placement position in the most recent match.
  4. Total damage dealt in the most recent match.
* **FR-3.3 (EWC Smash Rule Engine)**:
  * When a Stage is set to `SMASH_RULE`, the engine shall track each team's cumulative points.
  * Once a team reaches or surpasses the configured point threshold (e.g. $\ge 60$ pts), the engine marks that team as **Smash Eligible** (displaying a prominent indicator on the leaderboard).
  * If a Smash-Eligible team achieves 1st place (WWCD) in any subsequent match, that team is crowned Stage Champion, and the stage concludes.
* **FR-3.4 (Stage Leaderboard Presentation)**: The UI shall display:
  * Rank, Team Name, Team Logo, Matches Played, Kill Points, Placement Points, Total Points, and WWCDs (Wins).
  * Interactive tooltips explaining tie-breaker resolutions.
  * Smash-eligibility badges when Smash Rule is active.
* **FR-3.5 (Visual Cut-Off Lines & Status Highlighting)**:
  * The standings table shall render prominent **horizontal cut-off divider lines** between qualification tiers (e.g. `▲ ADVANCES TO GRAND FINALS (TOP 8) • CUT-OFF LINE • ELIMINATED (9TH-16TH) ▼`).
  * Teams in advancing positions shall feature green accent left-borders and progression badges (e.g., `QUALIFIED 🏆` or `ADVANCES TO WINNERS 🟢`).
  * Teams in demotion positions shall feature amber accent borders (e.g., `DROPS TO LOSERS 🟡`).
  * Teams in elimination positions shall feature red accent borders, dimmed row opacity, and status badges (e.g., `ELIMINATED 🔴`).
  * Teams near the cut-off boundary shall display points-to-safety margins (e.g. `-2 pts below cut-off`).

---

### 4.4 Feature Set 4: Player Statistics Engine

* **FR-4.1 (Metrics Extraction)**: The reducer shall calculate the following metrics per player across all matches in the Stage:
  * **Kills**: Confirmed eliminations.
  * **Total Damage**: Cumulative damage dealt to opponents (excluding team damage/suicide).
  * **Average Damage (Damage/Match)**: $\frac{\text{Total Damage}}{\text{Matches Played}}$.
  * **DBNOs (Knocks)**: Down But Not Out count (`LogPlayerMakeGroggy`).
  * **Assists**: Assists credited in `LogPlayerKillV2`.
  * **Headshot Kills**: Kills where `damageReason == HeadShot`.
  * **Headshot %**: $\frac{\text{Headshot Kills}}{\text{Total Kills}} \times 100$.
  * **Longest Kill Distance**: Maximum elimination distance in meters.
  * **Average Survival Time**: Mean match survival duration.
* **FR-4.2 (Table View & Sorting)**:
  * Displays all participating players in the Stage.
  * Supports client-side multi-column sorting (clicking headers: Kills, Damage, Knocks, etc.).
  * Real-time text search by player nickname or team.
  * Team filter dropdown (filters table to a specific team's active players).
* **FR-4.3 (Player Drill-Down Performance Card)**:
  * Clicking any player row opens a detailed modal / drawer.
  * Displays player highlight badges (Total Kills, Total Damage, Knocks, Headshot %).
  * Displays a chronological **Match-by-Match Breakdown** table showing Match #, Map, Kills, Damage, Assists, and Survival Time.

---

### 4.5 Feature Set 5: Interactive 2D Replay Map & Kill Feed

* **FR-5.1 (Map Calibration)**: The 2D SVG canvas shall support the 4 competitive PUBG maps:
  * **Erangel**, **Miramar**, **Taego**, and **Rondo** ($8\times 8$ km, $816{,}000 \times 816{,}000$ coordinate space).
* **FR-5.2 (Playback Controls)**:
  * Continuous scrub slider traversing match time from `00:00` to end of match.
  * Play, Pause, and Step buttons (-10s / +10s).
  * Playback speed multiplier (1x, 2x, 5x, 10x).
* **FR-5.3 (Circle Zones)**:
  * Animate the **White Safe Zone** (static target circle for the active phase).
  * Animate the **Blue Zone** (dynamically contracting circle based on timestamp and phase radii).
* **FR-5.4 (Player & Team Visualization)**:
  * Active players rendered as colored dots matching their official team color with player name labels.
  * Eliminated players display a casualty marker (skull icon or fade out).
  * Knocked players (DBNO) show a highlighted state (amber halo).
* **FR-5.5 (Kill Vectors)**:
  * When an elimination occurs, a vector line is rendered connecting the killer coordinate to the victim coordinate, displaying distance and weapon.
* **FR-5.6 (Synchronized Kill Feed Sidebar)**:
  * A dedicated sidebar displays the chronological feed of kills and knocks for the match.
  * Each feed card displays: timestamp, phase, killer (with team tag), weapon name, distance, and victim (with team tag).
  * **Interactive Scrubbing**: Clicking any kill feed card immediately jumps the 2D replay slider to that exact timestamp.

---

## 5. Non-Functional Requirements & Architecture Constraints

* **NFR-1 (Compiler-Enforced Hexagonal Architecture)**:
  * `:core` module contains zero Spring, zero JPA, and zero network/filesystem dependencies.
  * All domain models (`Tournament`, `Stage`, `Match`, `Team`, `Player`, `MatchReplay`) are immutable Java 27 `record`s.
  * All rules and reducers are 100% pure functions.
* **NFR-2 (Performance Targets)**:
  * Telemetry ingestion and reduction of a 40MB file: $\le 3$ seconds.
  * Standings and Player Stats REST response time: $\le 100$ms.
  * 2D SVG Replay animation: 60 FPS in modern browsers.
* **NFR-3 (Data Storage & Migration)**:
  * Relational persistence via PostgreSQL 16+ using Spring Data JPA.
  * Database schema managed strictly via Liquibase migrations.

---

## 6. Inbound REST API Specification (Shell)

| Method | Endpoint | Access | Purpose |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/tournaments` | Public | List all tournaments with active stage indicators |
| `GET` | `/api/tournaments/{id}` | Public | Get tournament details with ordered stages roadmap & statuses |
| `POST` | `/api/tournaments` | Admin | Create a new tournament |
| `POST` | `/api/tournaments/{id}/stages` | Admin | Create a stage with ruleset, slot mapping, and cut-off rules |
| `GET` | `/api/tournaments/{id}/stages/{stageId}/standings` | Public | Get calculated leaderboard with cut-off lines & progression statuses |
| `GET` | `/api/tournaments/{id}/stages/{stageId}/player-stats` | Public | Get stage player statistics table |
| `GET` | `/api/tournaments/{id}/stages/{stageId}/players/{playerId}` | Public | Get individual player match-by-match breakdown |
| `GET` | `/api/matches/{id}/replay` | Public | Get 2D replay state (zones, sampled paths, kill events) |
| `POST` | `/api/tournaments/{id}/stages/{stageId}/matches/upload` | Admin | Upload and ingest telemetry JSON file |
| `POST` | `/api/tournaments/{id}/stages/{stageId}/fixtures/load` | Admin | Ingest bundled demo fixture matches |

---

## 7. Acceptance Criteria (Given - When - Then)

### Scenario 1: S.U.P.E.R. Tie-Breaker Resolution
* **Given** two teams finish a stage tied at 120 total points,
* **When** the `SuperRuleEngine` calculates the final rankings,
* **Then** the team with more total Placement Points is awarded the higher rank.
* **And** if placement points are identical, the team with more total points in the final match is awarded the higher rank.

### Scenario 2: Smash Rule Stage Victory
* **Given** a Stage configured with `SMASH_RULE` and a threshold of 60 points,
* **When** Team A reaches 62 points in Match 5,
* **Then** the leaderboard marks Team A as "Smash Eligible".
* **When** Team A wins Match 7 (WWCD - 1st place),
* **Then** the stage concludes immediately, and Team A is declared Stage Champion.

### Scenario 3: Stage Progression Cut-Off Line Rendering
* **Given** a Last Chance stage with a cut-off rule designating Top 8 to Advance to Grand Finals and 9th–16th as Eliminated,
* **When** a user views the stage standings,
* **Then** a visible divider line separates 8th and 9th place,
* **And** teams 1–8 display green accent borders with `QUALIFIED 🏆` badges,
* **And** teams 9–16 display red accent borders with `ELIMINATED 🔴` badges.

### Scenario 4: Telemetry Slot Mapping Accuracy
* **Given** a Stage with Slot 4 configured as "Twisted Minds" (`#A855F7`),
* **When** a match telemetry file is uploaded containing player `TWIS_xmpl` in `teamId: 4`,
* **Then** the player's kills and damage are credited to "Twisted Minds",
* **And** the 2D replay renders the player's marker with color `#A855F7`.

### Scenario 5: Synchronized Kill Feed Scrubbing
* **Given** the 2D Replay is open for Match 1,
* **When** the user clicks a kill feed item occurring at `14:21`,
* **Then** the replay scrubber jumps to `14:21`, rendering the blue/white zones and player positions at that exact second.
