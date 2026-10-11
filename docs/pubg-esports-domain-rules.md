# PUBG Esports Domain Rules & Competition Specification

> **Document Version**: 3.0.0 (Unified Multi-Era Competitive Standard & Tournament Topology Catalog)  
> **Status**: Approved & Authoritative  
> **Target Systems**: `deadzone-esports` Domain Core, Ingestion Engine & Leaderboard Services  
> **Companion Document**: [`docs/pubg-telemetry-event-contract.md`](file:///D:/MyProjects/Java/deadzone-esports/docs/pubg-telemetry-event-contract.md)

---

## 1. Executive Summary & Scope

This specification defines the authoritative competitive rules, tournament stage topologies, scoring algorithms, and domain invariants governing professional PUBG Esports across its modern standard and historical lineage (2019–2026).

It acts as the single source of truth for the `deadzone-esports` platform, driving:
1. **Competition Data Modeling** (`Tournament`, `Stage`, `MatchDay`, `Match`, `Roster`, `TeamSlot` 1–16).
2. **Pluggable Scoring & Tie-Breaker Strategies**:
   * S.U.P.E.R. Modern v3 & v2 (Placement-first hierarchy).
   * S.U.P.E.R. Legacy v1 (Kill-first hierarchy).
   * Most Chicken / WWCD Engine (Match wins primary).
   * EWC / Smash Rule Match Point Engine.
3. **Player Elimination Lifecycle Models**:
   * Historical Single-Life Permanent Elimination (2019–2025).
   * Modern Multi-Life Blue Chip Recall Towers (2026).
4. **Authoritative Tournament Topologies & Progression Funnels**:
   * **Modern 2026**: PGS Circuit System (24 teams), PEC Championship (EMEA), PGC 2026 (Tiered Entry & Survival Ladder).
   * **Historical Lineage (2021–2025)**: PGS 2024–2025, PEC 2024–2025 Closed Qualifiers, PGC 2025 Split-Funnel, PGC 2024 Waterfall Circuit, PGC 2023 Double Elimination, PGC 2022 Grand Survival, and PGC/PGI.S 2021 Dynamic Waitlist Rolling Ladder.
5. **State Machines & Mathematical Solvers**:
   * Clinch condition algorithm ("Magic Number").
   * Rolling lobby backfill queue state machine.

> [!NOTE]
> **MVP Scope Boundary**: The MVP focuses strictly on intra-tournament and intra-stage calculations (match telemetry processing, stage standings, rank deltas, bracket cut-offs, dynamic waitlist progressions, and single-tournament progression). Global cross-tournament annual leaderboards (e.g. cumulative multi-event annual PGC/PGS points tables) and cross-regional trickle-down allocations are defined conceptually for seeding context but are excluded from MVP automated calculation.

---

## 2. Ubiquitous Domain Terminology

```
┌────────────────────────────────────────────────────────────────────────┐
│                        DOMAIN VOCABULARY MATRIX                        │
├──────────────────────┬─────────────────────────────────────────────────┤
│ Core Entities        │ Tournament, Stage, MatchDay, Match, TeamSlot    │
│ Scoring Strategies   │ SUPER_V3, SUPER_V2, SUPER_V1_LEGACY, MOST_CHICKEN│
│ Elimination Models   │ SINGLE_LIFE_PERMANENT, MULTI_LIFE_RECALL        │
│ Progression Types    │ ROUND_ROBIN, DOUBLE_ELIMINATION, WATERFALL_STEP,│
│                      │ DYNAMIC_WAITLIST_LADDER, LAST_CHANCE            │
└──────────────────────┴─────────────────────────────────────────────────┘
```

| Domain Term | Definition | Invariants & Business Rules |
| :--- | :--- | :--- |
| **S.U.P.E.R.** | Standard and Universal PUBG Esports Ruleset | Official Krafton regulatory framework standardizing match settings, point tables, and tie-breakers. |
| **Lobby Slot** | Fixed integer index (1 through 16) | Standard competitive PUBG lobbies strictly host **16 teams** (4 players per squad, 64 players total). Custom match lobby slots (1–16) map directly to registered tournament teams. |
| **WWCD** | "Winner Winner Chicken Dinner" | Finishing 1st place in an individual match (awards 10 placement points under S.U.P.E.R.; serves as primary rank metric under Most Chicken rules). |
| **DBNO** | "Down But Not Out" (Knock) | State where a player sustains fatal damage while at least one squad teammate remains alive. |
| **Smash Rule** | Match Point tournament format | Stage format where reaching a points threshold qualifies a team for match point; winning a WWCD in a subsequent match wins the championship. |
| **Recall Tower** | Blue Chip Recall Station | In-game station allowing surviving players to respawn eliminated teammates. **Permanently deactivates at the start of Phase 7 in 2026 rules; disabled in 2019–2025**. |
| **Single-Life Rule** | Permanent elimination invariant | In 2019–2025 competitive rules, player eliminations are final; exactly 64 lives exist per match. |
| **Cut-Off Line** | Qualification threshold boundary | Rank divider in a leaderboard delineating advancing, demoting, or eliminated zones. |
| **Clinch** | Mathematically secured qualification | State where a team's cumulative point lead over the cut-off rank exceeds the maximum points any trailing team can mathematically earn in remaining matches. |
| **Rolling Waitlist** | Dynamic lobby backfill queue | Stage mechanic (PGI.S / PGC 2021) where match winners exit immediately and waitlisted teams backfill vacated slots for the next match. |
| **Waterfall Stage** | Staggered tier entry bracket | Stage format (PGC 2024) where daily pools combine surviving teams from the prior day with higher-seeded cohorts. |
| **Invited vs. Qualified** | Team Enrollment Origin | Distinguishes whether a team enters via direct seed/partner status (`GLOBAL_PARTNER`, `REGIONAL_PARTNER`, `SPECIAL_INVITE`, `HOST_WILDCARD`) or earned qualification (`QUALIFIED_REGIONAL`, `QUALIFIED_CUP`). |

---

## 3. Official Scoring & Ranking Engine Catalog

```
┌────────────────────────────────────────────────────────────────────────┐
│                   SCORING & RANKING STRATEGY TAXONOMY                  │
├──────────────────────┬────────────────────────┬────────────────────────┤
│ Strategy             │ Primary Ranking Key    │ Era / Scope            │
├──────────────────────┼────────────────────────┼────────────────────────┤
│ 1. S.U.P.E.R. v2/v3  │ Placement Pts + Kills  │ mid 2022 – Present     │
│ 2. S.U.P.E.R. v1     │ Placement Pts + Kills  │ 2019 – mid 2022        │
│ 3. Most Chicken (MC) │ WWCD Count (Wins)      │ 2021 (PCS4, PCS5)      │
│ 4. Smash / Match Pt  │ Threshold Check + WWCD │ 2024–2026 (BSC, EWC)   │
└──────────────────────┴────────────────────────┴────────────────────────┘
```

### 3.1 Standard S.U.P.E.R. Point Matrix (Universal 10-Point Scale)

Across all S.U.P.E.R. eras (2019 through 2026), point allocation follows the official 10-point scale:

$$\text{Total Match Points} = \text{Kill Points} + \text{Placement Points}$$

* **Kill Points**: Exactly **1 point** per confirmed elimination.
* **Placement Points Matrix**:
  * **1st Place (WWCD)**: 10 pts
  * **2nd Place**: 6 pts
  * **3rd Place**: 5 pts
  * **4th Place**: 4 pts
  * **5th Place**: 3 pts
  * **6th Place**: 2 pts
  * **7th Place**: 1 pt
  * **8th Place**: 1 pt
  * **9th – 16th Place**: 0 pts

---

### 3.2 S.U.P.E.R. Tie-Breaker Policy Evolution

The domain model supports two distinct tie-breaker hierarchies based on ruleset version:

```
MODERN (Post-June 2, 2022 to Present)      LEGACY (2019 to June 2, 2022)
┌─────────────────────────────────────┐    ┌─────────────────────────────────────┐
│ Tier 1: Total Placement Points      │    │ Tier 1: Total Accumulated Kills     │
└──────────────────┬──────────────────┘    └──────────────────┬──────────────────┘
                   │ Tied                                     │ Tied
                   ▼                                          ▼
┌─────────────────────────────────────┐    ┌─────────────────────────────────────┐
│ Tier 2: Last Match Total Points     │    │ Tier 2: Best Single Match Points    │
└──────────────────┬──────────────────┘    └──────────────────┬──────────────────┘
                   │ Tied                                     │ Tied
                   ▼                                          ▼
┌─────────────────────────────────────┐    ┌─────────────────────────────────────┐
│ Tier 3: Last Match Placement Points │    │ Tier 3: Best Single Match Kills     │
└──────────────────┬──────────────────┘    └──────────────────┬──────────────────┘
                   │ Tied                                     │ Tied
                   ▼                                          ▼
┌─────────────────────────────────────┐    ┌─────────────────────────────────────┐
│ Tier 4: Last Match Total Damage     │    │ Tier 4: Final Match Total Kills     │
└─────────────────────────────────────┘    └──────────────────┬──────────────────┘
                                                              │ Tied
                                                              ▼
                                           ┌─────────────────────────────────────┐
                                           │ Tier 5: Final Match Finishing Rank  │
                                           └─────────────────────────────────────┘
```

#### Modern Tie-Breaker (Placement-First Hierarchy — mid 2022+)
When two or more teams tie on cumulative total points, the solver evaluates:
1. **Tier 1**: Total Accumulated Placement Points (across all stage matches).
2. **Tier 2**: Most Recent Match — Total Match Points (Placement + Kills).
3. **Tier 3**: Most Recent Match — Placement Points.
4. **Tier 4**: Most Recent Match — Total Damage Dealt.
* **Why Tier 3 and 4 Both Exist**: Teams finishing 9th–16th all receive 0 placement points. If Team A (9th, 2 kills) and Team B (14th, 2 kills) tie on Tier 2 (2 pts) and Tier 3 (0 pts), Tier 4 (Damage) resolves the tie.
* **Recursive Application**: If still tied across all 4 tiers for Match $N$, recursively evaluate Match $N-1$, then Match $N-2$, until resolved.

#### Legacy Tie-Breaker (Kill-First Hierarchy — 2019 to June 2022)
Prior to the June 2, 2022 update, kill volume was prioritized over placement consistency:
1. **Tier 1**: Total Accumulated Kill Points across all matches in the series.
2. **Tier 2**: Highest Total Points earned in a single match within the series.
3. **Tier 3**: Highest Kill Points earned in a single match within the series.
4. **Tier 4**: Total Kill Points in the final match of the series.
5. **Tier 5**: Finishing rank in the final match of the series.

---

### 3.3 The "Most Chicken" (WWCD) Ranking Strategy (2021)

Applied globally during PCS4 and PCS5, this strategy altered the primary objective from cumulative points to match victories:

```
┌────────────────────────────────────────────────────────┐
│ Rank Key 1: Total Number of Chicken Dinners (WWCDs)    │
└───────────────────────────┬────────────────────────────┘
                            │ Tied
                            ▼
┌────────────────────────────────────────────────────────┐
│ Rank Key 2: Total Accumulated Kill Points              │
└───────────────────────────┬────────────────────────────┘
                            │ Tied
                            ▼
┌────────────────────────────────────────────────────────┐
│ Rank Key 3: Finishing Rank in the Final Match          │
└────────────────────────────────────────────────────────┘
```

* **Core Invariant**: A team with 1 WWCD and 2 kills ranks **strictly ahead** of a team with 0 WWCDs and 80 kills.
* **Placement Points Void**: Individual placements 2nd through 16th awarded zero standings credit; only match victory (1st) impacted the primary ranking key.

---

### 3.4 Match Point / Smash Rule Engine (BSC, EWC 2024–2026)

Governs high-stakes climax finals (Battlegrounds Smash Cup, Esports World Cup):

```
                     SMASH RULE ENGINE WORKFLOW
┌──────────────────────────────────────────────────────────────────┐
│ Team Cumulative Points < Point Threshold (e.g. 60 or 70 pts)    │
└─────────────────────────────────┬────────────────────────────────┘
                                  │ Crosses Threshold
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│ SMASH ELIGIBILITY ACTIVATED (Effective starting in NEXT match)   │
└─────────────────────────────────┬────────────────────────────────┘
                                  │ Subsequent Match
                                  ▼
         ┌────────────────────────┴────────────────────────┐
         │ Does Smash-Eligible Team Secure WWCD (1st Place)?│
         └───────────────┬───────────────────┬─────────────┘
                         │ YES               │ NO
                         ▼                   ▼
       ┌────────────────────────┐  ┌───────────────────────────────┐
       │ TOURNAMENT CONCLUDES:  │  │ Continue matches until cap.   │
       │ Team Crowned Champion  │  │ If cap reached, highest total │
       │ Immediately            │  │ points wins (EWC Rule).       │
       └────────────────────────┘  └───────────────────────────────┘
```

1. **Threshold Formulation**: Predefined point target (typically **60 or 70 points**).
2. **Smash Eligibility Invariant**: A team becomes **Smash Eligible** when cumulative points $\ge \text{Threshold}$.
3. **Next-Match Activation Invariant**: Hitting the threshold and securing WWCD in the *same* match does **not** trigger victory; eligibility only takes effect starting in the subsequent match.
4. **Match Cap Fall-Through (The EWC Rule)**: If no eligible team wins a WWCD before the maximum scheduled matches conclude, the team with the highest cumulative total points is crowned Champion *(e.g., Virtus.pro winning EWC 2026)*.
5. **Subsequent Standings (2nd–16th)**: Ranked by cumulative points subject to standard S.U.P.E.R. tie-breakers.

---

## 4. In-Game Elimination Invariants & Player Lifecycle Models

```
┌────────────────────────────────────────────────────────────────────────┐
│                  ELIMINATION LIFECYCLE MODEL CONTRAST                  │
├─────────────────────────┬──────────────────────────────────────────────┤
│ 2019–2025 Era           │ Strictly Single-Life: 64 total lives/match.  │
│ (Historical Standard)   │ No Blue Chip Towers. Death is permanent.     │
├─────────────────────────┼──────────────────────────────────────────────┤
│ 2026 Era                │ Multi-Life Recall Towers active Phase 1–6.   │
│ (Modern Circuit)        │ Deactivates at Phase 7. Multi-kill accounting.│
└─────────────────────────┴──────────────────────────────────────────────┘
```

### 4.1 Historical Single-Life Model (2019–2025)
* **Single-Life Invariant**: Every player possesses exactly **1 life**. The match telemetry contains at most 64 death events.
* **Finality**: When a player is eliminated, their status is immutable. No recall flights or respawn transmitters exist.
* **Kill Accounting**: Exactly 1 kill point is awarded per elimination; no player can be eliminated more than once.

### 4.2 Modern Multi-Life Recall Model (2026)
* **Phase 7 Deactivation Invariant**: At the start of **Phase 7**, all Blue Chip Recall Towers deactivate permanently. Any elimination occurring in Phase 7, 8, or 9 is non-recoverable.
* **Multi-Life Statistics Accounting**:
  * Eliminations are immutable: killer receives +1 kill point immediately.
  * If Player X is recalled and eliminated again, Player X records 2 deaths, and the second killer receives +1 kill point.
  * Recalls never deduct points, erase deaths, or retract kill credits.

### 4.3 Universal Squad Wipe & Placement Invariants
* **Placement Locking**: A squad's match placement is locked **strictly when the entire squad is eliminated** (0 surviving or recallable players).
* **Single Survivor Invariant**: As long as 1 squad member remains alive, the squad's placement continues to advance as other teams wipe.
* **Instant Wipe on Last Man Knocked**: Self-AED is disallowed/unspawned; when the last living member of a squad is knocked down, the entire team is wiped out **instantly** without entering DBNO.
* **Simultaneous Squad Wipe**: If two squads wipe out within the same simulation tick, finishing placement is resolved by the exact millisecond timestamp order (`_D`) in telemetry.
* **Environmental & Friendly Deaths**: Dying to the Bluezone, red zone, fall, or team kill awards **0 kill points** to any team. No negative point deductions exist.

---

## 5. Authoritative Tournament Topologies & Stage Progression

```
                               TOURNAMENT TOPOLOGY CATALOG
  ┌─────────────────────────────────────────────────────────────────────────────────────┐
  │ PART I: MODERN 2026 CIRCUITS                                                        │
  │ • Topology 1: PGS Circuit System 2026 (24 Teams, 3-Week Linked Series)              │
  │ • Topology 2: PEC Championship 2026 (EMEA Regional 3-Day Playoff Funnel)            │
  │ • Topology 3: PGC 2026 (32 Teams, Tiered Entry & 5-Day Survival Ladder)             │
  ├─────────────────────────────────────────────────────────────────────────────────────┤
  │ PART II: HISTORICAL LINEAGE CIRCUITS (2021–2025)                                    │
  │ • Topology 4: PGS 2024–2025 (24 Teams, 3 Groups, Top 16 Finals, Bottom 8 Out)      │
  │ • Topology 5: PEC 2024–2025 Closed Qualifiers (Top 8 Finals, 16 Losers -> 8 Finals) │
  │ • Topology 6: PGC 2025 (32 Teams, Split-Funnel Last Stage, Bangkok)                 │
  │ • Topology 7: PGC 2024 (24 Teams, 3-Tier Daily Waterfall Circuits, Kuala Lumpur)   │
  │ • Topology 8: PGC 2023 (32 Teams, Double Elimination + Last Chance, Bangkok)        │
  │ • Topology 9: PGC 2022 (32 Teams, Double Elimination + 4-Match WWCD Grand Survival) │
  │ • Topology 10: PGC / PGI.S 2021 (32 Teams, Dynamic Waitlist Rolling Survival Ladder)│
  └─────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 5.1 Topology 1: PGS Circuit System 2026 (24 Teams)
Governing the **PUBG Global Series (PGS 2026)**:
* **Capacity**: 24 teams (Global Partner Teams + Regional Qualifiers).
* **Circuit Architecture**: A 3-week progressive circuit divided into three linked Series:

#### Series 1 (Week 1)
1. **Group Stage (1 Day, 3 Groups A, B, C)**: Round-robin (6 matches/team). **Top 16** advance to Winner Bracket; **Bottom 8** drop to Loser Bracket.
2. **Winner Bracket (16 teams, 5 matches)**: **Top 8** advance to Series 1 Final; **Bottom 8** drop to Loser Bracket.
3. **Loser Bracket (16 teams, 5 matches)**: Composed of 8 from Group Stage + 8 from Winner Bracket. **Top 8** advance to Series 1 Final; **Bottom 8 eliminated from Series 1** (seeded into Series 2 Loser Bracket).
4. **Series 1 Final (16 teams, 10 matches over 2 days)**: Awards Series 1 Circuit Points.

#### Series 2 (Week 2)
1. **Winner Bracket (16 teams, 5 matches)**: Composed of the 16 finalists from Series 1 Final. **Top 8** to Series 2 Final; **Bottom 8** drop to Loser Bracket.
2. **Loser Bracket (16 teams, 5 matches)**: Composed of 8 waiting teams + 8 dropping teams. **Top 8** to Series 2 Final; **Bottom 8 eliminated from Series 2**.
3. **Series 2 Final (16 teams, 10 matches over 2 days)**: Awards Series 2 Circuit Points.

#### Series Final / Grand Finals (Week 3)
1. **Cumulative Point Seeding**: Series 1 + Series 2 Circuit Points determine standings:
   * **Top 8 Teams**: Qualify **DIRECTLY to Grand Finals**.
   * **Ranks 9–24 (16 teams)**: Enter Week 3 Loser Bracket.
2. **Week 3 Loser Bracket (16 teams, 5 matches)**: **Top 8** advance to Grand Finals; **Bottom 8 eliminated**.
3. **Grand Finals (16 teams, 15 matches over 3 days, 5 matches/day)**: 8 Direct Qualifiers + 8 Loser Qualifiers determine the Circuit Champion.

---

### 5.2 Topology 2: PEC Championship 2026 (EMEA Regional)
Governing regional Tier-1 championships in EMEA:

#### 1. The Weekly Cups Funnel (Weeks 1–5)
* 5 Weekly Cups establish cumulative Cup Leaderboard. Direct seeds into Playoffs Day 1: **Winner of Cup 4** and **Winner of Cup 5**.

#### 2. The 3-Day Playoff Funnel (16 Teams per Day)
* **Playoffs Day 1 (16 teams)**: 8 Invited Partners + 2 Cup Winners + Top 6 Cup Leaderboard.  
  ➔ **Top 8 advance to Grand Finals**. Bottom 8 drop to Day 2.
* **Playoffs Day 2 (16 teams)**: 8 dropping from Day 1 + Next 8 from Cup Leaderboard.  
  ➔ **Top 5 advance to Grand Finals**. Bottom 11 drop to Day 3.
* **Playoffs Day 3 (16 teams)**: 11 dropping from Day 2 + Next 5 from Cup Leaderboard.  
  ➔ **Top 3 advance to Grand Finals**. Remaining 13 eliminated.

#### 3. Grand Finals (16 Teams, 15 Matches)
* Finalists: $8 \text{ (Day 1)} + 5 \text{ (Day 2)} + 3 \text{ (Day 3)} = \mathbf{16\text{ teams}}$ (5 matches/day over 3 days).

---

### 5.3 Topology 3: PGC 2026 (Tiered Dynamic Entry & Survival Ladder)
Governing the pinnacle **PUBG Global Championship 2026** in İstanbul (32 teams, 9 match days):

```
                              PGC 2026 TIERED ENTRY ARCHITECTURE
   ┌────────────────────────────────────────────────────────┐
   │ 8 Direct Grand Finals Seeds                            │ ───────────────────────────────────┐
   │ • 1 Host Invite (Turkey)                               │                                    │
   │ • 1st place of PGS, PCL, PEC, PAS, PWS, PTS, PVS (7)   │                                    │
   └────────────────────────────────────────────────────────┘                                    │
                                                                                                 ▼
   ┌────────────────────────────────────────────────────────┐                   ┌──────────────────────────────────┐
   │ 8 Survival Stage Direct Seeds                          │ ──► ┌───────────┐ │          GRAND FINALS            │
   │ • 2nd place of all 7 circuit points (7 teams)          │     │           │ │           (16 Teams)             │
   │ • 1st place of Asia-Pacific PMS (1 team)               │     │ SURVIVAL  │ │  • 8 Direct Seeds                │
   └────────────────────────────────────────────────────────┘     │   STAGE   │ │  • 8 Survival Stage Qualifiers   │
                                                                  │           │ │    (4 Daily + 4 Final Day)       │
   ┌────────────────────────────────────────────────────────┐     │  (5 Days, │ │  • 3 Days, 5 matches/day         │
   │ 16 Qualifying Stage Teams                              │     │ 16 tm/day,│ │    (15 matches total)            │
   │ • 3rd-8th of PGS (6 teams)                             │     │ 5 games/d)│ └──────────────────────────────────┘
   │ • 3rd-4th of PCL, PEC, PAS (6 teams)                   │ ──► │           │                  ▲
   │ • 3rd of PWS, PTS, PVS (3 teams)                       │     └─────┬─────┘                  │
   │ • 2nd of Asia-Pacific PMS (1 team)                     │           │ 8 Qualifiers (4+4)     │
   └────────────────────────────────────────────────────────┘           └────────────────────────┘
```

* **Stage 1: Qualifying Stage (1 Day, 5 Matches, 16 Teams)**: Top 8 $\rightarrow$ Survival Day 1; Bottom 8 $\rightarrow$ Survival Day 2. Zero teams eliminated.
* **Stage 2: Survival Stage (5 Days, 16 Teams/Day, 5 Matches/Day)**:
  * **Day 1**: 8 Direct Seeds + 8 Top Qualifying Teams. **1st place advances to Grand Finals** (Qualifier #1); 2nd–9th to Day 2; 10th–16th to Day 3.
  * **Day 2**: 8 from Day 1 + 8 Bottom Qualifying Teams. **1st place advances to Grand Finals** (Qualifier #2); 2nd–10th to Day 3; 11th–16th to Day 4.
  * **Day 3**: 9 from Day 2 + 7 from Day 1. **1st place advances to Grand Finals** (Qualifier #3); 2nd–11th to Day 4; others wait for Day 4 aggregation.
  * **Day 4**: 10 from Day 3 + 6 from Day 2. **1st place advances to Grand Finals** (Qualifier #4).
  * **Post-Day 4 Cut**: Remaining teams aggregated. Top 16 proceed to Final Day; Bottom 4 eliminated (29th–32nd).
  * **Final Day (Day 5, 16 Teams, 5 Matches)**: **Top 4 advance to Grand Finals** (Qualifiers #5–#8); Bottom 12 eliminated (17th–28th).
* **Stage 3: Grand Finals (16 Teams, 15 Matches over 3 Days)**: 8 Direct Seeds + 8 Survival Qualifiers determine the Champion.

---

### 5.4 Topology 4: PGS 2024–2025 Circuit Topology (24 Teams)
Governing the standard PUBG Global Series format across the 2024 and 2025 seasons:

```
┌────────────────────────────────────────────────────────────────────────┐
│ GROUP STAGE (24 Teams: Groups A, B, C of 8 teams each)                │
│ • Round-Robin: A vs B, B vs C, A vs C (3 Days, 6 matches/day = 18 total)│
│ • Each team plays exactly 12 matches under standard S.U.P.E.R.         │
├────────────────────────────────────────────────────────────────────────┤
│ ➔ TOP 16 TEAMS ─────────────► ADVANCE DIRECTLY TO GRAND FINALS         │
│ ➔ BOTTOM 8 TEAMS (17th–24th) ► ELIMINATED ("BYE-BYE")                 │
└──────────────────────────────────────┬─────────────────────────────────┘
                                       │ 16 Qualifiers
                                       ▼
┌────────────────────────────────────────────────────────────────────────┐
│ GRAND FINALS (16 Teams, 18 Matches over 3 Days, 6 matches/day)         │
│ • Winner crowned PGS Champion                                          │
└────────────────────────────────────────────────────────────────────────┘
```

* **Advancement Invariant**: Pure single-stage cut. Zero lower brackets or second-chance lifelines.

---

### 5.5 Topology 5: PEC 2024–2025 Closed Qualifier Topology (24 Teams)
Governing the regional EMEA closed qualifier circuit in 2024–2025:

```
┌────────────────────────────────────────────────────────────────────────┐
│ GROUP STAGE (24 Teams: 3 Groups of 8 Round-Robin, 12 matches/team)     │
├────────────────────────────────────────────────────────────────────────┤
│ ➔ TOP 8 TEAMS ─────────────────────────► DIRECT TO GRAND FINALS        │
│ ➔ RANKS 9th–24th (16 Teams) ───────────► DROP TO LAST CHANCE / LOSERS  │
└──────────────────────────────────────────────┬─────────────────────────┘
                                               │ 16 Teams
                                               ▼
┌────────────────────────────────────────────────────────────────────────┐
│ LAST CHANCE / LOSERS BRACKET (16 Teams, 12 Matches over 2 Days)        │
├────────────────────────────────────────────────────────────────────────┤
│ ➔ TOP 8 TEAMS ─────────────────────────► ADVANCE TO GRAND FINALS       │
│ ➔ BOTTOM 8 TEAMS (Ranks 9th–16th) ─────► ELIMINATED                    │
└──────────────────────────────────────────────┬─────────────────────────┘
                                               │ 8 Qualifiers
                                               ▼
┌────────────────────────────────────────────────────────────────────────┐
│ GRAND FINALS (16 Teams: 8 Group Stage + 8 Last Chance, 15 Matches)     │
└────────────────────────────────────────────────────────────────────────┘
```

---

### 5.6 Topology 6: PGC 2025 Split-Funnel Topology (32 Teams, Bangkok)
Governing the 2025 World Championship under S.U.P.E.R. v5.0.5:

```
┌────────────────────────────────────────────────────────────────────────┐
│ GROUP STAGE (32 Teams: Group A [16] & Group B [16], 18 matches each)   │
├────────────────────────────────┬───────────────────────────────────────┤
│ Group A (18 matches):          │ Group B (18 matches):                 │
│ • Top 5 (5 teams) ────────────┼─┐ Top 5 (5 teams) ────────────────────┐│
│ • Middle 8 (Ranks 6–13) ─────┐│ │ • Middle 8 (Ranks 6–13) ───────────┐││
│ • Bottom 3 (Ranks 14–16)     ││ │ • Bottom 3 (Ranks 14–16)           │││
│   ──► ELIMINATED (6 teams)   ││ │   ──► ELIMINATED                   │││
└──────────────────────────────┼┼─┴────────────────────────────────────┼┼┘
                               ││                                      ││
                               ││ 16 Middle Teams                      ││ 10 Direct
                               ▼▼                                      ││ Seeds
┌────────────────────────────────────────────────────────┐             ││
│ LAST STAGE (16 Teams: 8 from Grp A + 8 from Grp B)     │             ││
│ • 18 Matches over 3 days (6 matches/day)               │             ││
│ • Top 5 Teams Advance ───────────────────────────────┐ │             ││
│ • Bottom 11 Teams (Ranks 6th–16th) ──► ELIMINATED    │ │             ││
└──────────────────────────────────────────────────────┼─┘             ││
                                                       │ 5 Qualifiers  ││
                                                       ▼               ▼▼
┌────────────────────────────────────────────────────────────────────────┐
│ GRAND FINALS (16 Teams: 10 Group + 5 Last Stage + 1 Host Wildcard)     │
│ • 18 Matches over 3 days under S.U.P.E.R. points                       │
│ • Host Wildcard: FULL SENSE (Thailand)                                 │
└────────────────────────────────────────────────────────────────────────┘
```

* **Group Stage Elimination Invariant**: Bottom 3 teams of each group (6 teams total) are eliminated immediately without entering the Last Stage.

---

### 5.7 Topology 7: PGC 2024 Waterfall Circuit System (24 Teams, Kuala Lumpur)
Governing the 2024 World Championship across three progressive circuits:

```
PGC 2024 Single Circuit Progression (Repeats for Circuit 1, 2, and 3):
┌────────────────────────────────────────────────────────────────────────┐
│ DAY 1 (16 Teams: Seeds 9th–24th, 6 matches)                            │
│ ➔ Top 12 Advance to Day 2       │ ➔ Bottom 4 Eliminated from Circuit   │
└───────────────────────────────┬────────────────────────────────────────┘
                                │ 12 Teams
                                ▼
┌────────────────────────────────────────────────────────────────────────┐
│ DAY 2 (16 Teams: 12 from Day 1 + Seeds 5th–8th, 6 matches)             │
│ ➔ Top 12 Advance to Day 3       │ ➔ Bottom 4 Eliminated from Circuit   │
└───────────────────────────────┬────────────────────────────────────────┘
                                │ 12 Teams
                                ▼
┌────────────────────────────────────────────────────────────────────────┐
│ DAY 3: CIRCUIT FINAL (16 Teams: 12 from Day 2 + Seeds 1st–4th, 6 match)│
│ ➔ INVARIANT: Only Day 3 points accumulate on Circuit Leaderboard!      │
└────────────────────────────────────────────────────────────────────────┘
                                │ After Circuits 1, 2, 3:
                                ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Cumulative 3-Circuit Leaderboard:                                      │
│ • Top 16 ──► Qualify for Grand Finals (18 matches, S.U.P.E.R. Points)  │
│ • Bottom 8 (Ranks 17th–24th) ──► Eliminated from PGC 2024              │
└────────────────────────────────────────────────────────────────────────┘
```

* **Point Reset Invariant**: Day 1 and Day 2 matches are strict qualification gates; zero points from Days 1 and 2 carry forward. Only points scored on Day 3 count toward Grand Finals qualification.
* **Dynamic Seeding**: Circuit 1 seeded by PGS Points; Circuits 2 and 3 seeded by final placements of the preceding circuit.

---

### 5.8 Topology 8: PGC 2023 Double Elimination with Last Chance (32 Teams, Bangkok)
Governing the 2023 World Championship:

```
┌────────────────────────────────────────────────────────────────────────┐
│ GROUP STAGE (32 Teams: Group A [16] & Group B [16], 12 matches each)   │
├────────────────────────────────────────────────────────────────────────┤
│ ➔ Top 8 from each group (16 teams) ──► Advance to WINNERS BRACKET      │
│ ➔ Bottom 8 from each group (16 teams) ► Advance to LOSERS BRACKET      │
└──────────────────┬─────────────────────────────────┬───────────────────┘
                   │                                 │
                   ▼                                 ▼
┌────────────────────────────────────┐ ┌─────────────────────────────────┐
│ WINNERS BRACKET (16 Teams, 12 gms) │ │ LOSERS BRACKET (16 Teams, 12 gms│
├────────────────────────────────────┤ ├─────────────────────────────────┤
│ • Top 8 ──► DIRECT TO GRAND FINALS │ │ • Top 8 ──► Advance to LAST     │
│ • Bottom 8 ──► Drop to LAST CHANCE │ │             CHANCE              │
└──────────────────┬─────────────────┘ │ • Bottom 8 ──► ELIMINATED       │
                   │                   └─────────────┬───────────────────┘
                   │ 8 Teams                         │ 8 Teams
                   └─────────────────┬───────────────┘
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│ LAST CHANCE (16 Teams: 8 Winners Bracket + 8 Losers Bracket, 12 games) │
├────────────────────────────────────────────────────────────────────────┤
│ ➔ Top 8 Teams ─────────────────────────► ADVANCE TO GRAND FINALS       │
│ ➔ Bottom 8 Teams ──────────────────────► ELIMINATED                    │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │ 8 Qualifiers
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│ GRAND FINALS (16 Teams: 8 Winners Bracket + 8 Last Chance, 18 matches) │
└────────────────────────────────────────────────────────────────────────┘
```

---

### 5.9 Topology 9: PGC 2022 Double Elimination + Grand Survival (32 Teams, Dubai)
Governing the 2022 World Championship:
* **Group Stage (32 teams, 2 groups of 16, 15 matches each)**: Top 8 from each $\rightarrow$ Winners Bracket; Bottom 8 from each $\rightarrow$ Losers Bracket 1.
* **Winners Bracket (16 teams, 10 matches)**: **Top 8 $\rightarrow$ Grand Finals**; Bottom 8 $\rightarrow$ Losers Bracket 2.
* **Losers Bracket 1 (16 teams, 10 matches)**: **Top 8 $\rightarrow$ Losers Bracket 2**; Ranks 9th–15th $\rightarrow$ Grand Survival; **16th place eliminated**.
* **Losers Bracket 2 (16 teams, 10 matches)**: **Top 4 $\rightarrow$ Grand Finals**; Bottom 12 $\rightarrow$ Grand Survival.
* **Grand Survival (19 Teams, 4 Matches)**:
  * Played under **WWCD (Most Chicken) rules**.
  * Matches 1–4: The WWCD winner of each match immediately qualifies for Grand Finals ($4\text{ teams}$).
  * The 15 non-winning teams are **eliminated**.
* **Grand Finals (16 Teams, 15 Matches)**: 8 Winners + 4 Losers 2 + 4 Grand Survival = 16 teams.

---

### 5.10 Topology 10: PGC / PGI.S 2021 Dynamic Waitlist Rolling Ladder

Governing the 2021 global championship qualification system:

```
                            ROLLING BACKFILL QUEUE STATE MACHINE
   ┌───────────────────┐
   │ WAITLIST_PENDING  │ ◄── Initial Queue (Seeds 17th–32nd from Rank Decision)
   └─────────┬─────────┘
             │ Vacancy Created (Team wins WWCD)
             ▼
   ┌───────────────────┐               WWCD Match Win
   │   ACTIVE_LOBBY    │ ───────────────────────────────────────────► ┌───────────────────┐
   │ (Fixed 16 Teams)  │                                              │  QUALIFIED_EXIT   │
   └─────────┬─────────┘                                              │  (Weekly Finals)  │
             │ Match 16 Concludes without WWCD                        └───────────────────┘
             ▼
   ┌───────────────────┐
   │  STAGE_EXCLUDED   │
   │  (Bottom 16 Stage)│
   └───────────────────┘
```

#### Queue Transition Invariants:
1. **Capacity Invariant**: The `ACTIVE_LOBBY` strictly maintains exactly 16 teams.
2. **Immediate Qualification Exit**: When a team achieves a WWCD, its state transitions to `QUALIFIED_EXIT`. It leaves the lobby immediately and does not play further matches in that Weekly Survival.
3. **Queue Ingestion Invariant**: The team at the head of `WAITLIST_PENDING` (determined by the prior Rank Decision or Weekly Finals seed) is popped and promoted to `ACTIVE_LOBBY` to fill the vacant slot for the next match.
4. **Finite Survival Horizon**: Weekly Survival consists of exactly **16 matches**. Exactly 16 teams qualify for the Weekly Finals. The remaining 16 non-qualified teams transition to `STAGE_EXCLUDED` (Bottom 16 stage).

---

### 5.11 Qualification Cut-Off Zones & Clinch Mathematical Invariants
Every Stage defines ordered `QualificationZone` records:
* `rankStart` to `rankEnd` (e.g. 1 to 8 vs 9 to 16).
* `disposition`: `ADVANCE_GRAND_FINALS`, `ADVANCE_WINNERS`, `DROP_LOSERS`, `DROP_LAST_CHANCE`, `ELIMINATED`.

#### Clinch Condition Algorithm (The "Magic Number")
Let:
* $R_{\text{cut}}$ = The cut-off rank boundary (e.g., Rank 8 for qualification).
* $M_{\text{rem}}$ = Number of matches remaining for trailing teams.
* $P_{\text{max}}$ = Practical single-match point ceiling ($10\text{ placement} + 20\text{ kills} = 30\text{ pts}$).
* $S_i$ = Current total score of Team $i$.
* $S_{\text{bubble}}$ = Current score of the team occupying Rank $R_{\text{cut}} + 1$ (the first non-qualifying team).

$$\text{Team } i \text{ has mathematically Clinched if: } S_i > S_{\text{bubble}} + (M_{\text{rem}} \times P_{\text{max}})$$

When this condition is satisfied, the team displays an immutable **`CLINCHED`** badge on the live leaderboard.

---

## 6. Telemetry Reducer Integration

The ingestion and translation of raw Krafton telemetry events into this domain model is formally contracted in:
➡️ [`docs/pubg-telemetry-event-contract.md`](file:///D:/MyProjects/Java/deadzone-esports/docs/pubg-telemetry-event-contract.md)

### Multi-Era Telemetry Reducer Expectations:
* **Eliminations & Knocks**: `LogPlayerMakeGroggy` and `LogPlayerKillV2` feed Section 3 (Scoring) and Section 4.3 (Squad Wipe).
* **Recall Lifecycle Flag**: In 2026 matches, `LogPlayerRevive` with Recall event flags tracks multi-life respawns up to Phase 7 (`LogGameStatePeriodic`). In 2019–2025 matches, telemetry parsers enforce strict single-life invariants.
* **Damage Aggregation**: `LogPlayerTakeDamage` feeds Tier 4 Tie-Breakers (Section 3.2).
* **Match Roster Mapping**: Telemetry `MatchId` links to `Stage` topology to evaluate stage qualification and dynamic queue promotions.
