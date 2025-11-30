# Group-Based League Simulation

## The Group System Model
This is a proposal for a **10-week 9-game scheduling commitment** designed for a **16-team league**. It solves the "Tie-Breaker Chaos" problem by ensuring that top teams play each other on the field, rather than relying on polls or complex metrics.

### The Structure
*   **16 Teams**: Split into **4 Groups of 4** (A, B, C, D).
*   **Weeks 1-3 (Group Play)**: A full round-robin within your group.
*   **Week 4 (Bye/OOC)**: A conference-wide bye week. Schools can schedule a marquee Out-of-Conference game or rest.
*   **Weeks 5-6 (Power Match)**: The innovation.
    *   **Week 5**: Two groups host the other two (e.g., A hosts B, C hosts D).
    *   **Week 6**: The roles flip and pairings switch (e.g., D hosts A, B hosts C).
    *   **The Matchups**: Decided *after Week 3*. You play the team in the opposing group that shares your rank (1st vs 1st, 2nd vs 2nd).
*   **Weeks 7-10 (Crossover)**: One group plays the entirety of another group (e.g., Group A plays all 4 teams in Group C).

### Why Mid-Season Power Match?
While placing the "Power Match" games at the end of the season offers better data for tie-breakers, placing them in the **Middle (Weeks 5-6)** is superior for the product.
*   **Narrative Tension**: It creates distance between the regular season matchup and a potential rematch in the Championship Game.
*   **Rematch Fatigue**: An immediate rematch (Week 12 Power Match followed by Week 13 CCG) feels stale. A rematch of a Week 5 thriller feels like a "Revenge Game."
*   **Clarity**: By Week 7, we know exactly who the contenders are. The "Pretenders" have been weeded out by the Power Match games.

### The Goal
The aim is to eliminate the "Scheduling Quirk" era of college football—where a team like Miami might miss the CCG over a lower-ranked Duke or Virginia simply because they didn't play the right people. This system forces the best to play the best, every single year.

---

## Key Findings

This project simulates a 16-team college football league (SEC or Big XII) split into 4 groups of 4. The goal is to analyze if this structure, combined with "Power Match" scheduling, reduces the frequency of chaotic tie-breakers for the Championship Game (CCG) spots compared to large divisions.

## Key Findings

Based on 1000 simulated seasons using real 2025 Elo ratings:

*   **Baseline (1 Power Match Week)**: Approximately **51-54%** of seasons end with a tie for the top 2 spots (requiring complex tie-breakers).
*   **Chaos Model (9-Game Random)**: Approximately **52%** of seasons end with a tie. This confirms that simply playing more games (9 vs 8) without structure doesn't solve the tie-breaker issue.
*   **Enhanced (2 Power Match Weeks)**: Increasing to 2 SoS weeks reduces the tie frequency to **~45%**.
*   **Timing**: Moving Power Match games to the **end** of the season (after group and crossover play) offers a marginal improvement over mid-season scheduling, likely because the matchups are based on more mature data.

## How to Run

### Prerequisites
- Python 3.x
- No external dependencies required (uses standard library).

### Basic Usage
Run a single season simulation for the SEC:
```bash
python3 main.py --league SEC
```

### Advanced Options
*   `--league`: Choose `SEC` or `BigXII`.
*   `--sims`: Number of simulations to run (e.g., `1000`).
*   `--power-weeks`: Number of Power Match games (`1` or `2`).
*   `--power-timing`: When to play Power Match games (`mid` or `end`).
*   `--evolve-elo`: Enable multi-season dynasty mode where ratings carry over.

### Examples
**Check tie frequency with 2 Power Match weeks:**
```bash
python3 main.py --league SEC --sims 1000 --power-weeks 2
```

**Simulate a 50-year dynasty:**
```bash
python3 main.py --league SEC --sims 50 --evolve-elo
```

## Exemplar Schedules

Below are examples of how a season plays out for a top team from each group under different scheduling models.

### Scenario A: Mid-Season Power Match (2 Weeks)
*Schedule Order: 3 Group Games -> 2 SoS Games -> 4 Crossover Games*

**Georgia (Group A)**
*   **Group Play**: W vs Florida, L vs South Carolina, W vs Kentucky
*   **SoS Week 1**: W vs Alabama (Group B leader)
*   **SoS Week 2**: W vs Texas (Group D leader)
*   **Crossover**: L vs LSU, L vs Ole Miss, L vs Miss State, W vs Arkansas
*   **Result**: 5-4

**Alabama (Group B)**
*   **Group Play**: W vs Auburn, W vs Tennessee, W vs Vanderbilt
*   **Power Match Week 1**: L vs Georgia
*   **Power Match Week 2**: L vs LSU
*   **Crossover**: W vs Texas, W vs Texas A&M, W vs Oklahoma, W vs Missouri
*   **Result**: 7-2

### Scenario B: End-Season Power Match (2 Weeks)
*Schedule Order: 3 Group Games -> 4 Crossover Games -> 2 Power Match Games*

**Georgia (Group A)**
*   **Group Play**: L vs Florida, W vs South Carolina, L vs Kentucky
*   **Crossover**: W vs LSU, W vs Ole Miss, W vs Miss State, W vs Arkansas
*   **Power Match Week 1**: L vs Alabama (Matched based on 5-2 record)
*   **Power Match Week 2**: L vs Texas A&M (Matched based on 5-3 record)
*   **Result**: 5-4

**Alabama (Group B)**
*   **Group Play**: W vs Auburn, W vs Tennessee, L vs Vanderbilt
*   **Crossover**: W vs Texas, W vs Texas A&M, L vs Oklahoma, W vs Missouri
*   **Power Match Week 1**: W vs Georgia
*   **Power Match Week 2**: W vs Ole Miss
*   **Result**: 7-2

## Configuration
Teams and groups are defined in `config.py`. You can modify the groups or update Elo ratings there. The current ratings are based on Warren Nolan's 2025 projections.

## Logistics & Feasibility (The "Flex" Model)
A common critique of dynamic scheduling is the difficulty of travel planning. A proposed solution to make this viable:

1.  **Pre-Set Rotations**: The Home/Away designation is fixed years in advance.
    *   *Example*: In 2026, Group A is guaranteed to **Host** Group B in Week 8.
    *   *Benefit*: Home fans know they have a game. Away fans know they are traveling to one of 4 specific campuses.
2.  **Staggered Scheduling**:
    *   **League 1 (e.g., SEC)**: Plays Power Match weeks in **Mid-October**.
    *   **League 2 (e.g., Big XII)**: Plays Power Match weeks in **Late November**.
    *   *Benefit*: This allows each league to dominate the TV ratings for a specific month and avoids cannibalizing viewership.
3.  **The "6-Day Window"**: TV networks already use a 6-day selection window for kickoff times. This system extends that concept to the *opponent* selection, which fits within existing operational workflows for broadcasters.

## Handling Interlocking Defeats (The "Circle of Death")
If Group A has three teams tied at 2-1 in group play (A beat B, B beat C, C beat A), we need a deterministic way to rank them 1-2-3 to match against Group B.

**Recommended Tie-Breaker Hierarchy:**
1.  **Head-to-Head**: (Busted in a circle).
2.  **Record vs Crossover Group**: Since the entire Group A plays the entire Group C (or similar), they have **4 Common Opponents**.
    *   *Logic*: If Team A went 4-0 against the Crossover Group, but Team B went 3-1, Team A is ranked higher.
    *   *Why it works*: It rewards performance against the rest of the league, not just the internal rock-paper-scissors.
3.  **Capped Point Differential**: If still tied (e.g., both went 4-0 vs Crossover), use point differential in the *Group Games*, capped at +17 per game.

### Final Recommendation: The "End-Season" Advantage
Because of the risk of interlocking defeats, **End-Season Power Match is superior**.
*   **Mid-Season**: You only have 3 data points (Group games) to break a circular tie. This is often insufficient.
*   **End-Season**: You have **7 data points** (3 Group + 4 Crossover). The "Record vs Crossover Group" tie-breaker is fully available *before* you select the Power Match opponent, ensuring the best team gets the #1 seed matchup.

## Handling Odd League Sizes (e.g., 17 Teams)
The Group System relies on symmetry. An odd number of teams breaks the pairing logic. Two solutions exist:

### 1. The "Alliance" Model
Find a partner league that also has an odd number (e.g., ACC).
*   **Mechanism**: The "Leftover" team from the SEC plays the "Leftover" team from the ACC during the Power Match week.
*   **Benefit**: Preserves 1v1 pairings for the top 16 teams while giving the 17th team a competitive Power-4 opponent.

### 2. The "Designated Donor" Model
The league contracts an external "Donor" team (e.g., New Mexico, Hawaii, or a recently departed school) to fill the 18th slot.
*   **Mechanism**: The Donor agrees to play whoever is left over in the Power Match pairing (usually a mid-tier or lower-tier team).
*   **Sweetener**: To make this attractive, the game can be a **Road Game for the Donor** (giving the league team a valuable home gate) or a "Buy Game" with a premium payout.
*   **Exit Fee Clause**: Teams leaving the league could be contractually bound to serve as the "Donor" for 4 years, ensuring the league has time to find a permanent replacement.
