# Playoff Fantasy Lineup Optimizer

This repository contains an optimizer for a playoff fantasy football league with unique rules:

## League Rules

- **One-time use**: Each player can only be used once across all playoff weeks
- **PPR Scoring**: 1.0 PPR for all positions
- **Tight End Premium**: 1.5 PPR for tight ends (0.5 bonus per reception)
- **Player pool shrinks**: As NFL teams are eliminated, their players become unavailable
- **Goal**: Maximize total fantasy points across ALL playoff weeks (not weekly wins)

## Lineup Requirements

- 1 QB
- 2-3 RB
- 2-3 WR
- 1-2 TE
- 0-1 K (optional)
- 0-1 DEF (optional)

## 2025 NFL Playoff Structure

### AFC
1. **Denver Broncos** (14-3) - #1 seed, first-round bye
2. New England Patriots - #2 seed
3. Jacksonville Jaguars - #3 seed
4. Pittsburgh Steelers - #4 seed
5. Houston Texans - #5 seed
6. Los Angeles Chargers - #6 seed
7. Buffalo Bills - #7 seed (data not available)

### NFC
1. **Seattle Seahawks** - #1 seed, first-round bye
2. Chicago Bears - #2 seed
3. Philadelphia Eagles - #3 seed
4. Carolina Panthers - #4 seed
5. Los Angeles Rams - #5 seed (San Francisco data not available)
6. (missing)
7. Green Bay Packers - #7 seed

### Wild Card Round Matchups

**AFC:**
- Patriots vs Chargers (Patriots favored)
- Jaguars vs Bills (Bills favored)
- Steelers vs Texans (Texans favored)

**NFC:**
- Bears vs Packers (Bears favored)
- Eagles vs 49ers (Eagles favored)
- Panthers vs Rams (Rams favored by 10)

## Optimization Strategy

The optimizer uses a sophisticated algorithm that considers:

1. **Base Projections**: Uses player's season average (FPTS/G) as playoff projection
2. **TE Premium**: Adds 0.5 points per reception for tight ends
3. **Team Advancement Probability**: Multiplies projections by probability team plays that week
4. **Elite Player Conservation**: Reduces value of elite players (>15 FPTS/G) on Super Bowl contenders (>25% SB odds) in early rounds
   - Wild Card: 60% penalty for elite players on strong teams
   - Divisional: 35% penalty for elite players on strong teams
5. **Bye Week Handling**: Broncos and Seahawks players have 0 value in Wild Card round

### Team Advancement Probabilities

Based on Vegas odds and predictions:

**Wild Card Survival:**
- DEN: 100% (bye), SEA: 100% (bye)
- LAR: 65%, PHI: 60%, BUF: 60%, NE: 55%, HOU: 55%, CHI: 55%
- JAX: 40%, LAC: 45%, PIT: 45%, GB: 45%, SF: 40%, CAR: 35%

**Divisional Survival:**
- DEN: 70%, SEA: 68%
- LAR: 42%, PHI: 40%, CHI: 33%, BUF: 35%, HOU: 32%, NE: 30%

**Championship Survival:**
- DEN: 55%, SEA: 52%
- LAR: 23%, PHI: 22%, CHI: 18%, BUF: 20%, HOU: 15%, NE: 15%

**Super Bowl Appearance:**
- DEN: 35%, SEA: 32%
- LAR: 13%, PHI: 12%, CHI: 8%, BUF: 10%, HOU: 5%, NE: 5%

## Optimal Lineups

### Wild Card Round (149.9 projected points)

| Position | Player | Team | Proj | Win Prob | Effective Value |
|----------|--------|------|------|----------|----------------|
| QB | Matthew Stafford | LAR | 20.6 | 65% | 13.4 |
| RB1 | Kyren Williams | LAR | 15.5 | 65% | 10.1 |
| RB2 | Saquon Barkley | PHI | 14.5 | 60% | 8.7 |
| RB3 | D'Andre Swift | CHI | 14.3 | 55% | 7.9 |
| WR1 | Puka Nacua | LAR | 23.4 | 65% | 15.2 |
| WR2 | Davante Adams | LAR | 15.9 | 65% | 10.3 |
| WR3 | A.J. Brown | PHI | 14.7 | 60% | 8.8 |
| TE1 | Dallas Goedert | PHI | 14.3 | 60% | 8.6 |
| TE2 | Tucker Kraft | GB | 16.7 | 45% | 7.5 |

**Strategy**: Focus on Rams and Eagles players with high win probability. Save Broncos/Seahawks elite players for later rounds.

### Divisional Round (111.6 projected points)

| Position | Player | Team | Proj | Win Prob | Effective Value |
|----------|--------|------|----------|----------|----------------|
| QB | Sam Darnold | SEA | 13.8 | 68% | 9.4 |
| RB1 | RJ Harvey | DEN | 12.2 | 70% | 8.5 |
| RB2 | J.K. Dobbins | DEN | 11.6 | 70% | 8.1 |
| RB3 | Kenneth Walker III | SEA | 11.3 | 68% | 7.7 |
| WR1 | Jaxon Smith-Njigba | SEA | 21.2 | 68% | 14.4 |
| WR2 | Courtland Sutton | DEN | 12.9 | 70% | 9.0 |
| WR3 | Troy Franklin | DEN | 10.4 | 70% | 7.3 |
| TE1 | AJ Barner | SEA | 10.2 | 68% | 7.0 |
| TE2 | Evan Engram | DEN | 8.0 | 70% | 5.6 |

**Strategy**: Deploy Broncos and Seahawks players who had their bye week. High confidence in both teams advancing.

### Championship Round (99.0 projected points)

| Position | Player | Team | Proj | Win Prob | Effective Value |
|----------|--------|------|----------|----------|----------------|
| QB | Bo Nix | DEN | 17.9 | 55% | 9.8 |
| RB1 | Zach Charbonnet | SEA | 11.3 | 52% | 5.9 |
| RB2 | Rhamondre Stevenson | NE | 12.8 | 15% | 1.9 |
| RB3 | TreVeyon Henderson | NE | 12.1 | 15% | 1.8 |
| WR1 | Rashid Shaheed | SEA | 8.0 | 52% | 4.2 |
| WR2 | Tory Horton | SEA | 7.4 | 52% | 3.8 |
| WR3 | Cooper Kupp | SEA | 7.3 | 52% | 3.8 |
| TE1 | Colby Parkinson | LAR | 10.1 | 23% | 2.3 |
| TE2 | Colston Loveland | CHI | 12.1 | 18% | 2.2 |

**Strategy**: Use remaining strong players from DEN/SEA. Accept lower-probability picks from eliminated teams.

### Super Bowl (76.0 projected points)

| Position | Player | Team | Proj | Win Prob | Effective Value |
|----------|--------|------|----------|----------|----------------|
| QB | Jalen Hurts | PHI | 18.7 | 12% | 2.2 |
| RB1 | Blake Corum | LAR | 7.2 | 13% | 0.9 |
| RB2 | Kyle Monangai | CHI | 8.6 | 8% | 0.7 |
| WR1 | Marvin Mims Jr. | DEN | 5.8 | 35% | 2.0 |
| WR2 | DeVonta Smith | PHI | 11.9 | 12% | 1.4 |
| WR3 | Rome Odunze | CHI | 12.2 | 8% | 1.0 |
| TE1 | Adam Trautman | DEN | 3.3 | 35% | 1.2 |
| TE2 | Tyler Higbee | LAR | 8.3 | 13% | 1.1 |

**Strategy**: Use remaining players. Limited options available.

## Summary

- **Total Projected Points**: 436.6 points
- **Players Used**: 35 players
- **Key Decision**: Heavy use of Rams in Wild Card pays off (65% win probability)
- **Conservation**: Saved Bo Nix, JSN, and Broncos RBs for later rounds

## Usage

Run the optimizer:

```bash
python3 playoff_optimizer.py
```

The script will:
1. Load all team CSV files
2. Calculate optimal lineups for each week
3. Output results to console and `optimal_lineups.txt`

## Files

- `playoff_optimizer.py` - Main optimization script
- `optimal_lineups.txt` - Generated optimal lineups
- `playoff_fantasy_ai_strategy.txt` - Strategy guidelines
- `PlayoffTeams` - Team information
- `Predictions` - Matchup predictions and odds
- `*Stats*.csv` - Player statistics for each team
