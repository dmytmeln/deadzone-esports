# `deadzone-esports` — Functional Requirements Specification (FRS)

> **Document Version**: 1.2.0  
> **Status**: Approved via Architectural Alignment  
> **Target Release**: MVP  
> **Reference Architecture**: [`docs/deadzone-esports-architecture.md`](file:///D:/MyProjects/Java/deadzone-esports/docs/deadzone-esports-architecture.md)  
> **UI/UX Reference Mockup**: [`docs/ui-mockup.html`](file:///D:/MyProjects/Java/deadzone-esports/docs/ui-mockup.html)

---

## 1. Executive Summary & Purpose

`deadzone-esports` is a dedicated PUBG Esports tournament engine, statistics calculation platform, and 2D match replay viewer inspired by [Twire.gg](https://twire.gg).

The system accepts official Krafton PUBG telemetry files (`telemetry.json` / `.json.gz`), processes them via a pure Java 27 Functional Core (FCIS + Hexagonal Architecture), persists the normalized state in PostgreSQL, and delivers:
1. **Tournament Catalog & Discovery Hub** (Categorized into `ONGOING`, `PAST`, and `UPCOMING` tournaments, filterable by region and tier, with real-time title search).
2. **Tournament Stages Roadmap & Progression Hub** (Visual overview of stage progression with `LIVE`, `ONGOING`, `COMPLETED`, and `UPCOMING` statuses, stage rule summaries, and reigning/current leaders).
3. **Official Tournament Standings with Qualification Cut-Offs & Deltas** (Standard S.U.P.E.R. & EWC Smash Rule, with visual cut-off lines distinguishing live projected vs. locked final zones, plus match-to-match and day-to-day rank deltas).
4. **Team Statistics Engine** (Tournament-wide and stage-scoped performance analytics, searchable and filterable by match and map).
5. **Comprehensive Player Statistics & Teammate Drill-Down** (Kills, Damage, Knocks, Headshots, Survival Time, filterable by team, match, and map, with an in-modal teammate switcher).
6. **Unified Cross-View Filter Persistence** (Preserving user-selected stage, map, match, and team across Standings, Team Stats, and Player Stats).
7. **Interactive 2D Replay Map** (Realistic PUBG map background, pan/zoom, fullscreen, continuous timeline scrubbing, 5s/10s step toggle, squad player numbers, plane trajectory toggle, in-page match switcher, and synchronized kill feed with auto-camera centering and player highlight beacons).

---

## 2. User Personas & Permissions

| Persona | Role | Capabilities |
| :--- | :--- | :--- |
| **Spectator / Analyst** | Public (Unauthenticated) | • Discover tournaments across `ONGOING`, `PAST`, and `UPCOMING` categories.<br>• Filter tournaments by region, tier, and name.<br>• View tournament stages roadmap, rule summaries, and stage leaders.<br>• View tournament leaderboards with projected/locked cut-off lines and match/day rank deltas.<br>• Analyze Team Stats and Player Stats across tournament and stage scopes with map/match filters.<br>• Open player drill-down cards and switch between teammates seamlessly.<br>• Play, pause, scrub, pan, zoom, and inspect 2D match replays with the kill feed, plane toggle, and in-page match selector. |
| **Tournament Organizer / Admin** | Protected (Authenticated) | • Create and configure Tournaments (with region and tier metadata), Stages, and Progression Cut-Off rules.<br>• Configure Stage Rosters and Lobby Slot Mappings (Slots 1–16).<br>• Select scoring rulesets (Standard S.U.P.E.R. vs. EWC Smash Rule with configurable threshold).<br>• Upload and ingest match telemetry files.<br>• Load bundled fixture matches. |

---

## 3. Domain Model & Competition Hierarchy

The platform strictly implements a three-tier competition structure:

```
┌───────────────────────────────────────────────────────────────────────────┐
│              TOURNAMENT (e.g. PGC 2024, Region: GLOBAL, Tier: S)          │
│                                                                           │
│  STAGES ROADMAP HUB:                                                      │
│  ┌───────────────────────┐       ┌───────────────────────┐                │
│  │   STAGE 1: Group      │       │   STAGE 4: Finals     │                │
│  │   Status: COMPLETED   │ ───►  │   Status: LIVE NOW    │                │
│  │   Leader: Twisted M.  │       │   Leader: FaZe Clan   │                │
│  │   Rule: Top 8 -> Win  │       │   Rule: Champion      │                │
│  └───────────┬───────────┘       └───────────┬───────────┘                │
└──────────────┼───────────────────────────────┼────────────────────────────┘
               ▼                               ▼
      ┌─────────────────┐             ┌─────────────────┐
      │ Match 1 (Day 1) │             │ Match 1 (Day 1) │
      │ Match 2 (Day 1) │             │ Match 2 (Day 1) │
      │ ... Match 18    │             │ ... Match 18    │
      └─────────────────┘             └─────────────────┘
```

### 3.1 Domain Entities & Invariants
* **`Tournament`**: Overarching competition (e.g., *PUBG Global Championship 2024*, *Esports World Cup 2024*).
  * Attributes: `id`, `title`, `slug`, `seasonYear`, `dates`, `location`, `prizePool`, `logoUrl`, `region`, `tier`, ordered `stages`.
  * `TournamentRegion`: Enum (`GLOBAL`, `EMEA`, `AMERICAS`, `APAC`, `ASIA`).
  * `TournamentTier`: Enum (`S_TIER`, `A_TIER`, `B_TIER`, `QUALIFIER`).
* **`Stage`**: Discrete tournament phase (e.g., *Group Stage*, *Winners Bracket*, *Last Chance*, *Grand Finals*).
  * `StageStatus`: Lifecycle state enum (`UPCOMING`, `ONGOING`, `LIVE`, `COMPLETED`).
  * `ScoringRule`: Ruleset configuration (`SUPER_STANDARD` or `SMASH_RULE` with point threshold, default 60 pts).
  * `StageRoster`: Maps custom match lobby slots (1–16) to official Team profiles.
  * `ProgressionRules`: Configured qualification zones defining promotion, demotion, and elimination cut-offs.
  * `ruleSummary`: Human-readable summary string (e.g. `"Top 8 Advance to Winners Bracket, Bottom 8 Drop to Losers"`).
* **`QualificationZone`**: Defines tournament advancement boundaries for a stage:
  * `targetStage`: Name of destination stage or final disposition (`ADVANCE_FINALS`, `ADVANCE_WINNERS`, `DROP_LOSERS`, `ELIMINATED`).
  * `rankStart` and `rankEnd` (e.g. 1 to 8 vs 9 to 16).
  * `label` and `colorType` (Success/Green, Warning/Amber, Danger/Red).
* **`Team`**: Official team profile with `name`, `tag` (e.g. `TWIS`, `FAZE`, `17`), `colorHex` (e.g. `#A855F7`), and `logoUrl`.
* **`Player`**: Player account tied to a team roster. Identified by Krafton `accountId`, in-game nickname, and squad slot index (1–4).
* **`Match`**: An individual competitive game belonging to a Stage. Holds sequence number (`matchNumber`), match day sequence (`dayNumber`), map name, duration, telemetry source metadata, and reduced state.

---

## 4. Functional Requirements

### 4.1 Feature Set 1: Tournament Discovery & Catalog

* **FR-1.1 (Tournament Discovery & Grouping)**:
  * Navigating to the home/tournaments route (`/` or `/tournaments`) shall display all tournaments grouped into three distinct categories:
    * **`ONGOING`**: Tournaments with at least one stage currently `LIVE` or `ONGOING`.
    * **`UPCOMING`**: Tournaments scheduled for the future with no matches played.
    * **`PAST`**: Fully concluded tournaments where all stages are `COMPLETED`.
  * The user shall be able to switch between groups via tab navigation. Each tab shall display a counter badge with the number of tournaments in that category.
* **FR-1.2 (Search & Filtering)**:
  * The tournament catalog shall provide a real-time text search input filtering tournaments by name/title.
  * The user shall be able to filter tournaments by **Region** (`ALL`, `GLOBAL`, `EMEA`, `AMERICAS`, `APAC`, `ASIA`).
  * The user shall be able to filter tournaments by **Tier** (`ALL`, `S_TIER`, `A_TIER`, `B_TIER`, `QUALIFIER`).
  * Filters and search shall update the view immediately without a full page reload.
* **FR-1.3 (Tournament Creation & Admin)**:
  * An Admin shall be able to create and edit a `Tournament` with title, slug, season/year, start/end dates, location, prize pool, logo URL, region, tier, and description.

---

### 4.2 Feature Set 2: Tournament Roadmap & Stage Management

* **FR-2.1 (Stage Creation & Sequencing)**: The system shall allow an Admin to create ordered `Stage`s under a Tournament, specifying sequence number, stage name, start/end dates, and estimated match count.
* **FR-2.2 (Stage Lifecycle Status)**: Each stage shall maintain a lifecycle status:
  * `UPCOMING`: Scheduled for the future, zero matches played.
  * `ONGOING`: Active stage with matches recorded, but no match actively in-flight right now.
  * `LIVE`: Currently has a match actively underway.
  * `COMPLETED`: All scheduled matches played and final standings locked.
* **FR-2.3 (Stages Roadmap Hub & Leader Presentation)**:
  * Navigating to a Tournament page (`/tournaments/{id}`) shall present the **Stages Roadmap View** as the primary progression guide.
  * Chronological stage cards shall render:
    1. **Status Badge**: `COMPLETED`, `LIVE NOW` (with pulsing red indicator), `ONGOING`, or `UPCOMING`.
    2. **Dates & Progress**: Stage date range and match progress counter (e.g. *15/18 Matches*).
    3. **Stage Rule Summary**: The configured progression rule summary (e.g., *"Top 8 Advance to Grand Finals, Bottom 8 Eliminated"*).
    4. **Stage Leader**:
       * If `COMPLETED`: Displays **Stage Champion / Winner** (trophy icon, champion team name, logo, and final total points).
       * If `LIVE` or `ONGOING`: Displays **Current Leader** (`#1 Team` in interim standings with current points).
       * If `UPCOMING`: Displays `TBD` or scheduled start countdown.
  * If any stage is `LIVE` or `ONGOING`, the top header shall display a high-visibility CTA button: *"Jump to Live Stage"*, routing directly to the active stage leaderboard.
* **FR-2.4 (Stage Progression Cut-Off Configuration)**:
  * The Admin shall configure qualification cut-off zones per stage:
    * E.g. Group Stage: Ranks 1–8 Advance to Winners Bracket (`ADVANCE_WINNERS`), Ranks 9–16 Drop to Losers Bracket (`DROP_LOSERS`).
    * E.g. Last Chance: Ranks 1–8 Advance to Grand Finals (`ADVANCE_FINALS`), Ranks 9–16 are Eliminated (`ELIMINATED`).
* **FR-2.5 (Roster Slot Mapping)**: The Admin shall configure the 16 participating teams for the Stage, binding each team to their custom match lobby slot (`slotNumber` 1 through 16).

---

### 4.3 Feature Set 3: Match Ingestion & Telemetry Processing

* **FR-3.1 (Official Telemetry Upload)**: The system shall accept uploads of official Krafton PUBG Developer API telemetry files in `.json` or compressed `.json.gz` format via `POST /api/tournaments/{tournamentId}/stages/{stageId}/matches/upload`.
* **FR-3.2 (Slot-to-Team Resolution)**: During ingestion, the pure `MatchEventReducer` shall map raw `teamId` (1–16) from telemetry events directly to the Stage's configured `Team` profile.
* **FR-3.3 (Direct Synchronous Processing)**: 
  * The server shall stream the uploaded JSON payload in-flight using Jackson Streaming without loading the full DOM into memory.
  * Processing shall complete within $\le 3.0$ seconds for standard 40MB telemetry files on reference hardware.
  * The UI shall display a loading state on the upload trigger and redirect to the ingested match upon HTTP 201 response.
* **FR-3.4 (Validation & Error Reporting)**: If the uploaded file is malformed, missing required match definition events, or does not match the configured stage slot count, the system shall reject the upload with an HTTP 400 status and a descriptive domain error message.
* **FR-3.5 (Bundled Fixtures)**: The system shall provide a built-in `BundledFixtureLoader` capable of loading at least 3 pre-packaged pro matches (PGC/EWC) with zero external network connectivity for offline testing and demonstration.

---

### 4.4 Feature Set 4: Scoring Engine, Leaderboards & Progression Cut-Offs

* **FR-4.1 (Standard S.U.P.E.R. Scoring)**: For every match, the engine shall compute:
  * **Kill Points**: Exactly 1 point per confirmed elimination.
  * **Placement Points**:
    * 1st: 10 pts, 2nd: 6 pts, 3rd: 5 pts, 4th: 4 pts, 5th: 3 pts, 6th: 2 pts, 7th: 1 pt, 8th: 1 pt, 9th–16th: 0 pts.
* **FR-4.2 (Official S.U.P.E.R. Tie-Breaker Solver)**: When teams are tied on total points, the engine shall evaluate ties using the strict 4-tier hierarchy:
  1. Total accumulated Placement Points across all matches in the stage.
  2. Total Match Points (Placement + Kills) scored in the most recent match.
  3. Placement position in the most recent match.
  4. Total damage dealt in the most recent match.
* **FR-4.3 (EWC Smash Rule Engine)**:
  * When a Stage is set to `SMASH_RULE`, the engine shall track each team's cumulative points against the configured threshold (default: 60 pts).
  * Once a team reaches or surpasses the threshold, the engine marks that team as **Smash Eligible** (displaying a prominent badge on the leaderboard).
  * If a Smash-Eligible team achieves 1st place (WWCD) in any subsequent match, that team is crowned Stage Champion, and the stage concludes.
  * Placements 2nd through 16th are ordered by total cumulative points subject to the standard tie-breaker rules.
* **FR-4.4 (Stage Leaderboard Presentation)**: The UI shall display:
  * Rank, Team Name, Team Logo, Matches Played, Kill Points, Placement Points, Total Points, and WWCDs (Wins).
  * Interactive tooltips explaining tie-breaker resolutions.
  * Smash-eligibility badges when Smash Rule is active.
* **FR-4.5 (Rank Deltas per Match & per Day)**:
  * **Match-to-Match Delta**: The leaderboard shall display each team's rank movement since the previous match:
    * `▲ +N` (green) if rank improved.
    * `▼ -N` (red) if rank dropped.
    * `-` (neutral) if rank stayed identical.
  * **Day-to-Day Delta & Day View**:
    * The UI shall allow the user to select/filter by **Match Day** (e.g. *All Days*, *Day 1*, *Day 2*, *Day 3*).
    * When viewing standings, the system shall provide a day-progression indicator showing rank change across match days (e.g. illustrating comebacks from Rank 16 to Rank 5).
* **FR-4.6 (Visual Cut-Off Lines & Status Highlighting — Live vs. Completed)**:
  * **Live / Ongoing Stages (`LIVE` / `ONGOING`)**:
    * Render **Projected Cut-Off Divider Lines** (dashed divider with text: `▲ CURRENT QUALIFICATION ZONE (TOP 8) • PROJECTED BUBBLE • CURRENT ELIMINATION ZONE (9TH-16TH) ▼`).
    * Use soft background row shading and subtle left-border accents to indicate current projected status without declaring permanent elimination.
    * Teams near the bubble line shall display points-to-safety margins (e.g. `-2 pts below cut-off`).
    * *(Clinch Indicator)*: If a team has mathematically secured qualification regardless of remaining match outcomes, a `🔒 Clinched` badge shall be displayed.
  * **Completed Stages (`COMPLETED`)**:
    * Render **Locked Solid Cut-Off Lines**.
    * Display permanent, high-contrast badges:
      * Advancing positions: `QUALIFIED 🏆` or `ADVANCES TO WINNERS 🟢` with green border accents.
      * Demotion positions: `DROPS TO LOSERS 🟡` with amber border accents.
      * Elimination positions: `ELIMINATED 🔴` with red border accents and dimmed row opacity.

---

### 4.5 Feature Set 5: Team Statistics Engine

* **FR-5.1 (Scope of Aggregation)**:
  * The Team Stats view shall support two operational scopes:
    1. **Stage Scope**: Statistics aggregated across matches within a specific Stage.
    2. **Tournament Scope**: Statistics aggregated across all stages of the entire Tournament.
* **FR-5.2 (Team Performance Metrics)**: For every team in the selected scope, the engine shall compute and display:
  * **Matches Played**: Total games contested.
  * **Total Points**: Cumulative tournament points (Kill + Placement).
  * **Points / Match**: $\frac{\text{Total Points}}{\text{Matches Played}}$.
  * **Total Kills**: Cumulative confirmed kills.
  * **Kills / Match**: $\frac{\text{Total Kills}}{\text{Matches Played}}$.
  * **Total Damage**: Cumulative damage dealt to opponents.
  * **Damage / Match**: $\frac{\text{Total Damage}}{\text{Matches Played}}$.
  * **Average Placement**: Mean finishing position per match.
  * **WWCD Count & Win Rate %**: Total wins (1st place) and $\frac{\text{WWCDs}}{\text{Matches Played}} \times 100$.
  * **Top 4 Count & Top 4 %**: Finishes in ranks 1–4 and $\frac{\text{Top 4 Finishes}}{\text{Matches Played}} \times 100$.
  * **Total Knocks (DBNOs)**: Opponents knocked down.
  * **Assists**: Total credited assists.
* **FR-5.3 (Table Sorting & Search)**:
  * Support client-side multi-column sorting (clicking headers: Points, Kills/Match, Avg Damage, Top 4 %, etc.).
  * Real-time text search filtering by team name or team tag.
* **FR-5.4 (Filtering Capabilities)**:
  * **Stage Filter** (when viewing in Tournament Scope): Dropdown to isolate stats to a specific stage or view all stages combined.
  * **Match Filter**: Dropdown/multi-select to filter by specific match sequence (e.g. Match 1, Match 5, or Match range).
  * **Map Filter**: Dropdown to filter performance by map (`All Maps`, `Erangel`, `Miramar`, `Taego`, `Rondo`).

---

### 4.6 Feature Set 6: Player Statistics Engine

* **FR-6.1 (Metrics Extraction)**: The reducer shall calculate the following metrics per player across the selected scope:
  * **Kills**: Confirmed eliminations.
  * **Total Damage**: Cumulative damage dealt to opponents (excluding team damage/suicide).
  * **Average Damage (Damage/Match)**: $\frac{\text{Total Damage}}{\text{Matches Played}}$.
  * **DBNOs (Knocks)**: Down But Not Out count (`LogPlayerMakeGroggy`).
  * **Assists**: Assists credited in `LogPlayerKillV2`.
  * **Headshot Kills**: Kills where `damageReason == HeadShot`.
  * **Headshot %**: $\frac{\text{Headshot Kills}}{\text{Total Kills}} \times 100$.
  * **Longest Kill Distance**: Maximum elimination distance in meters.
  * **Average Survival Time**: Mean match survival duration.
* **FR-6.2 (Table View, Search & Filtering)**:
  * Supports dual scope: **Stage Scope** and **Overall Tournament Scope**.
  * Multi-column sorting by any stat metric.
  * Real-time text search by player nickname or team tag.
  * Dropdown filters:
    * **Team Filter**: Filter to active players of a specific team.
    * **Match Filter**: Filter to a specific match or match range.
    * **Map Filter**: Filter to a specific map (`Erangel`, `Miramar`, `Taego`, `Rondo`).
* **FR-6.3 (Player Drill-Down Modal with Teammate Switcher)**:
  * Clicking any player row shall open a comprehensive performance modal card.
  * The modal shall render:
    1. Player overview badges (Total Kills, Total Damage, Knocks, Headshot %, Longest Kill).
    2. Chronological **Match-by-Match Breakdown** table (Match #, Map, Kills, Damage, Knocks, Assists, Survival Time).
    3. **In-Modal Teammate Switcher**: A dedicated selector (tabs or pill buttons) displaying all active players on the same team, allowing the user to switch between teammates directly without closing or navigating away from the modal.

---

### 4.7 Feature Set 7: Cross-View Filter Persistence

* **FR-7.1 (URL Query Parameter Synchronization)**:
  * Shared filters—including selected **Stage**, **Map**, **Match**, and **Team**—shall synchronize bidirectionally with browser URL search parameters (e.g. `/tournaments/1/stats?stageId=2&map=Erangel&match=3`).
  * When a user switches between the **Leaderboard**, **Team Stats**, and **Player Stats** tabs, the currently active filter criteria shall persist seamlessly without resetting to default values.
  * Browser navigation (Back / Forward) shall accurately restore previous filter configurations.

---

### 4.8 Feature Set 8: Interactive 2D Replay Map & Kill Feed

* **FR-8.1 (Map Calibration & Realistic Raster Background)**:
  * The 2D SVG canvas shall render on top of the official, high-resolution top-down raster map textures for the 4 competitive maps:
    * **Erangel**, **Miramar**, **Taego**, and **Rondo** ($8\times 8$ km, $816{,}000 \times 816{,}000$ Krafton coordinate space).
* **FR-8.2 (Interactive Pan, Zoom & Fullscreen)**:
  * **Mouse Drag Pan**: Users shall be able to click and drag anywhere on the map canvas to pan smoothly.
  * **Zoom In / Out**: Support continuous zoom via mouse wheel, trackpad pinch, and dedicated on-screen zoom buttons (`+`, `-`, and `Reset View`).
  * **Fullscreen Mode**: A high-visibility button shall toggle native browser Fullscreen mode for immersive spectator and analyst replay review.
* **FR-8.3 (Playback & Scrubbing Controls)**:
  * Continuous scrub slider traversing match time from `00:00` to end of match.
  * Play and Pause controls with keyboard shortcuts (Spacebar).
  * Playback speed multiplier (1x, 2x, 5x, 10x).
  * **Step Buttons with Interval Selector**:
    * Rewind and fast-forward buttons.
    * Step interval toggle allowing user to choose between **5 seconds** or **10 seconds** per step.
* **FR-8.4 (Circle Zones Animation)**:
  * Animate the **White Safe Zone** (static target circle for the active phase).
  * Animate the **Blue Zone** (dynamically contracting circle based on timestamp and phase radii).
* **FR-8.5 (Squad, Player Numbers & Casualty Visualization)**:
  * Active players rendered as colored dots matching their official team color.
  * **Player Numbers**: Each player dot shall display their squad slot number (1, 2, 3, 4) alongside their player nickname label.
  * Eliminated players display a casualty marker (skull icon or gradual fade-out).
  * Knocked players (DBNO) show an animated highlight state (pulsing amber halo).
  * Elimination events render an instantaneous vector line connecting killer to victim with weapon icon and distance.
* **FR-8.6 (Plane Trajectory & Visibility Toggle)**:
  * During the match drop phase, the replay shall render the flight path vector and an animated plane icon across the map.
  * The UI shall provide a dedicated toggle button to **Show / Hide Plane** to declutter the canvas during subsequent phases.
* **FR-8.7 (In-Page Match Selector)**:
  * The 2D Replay header shall contain an immediate match dropdown selector (e.g. *Match 1: Erangel*, *Match 2: Miramar*), allowing the user to switch matches directly from within the 2D replay page without returning to the tournament roadmap.
* **FR-8.8 (Synchronized Kill Feed with Camera Centering & Player Highlighting)**:
  * A dedicated sidebar displays the chronological feed of confirmed kills and knocks (DBNOs).
  * Each feed card displays: timestamp, phase, killer (with team tag), weapon name, distance, and victim (with team tag).
  * **Interactive Centering & Highlighting**: Clicking any kill feed card shall:
    1. Immediately scrub the replay slider to that exact timestamp.
    2. Automatically **pan/center the map camera** onto the coordinates of the event.
    3. Trigger a high-visibility animated **pulse beacon** highlighting the involved killer/victim.

---

## 5. Non-Functional Requirements & Architecture Constraints

* **NFR-1 (Compiler-Enforced Hexagonal Architecture)**:
  * `:core` module contains zero Spring, zero JPA, and zero network/filesystem dependencies.
  * All domain models (`Tournament`, `Stage`, `Match`, `Team`, `Player`, `MatchReplay`) are immutable Java 27 `record`s.
  * All rules, tie-breaker solvers, and telemetry stream reducers are 100% pure functions.
* **NFR-2 (Performance Targets)**:
  * Telemetry ingestion and reduction of a 40MB file: $\le 3.0$ seconds.
  * Standings, Team Stats, and Player Stats REST response time: $\le 100$ms.
  * 2D Replay canvas rendering: $\ge 60$ FPS in modern browsers.
* **NFR-3 (Data Storage & Migration)**:
  * Relational persistence via PostgreSQL 16+ using Spring Data JPA.
  * Database schema managed strictly via Liquibase migrations.

---

## 6. Inbound REST API Specification (Shell)

| Method | Endpoint | Access | Purpose & Query Parameters |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/tournaments` | Public | List tournaments with filtering: `?status=ONGOING\|PAST\|UPCOMING&region=EMEA&tier=S_TIER&search=...` |
| `GET` | `/api/tournaments/{id}` | Public | Get tournament details with ordered stages roadmap & stage leader summaries |
| `POST` | `/api/tournaments` | Admin | Create a new tournament (title, slug, season, dates, location, prizePool, region, tier, description) |
| `POST` | `/api/tournaments/{id}/stages` | Admin | Create a stage with ruleset, slot mapping, and cut-off rules |
| `GET` | `/api/tournaments/{id}/stages/{stageId}/standings` | Public | Get calculated leaderboard with cut-off lines, rank deltas, and day filtering: `?dayNumber=1` |
| `GET` | `/api/tournaments/{id}/stages/{stageId}/team-stats` | Public | Get team stats for a stage: `?matchId=...&map=...&search=...` |
| `GET` | `/api/tournaments/{id}/team-stats` | Public | Get overall tournament team stats: `?stageId=...&matchId=...&map=...&search=...` |
| `GET` | `/api/tournaments/{id}/stages/{stageId}/player-stats` | Public | Get player stats for a stage: `?teamId=...&matchId=...&map=...&search=...` |
| `GET` | `/api/tournaments/{id}/player-stats` | Public | Get overall tournament player stats: `?stageId=...&teamId=...&matchId=...&map=...&search=...` |
| `GET` | `/api/tournaments/{id}/stages/{stageId}/players/{playerId}` | Public | Get individual player match breakdown and teammate roster |
| `GET` | `/api/matches/{id}/replay` | Public | Get 2D replay state (map raster metadata, zones, flight path, sampled player paths, kill events) |
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
* **Then** the stage concludes immediately, Team A is crowned Stage Champion, and ranks 2–16 are sorted by total points.

### Scenario 3: Live vs. Completed Stage Cut-Off Highlighting
* **Given** an ongoing Group Stage where only 4 of 18 matches have been played,
* **When** a user views the stage standings,
* **Then** a dashed divider line indicates the projected qualification boundary,
* **And** teams display projected zone indicators without definitive "ELIMINATED" badges.
* **When** all 18 matches are completed,
* **Then** the divider becomes a solid cut-off line, and teams 9–16 display definitive `ELIMINATED 🔴` badges.

### Scenario 4: Match & Day Rank Deltas
* **Given** Team B finished Match 2 at Rank 10,
* **When** Team B scores 18 points in Match 3 and rises to Rank 6,
* **Then** the leaderboard displays `▲ +4` in Team B's rank change column.
* **When** viewing the Day 2 filter,
* **Then** Team B's progression from their Day 1 finishing rank is displayed.

### Scenario 5: Teammate Switcher Inside Player Modal
* **Given** the user is viewing the detailed stats modal for player `TWIS_xmpl`,
* **When** the user clicks teammate `TWIS_BatulinS` within the in-modal teammate selector,
* **Then** the modal transitions to display `BatulinS`'s stats and match breakdown without closing the modal or altering page state.

### Scenario 6: Kill Feed Click Camera Centering & Beacon
* **Given** the user is inspecting the 2D Replay for Match 1,
* **When** the user clicks a kill feed item occurring at `18:45` involving `FaZe_Gustav`,
* **Then** the replay scrubber moves to `18:45`,
* **And** the 2D map view camera centers on `FaZe_Gustav`'s coordinate with an animated highlight pulse beacon.

### Scenario 7: Tournament Discovery Filtering
* **Given** tournaments exist across EMEA, AMERICAS, and GLOBAL,
* **When** the user selects the `ONGOING` tab and filters by `region: EMEA`,
* **Then** only active tournaments belonging to EMEA are rendered in the catalog.
