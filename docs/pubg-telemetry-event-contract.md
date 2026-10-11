# PUBG Telemetry Event Reducer Contract & Specification

> **Document Version**: 1.0.0  
> **Status**: Draft / Under Review against Real Telemetry  
> **Target System**: `deadzone-esports` Ingestion Engine & Pure Domain Core  
> **Related Document**: [`docs/pubg-esports-domain-rules.md`](file:///D:/MyProjects/Java/deadzone-esports/docs/pubg-esports-domain-rules.md)  
> **Reference Fixture**: [`docs/telemetry-sample.json`](file:///D:/MyProjects/Java/deadzone-esports/docs/telemetry-sample.json)

---

## 1. Overview & Ingestion Architecture

The `deadzone-esports` telemetry engine ingests official Krafton Developer API telemetry streams (`telemetry.json` / `.json.gz`). 

The telemetry reducer is a pure functional processor that consumes chronological telemetry events and folds them into an immutable match state:
* Resolves raw player account IDs and custom match lobby slots (`teamId` 1–16) to official registered tournament teams.
* Computes accurate combat metrics (Kills, Knocks, Assists, Damage, Survival Time).
* Calculates final squad placement ranks and S.U.P.E.R. / Smash points.
* Handles modern multi-life Recall events and complex kill attribution scenarios.

```
┌────────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐
│ Raw Telemetry Stream   │ ───► │ Telemetry Event Reducer │ ───► │ Normalized Match State  │
│ (Krafton JSON Events)  │      │ (Domain Event Reducer)  │      │ (Leaderboard & Stats)   │
└────────────────────────┘      └─────────────────────────┘      └─────────────────────────┘
```

---

## 2. Krafton Telemetry Event Schemas & Extraction Contracts

### 2.1 `LogMatchDefinition` / `LogMatchStart`
* **Trigger**: Emitted once at match initialization.
* **Key Fields to Extract**:
  * `MatchId`: Unique match GUID string.
  * `PingInterval`: Tick frequency.
  * `SeasonState`: Game version/patch context.
* **Reducer Action**: Initializes the match accumulator, establishes start timestamp ($T_0$), and verifies telemetry schema version compatibility.

---

### 2.2 `LogPlayerMakeGroggy` (Knocks / DBNO)
* **Trigger**: Emitted whenever a player's health drops to 0 while at least one squad teammate is alive, placing the victim into the Down-But-Not-Out (DBNO) state.
* **Key Fields to Extract**:
  * `attacker`: Knocker details (`accountId`, `name`, `teamId`).
  * `victim`: Downed player details (`accountId`, `name`, `teamId`).
  * `damageTypeCategory`: Weapon or source type (e.g., `Damage_Gun`, `Damage_Explosion`).
  * `damageCauserName`: Item or weapon identifier (e.g., `WeapBeryM762_C`, `WeapPanzerFaust100M_C`).
  * `distance`: Distance between attacker and victim in centimeters.
  * `_D`: Timestamp of the event.
* **Reducer Invariants**:
  1. Increment attacker's total **DBNOs / Knocks** metric (+1) if `attacker.teamId != victim.teamId`.
  2. Record the pair `(victim.accountId, attacker.accountId)` in the active DBNO registry. This knocker is designated as the active **`dBNOMaker`**.
  3. If `attacker == null` or `attacker.teamId == victim.teamId` (friendly knock or environmental knock), register `dBNOMaker = null`.

---

### 2.3 `LogPlayerKillV2` (Eliminations)
* **Trigger**: Emitted when a player dies permanently (from DBNO bleed-out, direct flush, instant wipe, or environmental death).
* **Key Fields to Extract**:
  * `killer`: The player executing the final damage tick (`accountId`, `name`, `teamId`). Can be `null`.
  * `victim`: The eliminated player (`accountId`, `name`, `teamId`).
  * `dBNOMaker`: The player who initially knocked the victim (`accountId`, `name`, `teamId`). Can be `null`.
  * `damageTypeCategory`: Primary category (`Damage_Gun`, `Damage_BlueZone`, `Damage_Explosion_RedZone`, `Damage_Suicide`).
  * `finishMethod`: Method of death (`DirectFlush`, `BleedOut`, `BlueZone`, etc.).
  * `assistant`: Optional assistant account metadata.
* **Attribution & Reducer Rules**:
  * **Rule A: Teammate Flush** (`killer.teamId == dBNOMaker.teamId`):
    * The original **`dBNOMaker`** receives the official Kill credit (+1 Kill Point).
    * The finishing teammate receives an **Assist** credit.
  * **Rule B: Third-Party Flush / Kill Steal** (`killer.teamId != dBNOMaker.teamId` and `killer.teamId != victim.teamId`):
    * In Krafton telemetry, the third-party finisher (`killer`) receives the official Kill credit (+1 Kill Point).
    * The original `dBNOMaker` retains the DBNO credit and is awarded an Assist.
  * **Rule C: Bleed-Out / Bluezone Death while Knocked**:
    * If an enemy player knocked the victim and the victim bleeds out, drowns, or dies to the Bluezone without third-party intervention (`killer == null` or environmental):
    * Telemetry attributes the kill to `dBNOMaker`. The `dBNOMaker` receives the official Kill credit (+1 Kill Point).
  * **Rule D: Posthumous Wipe Attribution**:
    * If the `dBNOMaker`'s entire squad was eliminated prior to the victim bleeding out in the Bluezone:
    * The `dBNOMaker`'s team **still receives the posthumous +1 Kill Point** on the tournament leaderboard.
  * **Rule E: Unknocked Environmental / Tactical Suicide / Red Zone Deaths**:
    * If a player dies directly to the Bluezone, Red Zone artillery (`Damage_Explosion_RedZone`), or fall damage without being in DBNO:
    * `killer == null`. **0 Kill Points are awarded to any team**. No negative points are deducted.
  * **Rule F: Team Kills (Friendly Fire)**:
    * If `killer.teamId == victim.teamId`:
    * **0 Kill Points awarded**. Does not increment kill count.

---

### 2.4 `LogPlayerTakeDamage` (Damage Aggregation)
* **Trigger**: Emitted every time a player sustains damage.
* **Key Fields to Extract**:
  * `attacker`: Damage dealer (`accountId`, `teamId`).
  * `victim`: Target (`accountId`, `teamId`).
  * `damage`: Floating-point damage amount.
  * `damageTypeCategory`: Damage classification.
* **Reducer Invariants**:
  1. **Strict Opponent Filter**: Damage is credited to the attacker **if and only if** `attacker != null` and `attacker.teamId != victim.teamId`.
  2. **Exclude Self-Damage & Friendly Fire**: Exclude all damage where `attacker.accountId == victim.accountId` or `attacker.teamId == victim.teamId`.
  3. **Cap Damage at Max Health**: If a single damage tick exceeds the target's current remaining health (including DBNO bleed-out health pools), cap the credited damage to the victim's actual remaining HP to prevent artificial damage inflation from overkill hits.

---

### 2.5 `LogPlayerRevive` & Blue Chip Recall Events
* **Trigger**: Emitted upon successful revival of a downed player or deployment from a Recall flight.
* **Key Fields to Extract**:
  * `reviver`: Player performing the action.
  * `victim`: Player brought back into active play.
  * `reviveType`: Differentiates between standard manual squad revive and `RecallTower` / `RecallTransmitter`.
* **Reducer Action**:
  * **Standard Teammate Revive**: Clears the DBNO state for the victim. Player resumes normal single-life status.
  * **Blue Chip Recall Redeployment**:
    * Victim re-enters the active match alive (`isAlive = true`).
    * **Crucial Multi-Life Invariant**: Previous deaths and enemy kills are **immutable**. They are never retracted or erased. The recalled player's individual death count is incremented upon each subsequent death.

---

### 2.6 `LogGameStatePeriodic` & Circle Phase Tracking
* **Trigger**: Emitted periodically (e.g. every few seconds) throughout the match.
* **Key Fields to Extract**:
  * `gameState.safetyZonePosition` & `safetyZoneRadius`: Coordinates and size of the current safe circle (white circle).
  * `gameState.poisonGasWarningPosition` & `poisonGasWarningRadius`: Coordinates of the outer blue zone boundary.
  * `gameState.numAliveTeams` & `numAlivePlayers`: Real-time active count.
* **Phase 7 Recall Deactivation**:
  * Telemetry tracks circle phases (Phase 1 through Phase 8/9).
  * At the start of **Phase 7**, Blue Chip Recall Towers deactivate permanently. Any subsequent death is non-recoverable.

---

## 3. Squad Wipe & Placement Rank Determination

### 3.1 Total Extinction Invariant
* In PUBG esports, a team's finishing placement rank is determined **strictly when the entire squad is eliminated** (0 active or recallable players remaining).
* **Single Survivor Extension**: As long as 1 squad member is alive, the team's placement continues to rise as other teams are wiped out.
* **Instant Squad Wipe on Last Man Knocked**: Because Self-AED is deleted from the game, when the final surviving member of a squad is knocked down, that player and any currently knocked teammates are eliminated **instantly** without entering a prolonged DBNO state.
* **Simultaneous Wipes**: If two squads are eliminated in the same game tick (e.g. mutual grenade or late blue zone collapse), placement is assigned based on the exact timestamp order recorded in telemetry (`_D`).

---

## 4. Match State Reducer Pseudocode

```python
def process_event(event, state):
    match event.type:
        case "LogPlayerMakeGroggy":
            if event.attacker and event.attacker.teamId != event.victim.teamId:
                state.player_stats[event.attacker.id].knocks += 1
                state.active_knocks[event.victim.id] = event.attacker.id

        case "LogPlayerTakeDamage":
            if event.attacker and event.attacker.teamId != event.victim.teamId:
                effective_damage = min(event.damage, state.get_player_hp(event.victim.id))
                state.player_stats[event.attacker.id].total_damage += effective_damage

        case "LogPlayerKillV2":
            victim_id = event.victim.id
            dbno_maker_id = state.active_knocks.pop(victim_id, None)
            
            # Determine credited killer
            if event.killer and event.killer.teamId != event.victim.teamId:
                if dbno_maker_id and state.get_team(dbno_maker_id) == event.killer.teamId:
                    # Teammate flushed
                    credit_kill(state, dbno_maker_id)
                    state.player_stats[event.killer.id].assists += 1
                else:
                    # Direct flush or third-party flush
                    credit_kill(state, event.killer.id)
                    if dbno_maker_id:
                        state.player_stats[dbno_maker_id].assists += 1
            elif dbno_maker_id:
                # Died to bluezone/fall while knocked by an opponent
                credit_kill(state, dbno_maker_id)
            else:
                # Unknocked suicide / redzone / teamkill -> 0 points awarded
                pass
            
            # Update victim state & check team wipe
            state.mark_player_dead(victim_id)
            if state.is_team_wiped(event.victim.teamId):
                current_alive_teams = state.count_alive_teams()
                state.team_placement[event.victim.teamId] = current_alive_teams + 1

        case "LogPlayerRevive":
            state.active_knocks.pop(event.victim.id, None)
            state.mark_player_alive(event.victim.id)
```
