# `deadzone-esports` — REST API Specification

> **Document Version**: 1.0.0  
> **Status**: Approved  
> **Target Release**: MVP  
> **Base URL**: `/api`  
> **Related Documents**:  
> • Functional Requirements Specification: [`docs/functional-requirements.md`](file:///D:/MyProjects/Java/deadzone-esports/docs/functional-requirements.md)  
> • Architecture Blueprint: [`docs/deadzone-esports-architecture.md`](file:///D:/MyProjects/Java/deadzone-esports/docs/deadzone-esports-architecture.md)

---

## 1. Overview & Conventions

All endpoints adhere to REST conventions over JSON:
* Dates and timestamps use ISO 8601 UTC (`YYYY-MM-DDTHH:mm:ssZ`).
* Standard HTTP status codes:
  * `200 OK`: Request succeeded.
  * `201 Created`: Resource created successfully.
  * `400 Bad Request`: Validation failure or malformed payload.
  * `404 Not Found`: Resource not found.
  * `500 Internal Server Error`: Unhandled server error.
* Error responses return a standardized domain error body:
  ```json
  {
    "timestamp": "2026-09-30T10:00:00Z",
    "status": 400,
    "error": "BAD_REQUEST",
    "message": "Telemetry file missing required LogMatchStart event",
    "path": "/api/tournaments/1/stages/1/matches/upload"
  }
  ```

---

## 2. API Endpoints & Requirements Traceability

### 2.1 Tournament Endpoints

#### `GET /api/tournaments` [`FR-1.1`, `FR-1.2`]
* **Purpose**: List tournaments grouped by lifecycle status or filtered by region/tier.
* **Query Parameters**:
  * `status` (optional): `ONGOING` | `PAST` | `UPCOMING`
  * `region` (optional): `GLOBAL` | `EMEA` | `AMERICAS` | `APAC` | `ASIA`
  * `tier` (optional): `S_TIER` | `A_TIER` | `B_TIER` | `QUALIFIER`
  * `search` (optional): Case-insensitive substring match on tournament title.
* **Response (200 OK)**:
  ```json
  [
    {
      "id": "pgc-2024",
      "title": "PUBG Global Championship 2024",
      "slug": "pgc-2024",
      "seasonYear": 2024,
      "region": "GLOBAL",
      "tier": "S_TIER",
      "dates": "Nov 15 - Dec 1, 2024",
      "location": "Kuala Lumpur, Malaysia",
      "prizePool": "$2,000,000 USD",
      "logoUrl": "/images/tournaments/pgc2024.png",
      "status": "ONGOING",
      "activeStageId": "stage-4-finals"
    }
  ]
  ```

#### `GET /api/tournaments/{id}` [`FR-2.3`]
* **Purpose**: Retrieve tournament details along with the ordered stages roadmap.
* **Response (200 OK)**:
  ```json
  {
    "id": "pgc-2024",
    "title": "PUBG Global Championship 2024",
    "region": "GLOBAL",
    "tier": "S_TIER",
    "stages": [
      {
        "id": "group-stage",
        "name": "Group Stage",
        "sequence": 1,
        "status": "COMPLETED",
        "matchProgress": "18/18",
        "ruleSummary": "Top 8 Advance to Winners Bracket, Bottom 8 Drop to Losers",
        "leader": {
          "teamName": "Twisted Minds",
          "teamTag": "TWIS",
          "points": 142,
          "isChampion": true
        }
      },
      {
        "id": "grand-finals",
        "name": "Grand Finals",
        "sequence": 4,
        "status": "LIVE",
        "matchProgress": "15/18",
        "ruleSummary": "Champion Crowned",
        "leader": {
          "teamName": "FaZe Clan",
          "teamTag": "FAZE",
          "points": 118,
          "isChampion": false
        }
      }
    ]
  }
  ```

#### `POST /api/tournaments` [`FR-1.3`]
* **Access**: Admin (Protected)
* **Payload**:
  ```json
  {
    "title": "Esports World Cup 2024",
    "slug": "ewc-2024",
    "seasonYear": 2024,
    "region": "GLOBAL",
    "tier": "S_TIER",
    "dates": "Aug 21 - Aug 25, 2024",
    "location": "Riyadh, Saudi Arabia",
    "prizePool": "$2,000,000 USD",
    "logoUrl": "/images/tournaments/ewc2024.png",
    "description": "Official EWC PUBG tournament."
  }
  ```
* **Response**: `201 Created` with tournament resource.

---

### 2.2 Stage & Standings Endpoints

#### `POST /api/tournaments/{id}/stages` [`FR-2.1`, `FR-2.4`, `FR-2.5`]
* **Access**: Admin (Protected)
* **Payload**:
  ```json
  {
    "name": "Grand Finals",
    "sequence": 4,
    "scoringRule": "SUPER_STANDARD",
    "smashThreshold": null,
    "ruleSummary": "Top 1 Crowned World Champion",
    "qualificationZones": [
      {
        "rankStart": 1,
        "rankEnd": 1,
        "targetStage": "CHAMPION",
        "label": "WORLD CHAMPION",
        "colorType": "SUCCESS"
      }
    ],
    "rosterSlots": [
      { "slotNumber": 1, "teamId": "twis", "teamName": "Twisted Minds", "tag": "TWIS" },
      { "slotNumber": 2, "teamId": "faze", "teamName": "FaZe Clan", "tag": "FAZE" }
    ]
  }
  ```
* **Response**: `201 Created`.

#### `GET /api/tournaments/{id}/stages/{stageId}/standings` [`FR-4.1` - `FR-4.6`]
* **Purpose**: Retrieve official calculated leaderboard with cut-offs and deltas.
* **Query Parameters**:
  * `dayNumber` (optional): Filter to match-day progression (`1`, `2`, `3`).
* **Response (200 OK)**:
  ```json
  {
    "stageId": "grand-finals",
    "stageStatus": "LIVE",
    "scoringRule": "SUPER_STANDARD",
    "matchesPlayed": 15,
    "totalMatches": 18,
    "standings": [
      {
        "rank": 1,
        "previousRank": 2,
        "rankDelta": 1,
        "dayDelta": 3,
        "teamId": "faze",
        "teamName": "FaZe Clan",
        "teamTag": "FAZE",
        "logoUrl": "/images/teams/faze.png",
        "matchesPlayed": 15,
        "killPoints": 72,
        "placementPoints": 46,
        "totalPoints": 118,
        "wwcdCount": 2,
        "isSmashEligible": false,
        "isClinched": false,
        "qualificationStatus": "PROJECTED_QUALIFIED"
      }
    ]
  }
  ```

---

### 2.3 Statistics Endpoints

#### `GET /api/tournaments/{id}/stages/{stageId}/team-stats` [`FR-5.1` - `FR-5.4`]
* **Purpose**: Team statistics aggregated across a specific stage.
* **Query Parameters**: `matchId`, `map` (`Erangel`|`Miramar`|`Taego`|`Rondo`), `search`.
* **Response (200 OK)**:
  ```json
  [
    {
      "teamId": "twis",
      "teamName": "Twisted Minds",
      "tag": "TWIS",
      "matchesPlayed": 15,
      "totalPoints": 112,
      "pointsPerMatch": 7.47,
      "totalKills": 68,
      "killsPerMatch": 4.53,
      "totalDamage": 14250,
      "damagePerMatch": 950.0,
      "avgPlacement": 5.2,
      "wwcdCount": 2,
      "winRatePercent": 13.3,
      "top4Count": 8,
      "top4Percent": 53.3,
      "totalKnocks": 74,
      "assists": 42
    }
  ]
  ```

#### `GET /api/tournaments/{id}/team-stats` [`FR-5.1` - `FR-5.4`]
* **Purpose**: Overall tournament-wide team statistics.
* **Query Parameters**: `stageId`, `matchId`, `map`, `search`.

#### `GET /api/tournaments/{id}/stages/{stageId}/player-stats` [`FR-6.1` - `FR-6.2`]
* **Purpose**: Player performance statistics for a given stage.
* **Query Parameters**: `teamId`, `matchId`, `map`, `search`.
* **Response (200 OK)**:
  ```json
  [
    {
      "playerId": "twis-xmpl",
      "nickname": "xmpl",
      "teamId": "twis",
      "teamTag": "TWIS",
      "matchesPlayed": 15,
      "kills": 29,
      "totalDamage": 5420.5,
      "avgDamage": 361.37,
      "dbnos": 24,
      "assists": 16,
      "headshotKills": 11,
      "headshotPercent": 37.93,
      "longestKill": 482.4,
      "avgSurvivalSeconds": 1320
    }
  ]
  ```

#### `GET /api/tournaments/{id}/player-stats` [`FR-6.1` - `FR-6.2`]
* **Purpose**: Tournament-wide player statistics across all stages.
* **Query Parameters**: `stageId`, `teamId`, `matchId`, `map`, `search`.

#### `GET /api/tournaments/{id}/stages/{stageId}/players/{playerId}` [`FR-6.3`]
* **Purpose**: Detailed player profile, match-by-match breakdown, and teammate roster for modal switcher.
* **Response (200 OK)**:
  ```json
  {
    "playerId": "twis-xmpl",
    "nickname": "xmpl",
    "teamId": "twis",
    "teamName": "Twisted Minds",
    "teamTag": "TWIS",
    "teammates": [
      { "playerId": "twis-batulins", "nickname": "BatulinS" },
      { "playerId": "twis-lu", "nickname": "Lu" },
      { "playerId": "twis-perfect1ks", "nickname": "Perfect1ks" }
    ],
    "matchBreakdown": [
      {
        "matchNumber": 1,
        "mapName": "Erangel",
        "kills": 4,
        "damage": 680.0,
        "dbnos": 3,
        "assists": 1,
        "survivalSeconds": 1640
      }
    ]
  }
  ```

---

### 2.4 Match Ingestion & 2D Replay Endpoints

#### `POST /api/tournaments/{id}/stages/{stageId}/matches/upload` [`FR-3.1` - `FR-3.4`]
* **Access**: Admin (Protected)
* **Content-Type**: `multipart/form-data` (file: `telemetry.json` or `.json.gz`)
* **Response**: `201 Created` with ingested match summary (`matchId`, `matchNumber`, `mapName`).

#### `POST /api/tournaments/{id}/stages/{stageId}/fixtures/load` [`FR-3.5`]
* **Access**: Admin (Protected)
* **Response**: `201 Created` with count of loaded fixtures.

#### `GET /api/matches/{id}/replay` [`FR-8.1` - `FR-8.8`]
* **Purpose**: Complete 2D replay state payload for canvas rendering.
* **Response (200 OK)**:
  ```json
  {
    "matchId": "match-1",
    "mapName": "Erangel",
    "coordinateBounds": { "minX": 0, "maxX": 816000, "minY": 0, "maxY": 816000 },
    "flightPath": {
      "startX": 120000, "startY": 45000,
      "endX": 750000, "endY": 780000
    },
    "durationSeconds": 1850,
    "phases": [
      {
        "phaseNumber": 1,
        "startTime": 0,
        "endTime": 360,
        "whiteCircle": { "x": 420000, "y": 380000, "radius": 200000 },
        "blueCircle": { "x": 408000, "y": 408000, "radius": 408000 }
      }
    ],
    "killEvents": [
      {
        "timestamp": 1125,
        "phase": 4,
        "isKnock": false,
        "killer": { "nickname": "Gustav", "teamTag": "FAZE", "x": 450120, "y": 395110 },
        "victim": { "nickname": "TGLTN", "teamTag": "SQ", "x": 451200, "y": 394800 },
        "weapon": "Beryl M762",
        "distanceMeters": 42.5
      }
    ]
  }
  ```
