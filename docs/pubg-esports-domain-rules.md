# PUBG Esports Domain Rules & Competition Specification

> **Document Version**: 2.1.0 (Modern Competitive Standard & 2026 Circuit Formats)  
> **Status**: Approved & Authoritative  
> **Target Systems**: `deadzone-esports` Domain Core, Ingestion Engine & Leaderboard Services  
> **Companion Document**: [`docs/pubg-telemetry-event-contract.md`](file:///D:/MyProjects/Java/deadzone-esports/docs/pubg-telemetry-event-contract.md)

---

## 1. Executive Summary & Scope

This specification defines the authoritative competitive rules, tournament stage topologies, scoring algorithms, and domain invariants governing modern professional PUBG Esports (Standard and Universal PUBG Esports Ruleset — S.U.P.E.R.).

It acts as the single source of truth for the `deadzone-esports` platform, driving:
1. **Competition Data Modeling** (`Tournament`, `Stage`, `MatchDay`, `Match`, `Roster`, `TeamSlot` 1–16).
2. **Official S.U.P.E.R. Scoring & Tie-Breaker Solver**.
3. **EWC / Smash Rule Match Point Engine**.
4. **Authoritative Tournament Topologies & Progression Funnels** (**PGS**, **PEC**, and **PGC 2026**).
5. **Multi-Life Recall Mechanics & Squad Extinction Invariants**.

> [!NOTE]
> **MVP Scope Boundary**: The MVP focuses strictly on intra-tournament and intra-stage calculations (match telemetry processing, stage standings, rank deltas, bracket cut-offs, and single-tournament progression). Global cross-tournament annual leaderboards (e.g. cumulative multi-event annual PGC/PGS points tables) and cross-regional trickle-down allocations are defined conceptually for seeding context but are excluded from MVP automated calculation.

---

## 2. Ubiquitous Domain Terminology

| Domain Term | Definition | Invariants & Business Rules |
| :--- | :--- | :--- |
| **S.U.P.E.R.** | Standard and Universal PUBG Esports Ruleset | Official Krafton regulatory framework standardizing match settings, point tables, and tie-breakers. |
| **Lobby Slot** | Fixed integer index (1 through 16) | Standard competitive PUBG lobbies strictly host **16 teams** (4 players per squad, 64 players total). Custom match lobby slots (1–16) map directly to registered tournament teams. |
| **WWCD** | "Winner Winner Chicken Dinner" | Finishing 1st place in an individual match (awards 10 placement points under S.U.P.E.R.). |
| **DBNO** | "Down But Not Out" (Knock) | State where a player sustains fatal damage while at least one squad teammate remains alive. |
| **Smash Rule** | Match Point tournament format | Stage format where reaching a points threshold qualifies a team for match point; winning a WWCD in a subsequent match wins the championship. |
| **Recall Tower** | Blue Chip Recall Station | In-game station allowing surviving players to respawn eliminated teammates. **Permanently deactivates at the start of Phase 7**. |
| **Cut-Off Line** | Qualification threshold boundary | Rank divider in a leaderboard delineating advancing, demoting, or eliminated zones. |
| **Clinch** | Mathematically secured qualification | State where a team's cumulative point lead over the cut-off rank exceeds the maximum points any trailing team can mathematically earn in remaining matches. |
| **Invited vs. Qualified** | Team Enrollment Origin | Distinguishes whether a team enters via direct seed/partner status (`GLOBAL_PARTNER`, `REGIONAL_PARTNER`, `SPECIAL_INVITE`) or earned qualification (`QUALIFIED_REGIONAL`, `QUALIFIED_CUP`). |

---

## 3. Official Scoring Engines

### 3.1 Standard S.U.P.E.R. Scoring Matrix
For every competitive match, the engine evaluates points using the official 10-point scale:

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

### 3.2 Official S.U.P.E.R. 4-Tier Tie-Breaker Hierarchy
When two or more teams tie on cumulative total points at the conclusion of a stage (or match day), the deadlock is broken strictly by evaluating the following 4-tier hierarchy:

```
┌────────────────────────────────────────────────────────────────────────┐
│ Tier 1: Total Accumulated Placement Points (across all stage matches)  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Tied
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Tier 2: Most Recent Match — Total Match Points (Placement + Kills)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Tied
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Tier 3: Most Recent Match — Placement Points                           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Tied
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Tier 4: Most Recent Match — Total Damage Dealt                         │
└────────────────────────────────────────────────────────────────────────┘
```

#### Why Tier 3 and Tier 4 Both Exist
In S.U.P.E.R., Tier 3 evaluates **Placement Points**, *not* finishing rank:
* **The Zero-Point Equality**: Any team finishing between 9th and 16th place receives exactly **0 placement points**.
* **The One-Point Equality**: Both 7th and 8th place receive exactly **1 placement point**.
* **Scenario**: If Team A finishes 9th with 2 kills (Total Match Points = 2, Placement Points = 0) and Team B finishes 14th with 2 kills (Total Match Points = 2, Placement Points = 0):
  * **Tier 2** is tied (both have 2 total match points).
  * **Tier 3** is tied (both have 0 placement points).
  * **Tier 4 (Total Damage Dealt)** breaks the deadlock.
* **Recursive Application**: If two teams remain tied across all 4 criteria for the most recent match (Match $N$), the solver recursively applies Tiers 2, 3, and 4 to the second most recent match (Match $N-1$), then Match $N-2$, until the tie is resolved.

---

### 3.3 The Smash Rule (Match Point Format)
The Smash Rule governs high-stakes climax stages (e.g. Esports World Cup — EWC, Battlegrounds Smash Cup):

1. **Threshold Formulation**:
   * A predefined point target (typically **60 or 70 points**), or dynamic target configured prior to the final match day.
2. **Smash Eligibility**:
   * A team becomes **Smash Eligible** the moment its cumulative total points $\ge \text{Threshold}$.
3. **The Victory Condition**:
   * A Smash-Eligible team must secure a **1st Place finish (WWCD)** in a **subsequent match** to win the championship and conclude the stage immediately.
   * *The Same-Match Invariant*: Crossing the threshold and winning the WWCD in the *same* match does **not** trigger victory; eligibility only takes effect starting in the *next* match.
4. **Scheduled Match Cap Fall-Through (The EWC Rule)**:
   * Every tournament stage defines a standard scheduled match allocation (e.g., 5 or 6 matches per day).
   * **If no eligible team achieves a WWCD within the scheduled matches of that stage/day, the tournament concludes at the match cap, and the team with the highest cumulative total points is crowned Champion** *(e.g., Virtus.pro winning EWC 2026)*.
5. **Subsequent Standings (2nd – 16th)**:
   * Placements 2nd through 16th are ordered strictly by total cumulative points, subject to standard S.U.P.E.R. tie-breakers.

---

## 4. In-Game Competitive Invariants & Elimination Mechanics

### 4.1 Blue Chip Recall Towers & Phase 7 Deactivation
* **Active Status**: Blue Chip Recall Towers are active during early and mid-match play.
* **Phase 7 Cut-Off**: At the start of **Phase 7** (when the final recall flight appears), all Recall Towers and transmitters are permanently deactivated. Any death occurring in Phase 7, 8, or 9 is non-recoverable.
* **Multi-Life Statistics Accounting**:
  * Every confirmed kill is permanent and immutable. If Player X is eliminated, the killer receives +1 kill point immediately.
  * If Player X is subsequently recalled and eliminated a second time, Player X records 2 deaths, and the second killer receives another +1 kill point.
  * Recalls do *not* deduct points, erase deaths, or retract kill credits.

### 4.2 Squad Wipe & Placement Rank Determination
* **Team Placement Invariant**: A team's match placement is locked **strictly when the entire squad is eliminated** (0 surviving or recallable players).
* **Single Survivor Survival**: As long as 1 squad member remains alive, the team's placement continues to rise as other squads are wiped out.
* **Instant Squad Wipe on Last Man Knocked**: Because Self-AED is deleted from the game, when the final living member of a squad is knocked down, the entire team is wiped out **instantly** without entering DBNO.
* **Simultaneous Squad Wipe**: If two squads are wiped out within the same game tick, finishing placement is resolved by the exact millisecond timestamp order recorded in telemetry (`_D`).

### 4.3 Environmental, Bluezone & Team Deaths
* **Tactical Bluezone / Fall / Redzone Deaths**:
  * Dying to the Bluezone, Red Zone artillery, or falling without an active opponent knock awards **0 kill points** to any team.
  * No negative point penalties exist on the scoreboard.
* **Friendly Fire (Team Kills)**:
  * Eliminating a teammate awards **0 kill points** and does not increment kill counts.

---

## 5. Authoritative Tournament Topologies & Stage Progression

```
                             TOURNAMENT TOPOLOGY CATALOG
 ┌──────────────────────────┐  ┌──────────────────────────┐  ┌──────────────────────────┐
 │ 1. PGS Circuit System    │  │ 2. PEC Championship      │  │ 3. PGC 2026 Tiered Entry │
 │    (24 Teams)            │  │    (EMEA Regional)       │  │    (32 Teams)            │
 │ • 3-Week Circuit         │  │ • 5 Weekly Cups Funnel   │  │ • Qualifying Stage (16)  │
 │ • Series 1 (Round-Robin) │  │ • 3-Day Playoff Funnel   │  │ • Survival Ladder (5 days│
 │ • Series 2 (Brackets)    │  │   (8+5+3 = 16 teams)     │  │   16 teams/day)          │
 │ • Series Final (15 games)│  │ • 15-Game Grand Finals   │  │ • Grand Finals (16 teams)│
 └──────────────────────────┘  └──────────────────────────┘  └──────────────────────────┘
```

---

### 5.1 Topology 1: PGS Circuit System (24 Teams)
Governing the **PUBG Global Series (PGS)**:
* **Capacity**: 24 teams (Global Partner Teams + Regional Qualifiers).
* **Circuit Architecture**: A 3-week progressive circuit divided into three linked Series:

#### Series 1 (Week 1)
1. **Group Stage (1 Day, 3 Groups A, B, C)**:
   * Round-robin matches (A vs B, B vs C, A vs C); each team plays exactly 6 matches.
   * **Top 16** advance to **Series 1 Winner Bracket**.
   * **Bottom 8 (Ranks 17–24)** drop to **Series 1 Loser Bracket**.
2. **Winner Bracket (16 teams, 5 matches)**:
   * **Top 8** advance to **Series 1 Final**.
   * **Bottom 8 (Ranks 9–16)** drop to **Series 1 Loser Bracket**.
3. **Loser Bracket (16 teams, 5 matches)**:
   * Composed of 8 teams from Group Stage + 8 teams dropping from Winner Bracket.
   * **Top 8** advance to **Series 1 Final**.
   * **Bottom 8 are eliminated from Series 1** (and seeded into Series 2 Loser Bracket).
4. **Series 1 Final (16 teams, 10 matches over 2 days, 5 matches/day)**:
   * Final standings award **Series 1 Circuit Points**.

#### Series 2 (Week 2)
1. **Winner Bracket (16 teams, 5 matches)**:
   * Composed of the **16 finalists from Series 1 Final**.
   * **Top 8** advance to **Series 2 Final**.
   * **Bottom 8** drop to **Series 2 Loser Bracket**.
2. **Loser Bracket (16 teams, 5 matches)**:
   * Composed of 8 waiting teams from Series 1 + 8 teams dropping from Series 2 Winner Bracket.
   * **Top 8** advance to **Series 2 Final**.
   * **Bottom 8 are eliminated from Series 2**.
3. **Series 2 Final (16 teams, 10 matches over 2 days, 5 matches/day)**:
   * Final standings award **Series 2 Circuit Points**.

#### Series Final / Grand Finals (Week 3)
1. **Seeding Qualification**:
   * Cumulative Circuit Points from Series 1 Final + Series 2 Final determine circuit standings:
   * **Top 8 Teams** qualify **DIRECTLY to Grand Finals**!
   * **Remaining 16 Teams (Ranks 9–24)** enter the **Week 3 Loser / Survival Bracket**.
2. **Week 3 Loser Bracket (16 teams, 5 matches)**:
   * **Top 8** claim the final 8 spots in the Grand Finals.
   * **Bottom 8 are eliminated**.
3. **Grand Finals (16 teams, 15 matches over 3 days, 5 matches/day)**:
   * 8 Direct Point Qualifiers + 8 Loser Bracket Qualifiers = **16 teams**.
   * Winner crowned **PGS Circuit Champion**.
   * *Dual-Use Points Invariant*: Points earned across the circuit serve a dual purpose: ranking teams within the circuit (Top 8 seed) and accumulating on the annual global PGS Points leaderboard.

---

### 5.2 Topology 2: PEC (PUBG EMEA Championship — Spring & Fall)
Governing regional Tier-1 championships in EMEA:

#### 1. The Weekly Cups Funnel (Weeks 1–5)
* 5 Weekly Cups establish the cumulative **PEC Cup Leaderboard**.
* Direct seeds into Playoffs Day 1: **Winner of Cup 4** and **Winner of Cup 5**.

#### 2. The 3-Day Playoff Funnel / Closed Qualifiers (16 Teams per Day)
* **Playoffs Day 1 (16 teams)**:
  * 8 Invited Regional Partners *(plus 1 Special Invite: Team Nemesis in Fall)*.
  * 2 Direct Cup Winners (Cups 4 & 5).
  * Top 6 *(Top 5 in Fall)* from Cup Leaderboard.
  * ➔ **Top 8 advance to Grand Finals**. Bottom 8 drop to Day 2.
* **Playoffs Day 2 (16 teams)**:
  * 8 teams dropping from Day 1.
  * Next 8 teams from the Cup Leaderboard (Ranks 7th–14th in Spring).
  * ➔ **Top 5 advance to Grand Finals**. Bottom 11 drop to Day 3.
* **Playoffs Day 3 (16 teams)**:
  * 11 teams dropping from Day 2.
  * Next 5 teams from the Cup Leaderboard (Ranks 15th–19th in Spring).
  * ➔ **Top 3 advance to Grand Finals**. Remaining 13 teams are eliminated.

#### 3. Grand Finals (16 Teams, 15 Matches)
* Finalists: $8 \text{ (Day 1)} + 5 \text{ (Day 2)} + 3 \text{ (Day 3)} = \mathbf{16\text{ teams}}$.
* 3 match days playing **5 matches per day** (total of 15 matches).
* The format repeats in **Stage 2**; cumulative PGC Points across both finals decide regional qualification standing.

---

### 5.3 Topology 3: PGC 2026 (Tiered Dynamic Entry & Survival Ladder)
Governing the pinnacle **PUBG Global Championship 2026** in İstanbul (32 teams, 9 match days, 5 matches per day):

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

#### Stage 1: Qualifying Stage (Dec 01 — 1 Day, 5 Matches, 16 Teams)
* 16 teams compete over 5 matches.
* **Advancement Invariant**: **Zero teams eliminated**.
  * **Top 8** advance to **Survival Stage — Day 1**.
  * **Bottom 8** proceed to **Survival Stage — Day 2**.

#### Stage 2: Survival Stage (Dec 02–06 — 5 Days, 16 Teams/Day, 5 Matches/Day)
* **Day 1 (16 teams)**:
  * 8 Direct Seeds (2nd of PGS, PCL, PEC, PAS, PWS, PTS, PVS + 1st of PMS) + 8 Top Teams from Qualifying Stage.
  * **1st Place advances DIRECTLY to Grand Finals** (Qualifier #1).
  * 2nd – 9th Place (8 teams) proceed to Day 2.
  * Bottom 7 (Ranks 10th–16th) proceed to Day 3.
* **Day 2 (16 teams)**:
  * 8 teams from Day 1 + 8 Bottom Teams from Qualifying Stage.
  * **1st Place advances DIRECTLY to Grand Finals** (Qualifier #2).
  * 2nd – 10th Place (9 teams) proceed to Day 3.
  * Bottom 6 (Ranks 11th–16th) proceed to Day 4.
* **Day 3 (16 teams)**:
  * 9 teams from Day 2 + 7 teams from Day 1.
  * **1st Place advances DIRECTLY to Grand Finals** (Qualifier #3).
  * 2nd – 11th Place (10 teams) proceed to Day 4.
  * Remaining teams wait for post-Day 4 aggregation.
* **Day 4 (16 teams)**:
  * 10 teams from Day 3 + 6 teams from Day 2.
  * **1st Place advances DIRECTLY to Grand Finals** (Qualifier #4).
* **Survival Final Day Transition (After Day 4)**:
  * The 4 daily champions have locked their Grand Finals berths.
  * Cumulative performance across the remaining teams determines:
    * **Top 16 proceed to the Final Day**.
    * **Bottom 4 are eliminated** (Tournament Ranks 29th–32nd).
* **Final Day (Day 5 of Survival Stage — 16 Teams, 5 Matches)**:
  * **Top 4 advance to Grand Finals** (Qualifiers #5, #6, #7, #8).
  * **Bottom 12 are eliminated** (Tournament Ranks 17th–28th).

#### Stage 3: Grand Finals (Dec 11–13 — 3 Days, 15 Matches total, 5 per Day)
* **16 teams**:
  * **8 Direct Seeds**: 1 Host Invite (Turkey) + 7 Regional/PGS Champions (1st of PGS, PCL, PEC, PAS, PWS, PTS, PVS).
  * **8 Survival Stage Qualifiers**: 4 Daily Champions (Days 1–4) + 4 Final Day Qualifiers.
* 15 matches (5 per day) under S.U.P.E.R. determine the **2026 PUBG World Champion**.

---

### 5.4 Qualification Cut-Off Zones & Clinch Mathematical Invariants
Every Stage defines ordered `QualificationZone` records:
* `rankStart` to `rankEnd` (e.g. 1 to 8 vs 9 to 16).
* `disposition`: `ADVANCE_GRAND_FINALS`, `ADVANCE_WINNERS`, `DROP_LOSERS`, `DROP_SURVIVAL_DAY_2`, `ELIMINATED`.

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

Key event couplings:
* **Eliminations & Knocks**: `LogPlayerMakeGroggy` and `LogPlayerKillV2` feed Section 3 (Scoring) and Section 4.2 (Squad Wipe).
* **Recall Lifecycle**: `LogPlayerRevive` with Recall event flags tracks multi-life respawns up to Phase 7 (`LogGameStatePeriodic`).
* **Damage Aggregation**: `LogPlayerTakeDamage` feeds Tier 4 Tie-Breakers (Section 3.2).
