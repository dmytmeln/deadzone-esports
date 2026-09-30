# `deadzone-esports` — UI/UX & Presentation Specification

> **Document Version**: 1.0.0  
> **Status**: Approved  
> **Target Release**: MVP  
> **Related Documents**:  
> • Functional Requirements Specification: [`docs/functional-requirements.md`](file:///D:/MyProjects/Java/deadzone-esports/docs/functional-requirements.md)  
> • Interactive Prototype Mockup: [`docs/ui-mockup.html`](file:///D:/MyProjects/Java/deadzone-esports/docs/ui-mockup.html)  
> • System Architecture: [`docs/deadzone-esports-architecture.md`](file:///D:/MyProjects/Java/deadzone-esports/docs/deadzone-esports-architecture.md)

---

## 1. Design Philosophy & Visual Language

`deadzone-esports` provides an esports broadcast-grade user interface inspired by Krafton official tournament aesthetics and Twire.gg analytics. The design prioritizes high contrast, information density, seamless spatial navigation, and zero visual stutter during live data updates.

### 1.1 Design Tokens & Color Palette

The interface is built with Tailwind CSS using the dedicated `pubg` dark design token family:

| Token | Hex Value | Usage / Semantic Role |
| :--- | :--- | :--- |
| `pubg-dark` | `#0B0E14` | Global application background |
| `pubg-surface` | `#151A23` | Navigation headers, filter toolbars, table headers |
| `pubg-card` | `#1B2230` | Cards, modal sheets, dropdown menus |
| `pubg-border` | `#2A364F` | Structural grid borders, dividers, subtle outlines |
| `pubg-gold` | `#F2A900` | Primary brand accent, tournament winner highlights, active tab states |
| `pubg-green` | `#10B981` | Advancement/promotion zones, positive rank deltas (`▲ +N`) |
| `pubg-amber` | `#F59E0B` | Relegation/demotion zones, knocked (DBNO) player states, warnings |
| `pubg-red` | `#E53E3E` | Elimination zones, negative rank deltas (`▼ -N`), live broadcast indicators |
| `pubg-blue` | `#3182CE` | Dynamic Blue Zone circle, information badges |

### 1.2 Typography
* **UI & Headings**: `Outfit`, sans-serif (weights: 400, 500, 600, 700, 800) — clean geometric readability.
* **Numbers, Scores & Timestamps**: `JetBrains Mono`, monospace (weights: 400, 600, 700) — tabular numerical alignment across tables and timers.

---

## 2. Component Specifications & Requirements Traceability

### 2.1 Tournament Discovery Hub [`FR-1.1`, `FR-1.2`]
* **Group Navigation Tabs**:
  * Three primary tabs: **Ongoing**, **Upcoming**, **Past**.
  * Each tab contains a pill badge with the tournament count (e.g. `Ongoing 3`, `Past 12`).
  * Active tab receives `bg-pubg-gold text-black font-bold` styling.
* **Filter Toolbar**:
  * Real-time search input with magnifying glass icon and instant clear button (`×`).
  * Dropdown menus for **Region** (`All`, `Global`, `EMEA`, `Americas`, `APAC`, `Asia`) and **Tier** (`All`, `S-Tier`, `A-Tier`, `B-Tier`, `Qualifier`).
* **Tournament Grid Cards**:
  * Render tournament logo, tier badge, region tag, prize pool, date range, and current active stage indicator.
  * Hover state: subtle scaling (`scale-[1.01]`) and border glow in `pubg-gold/40`.

---

### 2.2 Stages Roadmap & Progression Hub [`FR-2.3`]
* **Stages Progression Bar**:
  * Chronologically ordered stage cards connected by chevron or arrow progression lines.
  * **Stage Status Indicators**:
    * `LIVE NOW`: Pulsing red dot animation (`animate-ping`) with red badge and highlight border.
    * `ONGOING`: Amber/blue active badge with matches played progress (e.g., `14/18 Matches`).
    * `COMPLETED`: Muted slate badge with green checkmark.
    * `UPCOMING`: Dimmed card opacity with scheduled start date.
* **Stage Leader Presentation**:
  * **Completed Stage**: Stage Champion card displaying gold trophy icon (`🏆`), winning team name, team logo, and final points.
  * **Ongoing/Live Stage**: `#1 Interim Leader` card showing current top-ranked team and live points.
  * **Upcoming Stage**: `TBD` placeholder.
* **Quick-Action CTA**:
  * When a stage is active, the tournament header displays a pulsing action button: `"Jump to Live Stage"`, directly opening the active stage leaderboard.

---

### 2.3 Official Leaderboard & Standings Presentation [`FR-4.4`, `FR-4.5`, `FR-4.6`]

#### Standings Table Layout
The table displays: Rank, Trend Delta, Team Name & Tag, Matches Played, Kills, Placement Points, Total Points, and WWCDs.

#### Rank Deltas Visualization [`FR-4.5`]
* **Match-to-Match Delta**:
  * Green text `▲ +N` for rank improvement.
  * Red text `▼ -N` for rank drop.
  * Neutral dash `-` for unchanged rank.
* **Day-to-Day Progression**:
  * Match day filter tabs (`All Days`, `Day 1`, `Day 2`, `Day 3`).
  * Selection reveals day-over-day rank transition chips showing trajectory (e.g., comeback journey `16 ➔ 5`).

#### Cut-Off Dividers & Highlighting: Live vs. Completed [`FR-4.6`]
The visual treatment adapts dynamically based on the stage status:

```
LIVE / ONGOING STAGES (Provisional / Projected)
┌────────────────────────────────────────────────────────────────────────┐
│ Rank 1-8: Soft Green Shading + Green Left Accent Border                │
├- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ┤
│ - - - - ▲ PROJECTED QUALIFICATION CUT-OFF (TOP 8 BUBBLE) ▲ - - - - - - │
├- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ┤
│ Rank 9-16: Soft Red Shading + Points to Safety Margin ("-2 pts")       │
│ * Clinched Indicator: "🔒 Clinched" badge for mathematically safe teams│
└────────────────────────────────────────────────────────────────────────┘

COMPLETED STAGES (Final Locked Dispositions)
┌────────────────────────────────────────────────────────────────────────┐
│ Rank 1-8: Solid Green Left Border + "QUALIFIED 🏆" / "ADVANCES 🟢"     │
├════════════════════════════════════════════════════════════════════════┤
│ ════════════════════ FINAL LOCKED QUALIFICATION CUT-OFF ══════════════ │
├════════════════════════════════════════════════════════════════════════┤
│ Rank 9-16: Dimmed Row Opacity + "DROPS TO LOSERS 🟡" or "ELIMINATED 🔴"│
└────────────────────────────────────────────────────────────────────────┘
```

* **Smash Rule Badge** [`FR-4.3`]: Teams exceeding the configured point threshold display an animated gold flame/shield badge labeled `SMASH ELIGIBLE`.

---

### 2.4 Team & Player Statistics Views [`FR-5.1` - `FR-6.3`]

#### Cross-View Filter Toolbar [`FR-5.4`, `FR-6.2`, `FR-7.1`]
* Unified sticky toolbar containing:
  * **Scope Selector**: `Tournament Scope` vs. `Stage Scope`.
  * **Dropdown Filters**: Stage, Map (`Erangel`, `Miramar`, `Taego`, `Rondo`), Match selector.
  * **Search Input**: Team name/tag filter in Team Stats; Player nickname or Team tag filter in Player Stats.
* Changes sync immediately to browser URL parameters without resetting when switching between tabs.

#### Player Drill-Down Modal & Teammate Switcher [`FR-6.3`]
* **Trigger**: Clicking any player row opens a centered overlay modal with backdrop blur.
* **Modal Header & Teammate Switcher**:
  * Displays player nickname, team logo, and squad role.
  * Includes a row of **teammate pills/tabs** displaying all active players on the same squad.
  * Clicking any teammate immediately refreshes the modal with that player's data without closing or unmounting the modal.
* **Modal Body**:
  * Key Performance Indicators (KPI) grid: Kills, Total Damage, Damage/Match, Headshot %, DBNOs, Longest Snipe, Avg Survival.
  * Chronological **Match-by-Match Breakdown** table detailing match number, map name, individual kills, damage dealt, knocks, assists, and survival time.

---

### 2.5 Interactive 2D Match Replay Canvas [`FR-8.1` - `FR-8.8`]

#### Canvas Layout & Background [`FR-8.1`, `FR-8.2`]
* Scaled SVG overlay superimposed on official high-resolution top-down raster map textures (Erangel, Miramar, Taego, Rondo).
* **Viewport Navigation**:
  * Smooth mouse drag-to-pan with grab cursor.
  * Smooth zoom via mouse wheel, trackpad pinch, and dedicated `+`, `-`, and `Reset` controls.
  * Fullscreen toggle button (`⛶`) triggering browser native fullscreen mode.

#### Timeline & Playback Bar [`FR-8.3`]
* Video-style scrub slider spanning from match start (`00:00`) to match conclusion.
* Play / Pause button with spacebar keyboard shortcut.
* Playback speed multiplier selector: `1x`, `2x`, `5x`, `10x`.
* **Step Interval Toggle**: Buttons to step backward/forward with a configurable step interval switch between **5 seconds** and **10 seconds**.

#### Map Entities & Dynamic Elements [`FR-8.4`, `FR-8.5`, `FR-8.6`]
* **Safe Zone (White Circle)**: Static target circle for the active phase with crisp white stroke.
* **Playzone (Blue Circle)**: Dynamically interpolating circle contracting over phase duration with glowing blue stroke.
* **Squad & Player Markers**:
  * Colored circular dots matching official team branding.
  * Player slot number (`1`, `2`, `3`, `4`) embedded inside or beside the circle.
  * Player nickname label hovering above dot.
  * **Knocked State (DBNO)**: Pulsing amber halo surrounding player dot.
  * **Elimination**: Red skull icon at elimination coordinate with brief red vector line from killer to victim showing weapon icon and kill distance in meters.
* **Flight Path & Plane Toggle**:
  * Vector flight path line across the map with animated plane icon during drop phase.
  * Dedicated **Show / Hide Plane** toggle button to declutter canvas during late-game phases.

#### Synchronized Kill Feed Sidebar [`FR-8.8`]
* Chronological feed of match casualties and knocks (DBNOs).
* Feed card details: Timestamp (`MM:SS`), Phase number, Killer team tag & nickname, weapon icon, distance, Victim team tag & nickname.
* **Click-to-Focus Interaction**:
  1. Replay timeline scrubs instantly to the event timestamp.
  2. Canvas camera smoothly centers on the event coordinates.
  3. Displays an animated expanding pulse beacon around the involved player marker.
