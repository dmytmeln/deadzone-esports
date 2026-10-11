# deadzone-esports Domain Glossary

The authoritative ubiquitous language for the `deadzone-esports` tournament engine, telemetry analyzer, and 2D match replay viewer. Defines core domain entities, scoring rules, combat invariants, lifecycle models, progression dynamics, and presentation concepts across modern (2026) and historical (2019–2025) competitive eras.

---

## 1. Competition Hierarchy & Participants

**Tournament**:
The overarching championship competition spanning one or more sequential stages.
_Avoid_: Event, Series, Cup

**Stage**:
A discrete competitive phase of a tournament defined by its own roster, schedule, scoring strategy, and progression rules.
_Avoid_: Phase, Round, Segment, Bracket

**MatchDay**:
A scheduled calendar broadcast date within a stage hosting a defined sequential series of matches.
_Avoid_: Game Day, Round, Date

**Match**:
A single competitive game played on a specific map by up to 16 squads.
_Avoid_: Game, Round, Map

**Lobby Slot**:
A fixed integer index (1 through 16) within a match lobby mapped to an official registered team.
_Avoid_: Team ID, Lobby Seat, Seed

**Team**:
A registered esports club or organization competing in a tournament.
_Avoid_: Org, Clan, Franchise

**Roster**:
The official lineup of registered players representing a Team within a specific stage.
_Avoid_: Lineup, Squad List

**Player**:
An individual esports competitor registered to a team roster.
_Avoid_: Competitor, Member, User

### Participant Identity & Origin

**Partner Team**:
An esports organization holding guaranteed entry into global tournament stages through an official partnership program.
_Avoid_: Franchised Team, Invited Team

**Qualified Team**:
A team that earned entry into a tournament stage through open, regional, or third-party qualification events.
_Avoid_: Open Team, Regional Team

**Account ID**:
The immutable unique identifier issued by Krafton to a player's PUBG account.
_Avoid_: User ID, Player ID, Steam ID

**Nickname**:
A player's in-game display name used during a tournament match.
_Avoid_: Handle, Gamertag, In-Game Name, IGN

### Stage Topologies

**Round Robin**:
A tournament topology where teams are divided into seeded pools and rotate across lobby groups to ensure every pool competes equally against all others.
_Avoid_: Group Rotation, Pool Play

**Double Elimination**:
A tournament topology featuring upper (Winners) and lower (Losers) brackets where teams are eliminated only after losing across two separate phases.
_Avoid_: Dual Bracket, GSL Format

**Dynamic Waitlist Ladder** [Legacy 2021]:
A rolling lobby topology where a match winner immediately qualifies and exits, allowing the highest-ranked waiting team to backfill the vacated lobby slot for the subsequent match.
_Avoid_: Rolling Ladder, Survival Queue, Fill-in Bracket

**Waterfall Stage** [Legacy 2024]:
A multi-day progression topology where surviving teams from a preceding daily pool combine with newly entering seeded cohorts in successive stages.
_Avoid_: Staggered Bracket, Step Bracket, Tier Cascade

---

## 2. Scoring & Rulesets

**S.U.P.E.R.**:
The Standard and Universal PUBG Esports Ruleset governing competitive match settings, the universal 10-point placement scale, and kill points.
_Avoid_: Standard Rules, Pro Rules

**Placement Points**:
Points awarded to a team based on its final survival ranking at the conclusion of a match.
_Avoid_: Rank Points, Position Points

**Kill Points**:
Tournament points awarded at a rate of exactly one point per confirmed opponent elimination.
_Avoid_: Frag Points, Elimination Points, Score

**WWCD**:
"Winner Winner Chicken Dinner" — finishing first place in an individual match, awarding 10 placement points under S.U.P.E.R.
_Avoid_: Match Win, Chicken, Victory

**Modern S.U.P.E.R. Tie-Breaker** [Modern 2022–2026]:
A placement-first tie-breaking hierarchy prioritizing Total Placement Points, followed by Last Match Total Points, Last Match Placement Points, and Last Match Kills.
_Avoid_: Current Tie-Breaker, New Tie-Breaker

**Legacy S.U.P.E.R. Tie-Breaker** [Legacy 2019–2022]:
A kill-first tie-breaking hierarchy prioritizing Total Accumulated Kills, followed by Best Single Match Points and Best Single Match Kills.
_Avoid_: Old Tie-Breaker

**Smash Rule** [Modern 2024–2026]:
A match point championship format where reaching a predetermined point threshold enables match point eligibility, requiring a subsequent WWCD to secure the tournament title.
_Avoid_: Match Point Rule, Checkpoint Rule, Smash Format

**Match Point Eligible** [Modern 2024–2026]:
The status of a team that has reached or surpassed the Smash Rule point threshold, allowing them to claim the championship by winning their next match.
_Avoid_: On Match Point, Checkpointed, Smash Ready

**Most Chicken Rule** [Legacy 2021]:
A tournament ranking system where total WWCDs serve as the primary leaderboard metric, with kill points acting solely as secondary tie-breakers.
_Avoid_: MC Rule, WWCD First, Chicken Format

---

## 3. Combat & Telemetry Events

**Active Player**:
A player currently alive and capable of moving, shooting, and reviving teammates.
_Avoid_: Living Player, Standby Player

**Knock**:
A state where an active player's hitpoints drop to zero while at least one squad teammate remains alive, disabling combat capabilities until revived or flushed.
_Avoid_: DBNO, Downed, Groggy, Incapacitated

**Kill**:
The confirmed permanent elimination of an opponent player from the match, awarding one Kill Point.
_Avoid_: Frag, Death, Score

**Knocker**:
The player who dealt the damage that caused an opponent's initial Knock.
_Avoid_: Downer, Initiator, dBNOMaker

**Finisher**:
The player who delivers the terminal damage that flushes a knocked opponent or directly eliminates an active player.
_Avoid_: Killer, Executioner

**Flush**:
The deliberate elimination of a knocked player before their teammates can revive them.
_Avoid_: Thirst, Clean Up, Finish Off

**Kill Steal**:
The elimination of a knocked player by an opponent whose team did not score the initial Knock, transferring the Kill Point to the finisher while preserving Knock credit for the original knocker.
_Avoid_: Third-Party Flush, Vulture

**Wipe**:
The elimination of a squad's last active player, instantly causing the death of any remaining knocked teammates and ending the squad's match participation.
_Avoid_: Team Wipe, Extinction, Elimination

**Assist**:
Damage dealt to an opponent who is subsequently knocked and eliminated by a squad teammate within a qualifying attribution window.
_Avoid_: Helper, Support Credit

**Credited Damage**:
The net opponent hitpoints destroyed by a player, capped at the target's available health pool and strictly excluding friendly fire and self-damage.
_Avoid_: Raw Damage, Uncapped Damage, Inflated Damage

**Survival Time**:
The duration in seconds from initial match drop until a player or squad is eliminated or secures the WWCD.
_Avoid_: Lifespan, Time Alive, Match Duration

### Environmental Concepts

**Map**:
The competitive 8x8 km or 4x4 km terrain on which a match takes place (e.g., Erangel, Miramar, Taego, Rondo).
_Avoid_: Level, Arena, World, Battleground

**Circle Phase**:
One of nine discrete safe-zone shrinking cycles within a match (Phases 1 through 9).
_Avoid_: Ring, Circle, Stage

**Safe Zone**:
The circular white boundary on the map within which players take zero environmental damage.
_Avoid_: White Circle, Safe Area, Play Area

**Blue Zone**:
The shrinking electric perimeter enclosing the Safe Zone that inflicts escalating damage to players outside its boundary.
_Avoid_: Gas, Storm, Electric Field, Border

### Presentation & Replay Concepts

**2D Replay Map**:
An interactive top-down cartographic viewer rendering synchronized player coordinates, vehicle movements, and zone perimeters.
_Avoid_: Minimap, Game Viewer

**Flight Path**:
The initial linear trajectory flown by the C-130 transport aircraft across the map from which players deploy.
_Avoid_: Plane Route, Drop Line, Trajectory

**Kill Feed**:
A real-time, chronological combat ticker displaying Knocks, Flushes, and Wipes synchronized with match playback.
_Avoid_: Event Log, Death Feed, Combat Log

---

## 4. Elimination & Lifecycle Models

**Single-Life Permanent** [Legacy 2019–2025]:
The competitive lifecycle model where player death is final and irreversible, with exactly 64 lives per match.
_Avoid_: Hardcore, One-Life, Permadeath

**Multi-Life Recall** [Modern 2026]:
The competitive lifecycle model allowing surviving teammates to respawn eliminated players using Blue Chip Recall Stations before Phase 7.
_Avoid_: Revive Mode, Gulag, Rebirth

**Blue Chip Recall Station** [Modern 2026]:
A static in-game communications station used by surviving teammates to transmit a Blue Chip and respawn eliminated squad members.
_Avoid_: Revive Tower, Respawn Beacon, Antenna, Station

**Blue Chip** [Modern 2026]:
An electronic transmitter retrieved from an eliminated player's death crate required to authorize their respawn at a Recall Station.
_Avoid_: Dog Tag, Revive Card, Token

**Phase 7 Recall Cutoff** [Modern 2026]:
The absolute match boundary at the start of Circle Phase 7 when all Recall Stations permanently power down and player eliminations become irreversible.
_Avoid_: Recall Lock, Respawn Cutoff

---

## 5. Progression & Standings Dynamics

**Cut-Off Line**:
A standing boundary row separating advancing, demoted, and eliminated zones on a stage leaderboard.
_Avoid_: Bubble Line, Cut Line, Border

**Projected Cut-Off**:
A dynamic, real-time qualification boundary displayed during an active, ongoing stage that shifts as matches are played.
_Avoid_: Live Cut-off, Interim Border

**Locked Cut-Off**:
The final, immutable qualification boundary established upon the completion of all matches in a stage.
_Avoid_: Final Cut-off, Closed Line

**Clinch**:
The state where a team has mathematically guaranteed qualification to the next stage before completing all scheduled matches.
_Avoid_: Locked In, Safe, Qualified Early

**Magic Number**:
The exact cumulative point target that mathematically guarantees a team's qualification regardless of all opponents' potential scores.
_Avoid_: Clinch Threshold, Target Points

**Rank Delta**:
The net change in a team's leaderboard position relative to the previous match (Match Delta) or previous competition day (Day Delta).
_Avoid_: Position Shift, Rank Movement
