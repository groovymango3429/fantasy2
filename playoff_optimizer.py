#!/usr/bin/env python3
"""
Playoff Fantasy Lineup Optimizer

This script optimizes fantasy football lineups for a playoff league where:
- Players can only be used once across all weeks
- PPR scoring with 1.5x premium for tight ends
- Need to maximize total points across all playoff weeks
- Must consider team advancement probabilities
- Broncos and Seahawks have first-round byes
"""

import csv
import os
from typing import Dict, List, Tuple
from dataclasses import dataclass, field

@dataclass
class Player:
    name: str
    team: str
    position: str
    games_played: int
    passing_yards: float = 0
    passing_tds: int = 0
    passing_ints: int = 0
    rushing_yards: float = 0
    rushing_tds: int = 0
    receptions: int = 0
    receiving_yards: float = 0
    receiving_tds: int = 0
    sacks: float = 0
    defense_ints: int = 0
    fumbles_forced: int = 0
    fumbles_recovered: int = 0
    fpts_per_game: float = 0
    total_fpts: float = 0
    used: bool = False
    
    def calculate_playoff_projection(self, te_premium: bool = False) -> float:
        """Calculate projected fantasy points for a single playoff game"""
        # Use their season average as projection
        points = self.fpts_per_game
        
        # Apply TE premium if applicable
        if te_premium and self.position == 'TE':
            # TE gets 1.5 PPR instead of 1.0 PPR
            # Need to recalculate with the extra 0.5 per reception
            additional_points = self.receptions * 0.5 / self.games_played if self.games_played > 0 else 0
            points += additional_points
        
        return points


@dataclass
class Team:
    name: str
    seed: int
    conference: str
    players: List[Player] = field(default_factory=list)
    eliminated: bool = False
    bye_week: bool = False
    
    def get_available_players(self) -> List[Player]:
        """Get players that haven't been used yet"""
        if self.eliminated:
            return []
        return [p for p in self.players if not p.used]


class PlayoffOptimizer:
    def __init__(self):
        self.teams: Dict[str, Team] = {}
        self.all_players: List[Player] = []
        self.used_players: List[Player] = []
        self.lineups: Dict[str, Dict] = {}
        
        # Team advancement probabilities based on predictions
        # Wild Card round winners based on predictions
        self.team_probabilities = {
            # Wild Card Round (Week 1)
            'wildcard': {
                'DEN': 1.0,  # Bye
                'SEA': 1.0,  # Bye
                'NE': 0.55,  # Slight favorite vs LAC
                'LAC': 0.45,
                'JAX': 0.40,  # Underdog vs BUF
                'BUF': 0.60,
                'PIT': 0.45,  # Underdog vs HOU
                'HOU': 0.55,
                'CHI': 0.55,  # Slight favorite vs GB
                'GB': 0.45,
                'PHI': 0.60,  # Favorite vs SF
                'SF': 0.40,
                'CAR': 0.35,  # Underdog vs LAR
                'LAR': 0.65,
            },
            # Divisional Round (Week 2)
            'divisional': {
                'DEN': 0.70,  # Strong team
                'SEA': 0.68,  # Strong team
                'NE': 0.30,
                'BUF': 0.35,
                'HOU': 0.32,
                'CHI': 0.33,
                'PHI': 0.40,
                'LAR': 0.42,
            },
            # Championship Round (Week 3)
            'championship': {
                'DEN': 0.55,
                'SEA': 0.52,
                'NE': 0.15,
                'BUF': 0.20,
                'HOU': 0.15,
                'CHI': 0.18,
                'PHI': 0.22,
                'LAR': 0.23,
            },
            # Super Bowl (Week 4)
            'superbowl': {
                'DEN': 0.35,
                'SEA': 0.32,
                'NE': 0.05,
                'BUF': 0.10,
                'HOU': 0.05,
                'CHI': 0.08,
                'PHI': 0.12,
                'LAR': 0.13,
            }
        }
        
    def load_team_data(self, csv_file: str, team_abbr: str, team_seed: int, conference: str):
        """Load player data from a team's CSV file"""
        team = Team(name=team_abbr, seed=team_seed, conference=conference)
        
        # Broncos and Seahawks have first-round byes
        if team_abbr in ['DEN', 'SEA']:
            team.bye_week = True
        
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
            # Skip first row (category headers), second row is column names
            if len(rows) < 3:
                return
            
            # Column indices: RK, NAME, TEAM, POS, GP, YDS(pass), TD(pass), INT(pass), 
            #                 YDS(rush), TD(rush), REC, YDS(rec), TD(rec), SCK, INT(def), FF, FR, FPTS/G, FPTS
            for row in rows[2:]:  # Skip first 2 header rows
                if len(row) < 19:
                    continue
                
                try:
                    name = row[1].strip()
                    pos = row[3].strip()
                    
                    if not name or not pos:
                        continue
                    
                    player = Player(
                        name=name,
                        team=team_abbr,
                        position=pos,
                        games_played=int(row[4]) if row[4] else 0,
                        passing_yards=float(row[5]) if row[5] else 0,
                        passing_tds=int(row[6]) if row[6] else 0,
                        passing_ints=int(row[7]) if row[7] else 0,
                        rushing_yards=float(row[8]) if row[8] else 0,
                        rushing_tds=int(row[9]) if row[9] else 0,
                        receptions=int(row[10]) if row[10] else 0,
                        receiving_yards=float(row[11]) if row[11] else 0,
                        receiving_tds=int(row[12]) if row[12] else 0,
                        sacks=float(row[13]) if row[13] else 0,
                        defense_ints=int(row[14]) if row[14] else 0,
                        fumbles_forced=int(row[15]) if row[15] else 0,
                        fumbles_recovered=int(row[16]) if row[16] else 0,
                        fpts_per_game=float(row[17]) if row[17] else 0,
                        total_fpts=float(row[18]) if row[18] else 0,
                    )
                    
                    # Only add players with significant fantasy production
                    if player.fpts_per_game > 5.0 or player.position in ['QB', 'TE']:
                        team.players.append(player)
                        self.all_players.append(player)
                        
                except (ValueError, IndexError) as e:
                    continue
        
        self.teams[team_abbr] = team
        
    def load_all_teams(self):
        """Load data for all playoff teams"""
        base_path = '/home/runner/work/fantasy2/fantasy2'
        
        # AFC Teams
        self.load_team_data(f'{base_path}/DenverBroncosStats - Sheet1 (1).csv', 'DEN', 1, 'AFC')
        self.load_team_data(f'{base_path}/NewEnglandPatriotsStats - Sheet1.csv', 'NE', 2, 'AFC')
        self.load_team_data(f'{base_path}/JacksonvilleJaguarsStats - Sheet1.csv', 'JAX', 3, 'AFC')
        self.load_team_data(f'{base_path}/PittsburghSteelersStats - Sheet1.csv', 'PIT', 4, 'AFC')
        self.load_team_data(f'{base_path}/HoustanTexansStats - Sheet1.csv', 'HOU', 5, 'AFC')  # Note: filename has typo
        self.load_team_data(f'{base_path}/LosAngelesChargers.csv', 'LAC', 6, 'AFC')
        
        # NFC Teams
        self.load_team_data(f'{base_path}/SeattleSeahawksStats - Sheet1.csv', 'SEA', 1, 'NFC')
        self.load_team_data(f'{base_path}/ChicagoBearsStats - Sheet1.csv', 'CHI', 2, 'NFC')
        self.load_team_data(f'{base_path}/PhilidelphiaEaglesStats - Sheet1.csv', 'PHI', 3, 'NFC')  # Note: filename has typo
        self.load_team_data(f'{base_path}/CarolinaPanthersStats - Sheet1 (1).csv', 'CAR', 4, 'NFC')
        self.load_team_data(f'{base_path}/LosAngelesRamsStats - Sheet1.csv', 'LAR', 5, 'NFC')
        self.load_team_data(f'{base_path}/GreenBayPackersStats- Sheet1 (1).csv', 'GB', 7, 'NFC')
        
    def calculate_player_value(self, player: Player, week: str) -> float:
        """Calculate effective player value considering advancement probability"""
        base_projection = player.calculate_playoff_projection(te_premium=(player.position == 'TE'))
        team_prob = self.team_probabilities.get(week, {}).get(player.team, 0)
        
        # Teams on bye in wild card round don't play
        if week == 'wildcard' and player.team in ['DEN', 'SEA']:
            return 0.0
        
        # Effective value = projected points × probability of playing
        effective_value = base_projection * team_prob
        
        # Add future value adjustment for elite players on strong teams
        if week in ['wildcard', 'divisional']:
            # Check if this is an elite player (top tier production)
            is_elite = base_projection > 15.0
            
            # Check if team has strong Super Bowl odds
            sb_prob = self.team_probabilities['superbowl'].get(player.team, 0)
            strong_team = sb_prob > 0.25
            
            if is_elite and strong_team:
                # Significantly reduce value to encourage saving for later
                if week == 'wildcard':
                    effective_value *= 0.4  # Heavy penalty in wild card
                else:
                    effective_value *= 0.65  # Moderate penalty in divisional
        
        return effective_value
    
    def get_available_players_by_position(self, position: str) -> List[Tuple[Player, float]]:
        """Get available players for a position with their current week value"""
        players = []
        for player in self.all_players:
            if not player.used and player.position == position and not self.teams[player.team].eliminated:
                players.append(player)
        return players
    
    def select_optimal_lineup(self, week: str) -> Dict:
        """Select the optimal lineup for a given week"""
        lineup = {
            'week': week,
            'QB': None,
            'RB1': None,
            'RB2': None,
            'RB3': None,
            'WR1': None,
            'WR2': None,
            'WR3': None,
            'TE1': None,
            'TE2': None,
            'total_projected': 0
        }
        
        # Get all available players with their values for this week
        available_qbs = [(p, self.calculate_player_value(p, week)) for p in self.get_available_players_by_position('QB')]
        available_rbs = [(p, self.calculate_player_value(p, week)) for p in self.get_available_players_by_position('RB')]
        available_wrs = [(p, self.calculate_player_value(p, week)) for p in self.get_available_players_by_position('WR')]
        available_tes = [(p, self.calculate_player_value(p, week)) for p in self.get_available_players_by_position('TE')]
        
        # Sort by value (descending)
        available_qbs.sort(key=lambda x: x[1], reverse=True)
        available_rbs.sort(key=lambda x: x[1], reverse=True)
        available_wrs.sort(key=lambda x: x[1], reverse=True)
        available_tes.sort(key=lambda x: x[1], reverse=True)
        
        # Select best QB
        if available_qbs:
            lineup['QB'] = available_qbs[0][0]
            lineup['QB'].used = True
            self.used_players.append(lineup['QB'])
        
        # Select best 3 RBs
        for i, slot in enumerate(['RB1', 'RB2', 'RB3']):
            if i < len(available_rbs):
                lineup[slot] = available_rbs[i][0]
                lineup[slot].used = True
                self.used_players.append(lineup[slot])
        
        # Select best 3 WRs
        for i, slot in enumerate(['WR1', 'WR2', 'WR3']):
            if i < len(available_wrs):
                lineup[slot] = available_wrs[i][0]
                lineup[slot].used = True
                self.used_players.append(lineup[slot])
        
        # Select best 2 TEs
        for i, slot in enumerate(['TE1', 'TE2']):
            if i < len(available_tes):
                lineup[slot] = available_tes[i][0]
                lineup[slot].used = True
                self.used_players.append(lineup[slot])
        
        # Calculate total projected points
        for slot, player in lineup.items():
            if player and slot != 'week' and slot != 'total_projected':
                lineup['total_projected'] += player.calculate_playoff_projection(te_premium=(player.position == 'TE'))
        
        return lineup
    
    def eliminate_teams(self, week: str):
        """Mark teams as eliminated based on predictions"""
        if week == 'divisional':
            # Eliminate wild card losers based on predictions
            # Keep: LAR (beat CAR), CHI (beat GB), PHI (beat SF), NE (beat LAC), BUF (beat JAX), HOU (beat PIT)
            losers = ['LAC', 'JAX', 'PIT', 'GB', 'SF', 'CAR']
            for team_abbr in losers:
                if team_abbr in self.teams:
                    self.teams[team_abbr].eliminated = True
        elif week == 'championship':
            # Eliminate divisional round losers
            # Keep top 4 teams likely to make championship: DEN, SEA, LAR/PHI (NFC), NE/BUF/HOU (AFC)
            # More conservative - only eliminate teams with very low probability
            for team_abbr, team in self.teams.items():
                if self.team_probabilities['championship'].get(team_abbr, 0) < 0.18:
                    team.eliminated = True
        elif week == 'superbowl':
            # Keep only teams with highest Super Bowl probability
            for team_abbr, team in self.teams.items():
                if self.team_probabilities['superbowl'].get(team_abbr, 0) < 0.08:
                    team.eliminated = True
    
    def run_optimization(self):
        """Run the full optimization across all playoff weeks"""
        print("=" * 80)
        print("PLAYOFF FANTASY LINEUP OPTIMIZER")
        print("=" * 80)
        print("\nLoading team data...")
        self.load_all_teams()
        
        print(f"Loaded {len(self.all_players)} players from {len(self.teams)} teams")
        print("\nTeams with first-round bye: Denver Broncos, Seattle Seahawks")
        
        weeks = ['wildcard', 'divisional', 'championship', 'superbowl']
        
        output_lines = []
        output_lines.append("=" * 80)
        output_lines.append("PLAYOFF FANTASY LINEUP OPTIMIZER RESULTS")
        output_lines.append("=" * 80)
        output_lines.append("\nSTRATEGY:")
        output_lines.append("- PPR scoring with 1.5x premium for tight ends")
        output_lines.append("- Each player can only be used once")
        output_lines.append("- Maximize total points across all playoff weeks")
        output_lines.append("- Consider team advancement probabilities")
        output_lines.append("- Save elite players on Super Bowl contenders for later rounds")
        output_lines.append("\n")
        
        for week in weeks:
            print("\n" + "=" * 80)
            print(f"OPTIMIZING FOR: {week.upper()} ROUND")
            print("=" * 80)
            
            lineup = self.select_optimal_lineup(week)
            self.lineups[week] = lineup
            
            output_lines.append("=" * 80)
            output_lines.append(f"{week.upper()} ROUND LINEUP")
            output_lines.append("=" * 80)
            
            print(f"\nOptimal Lineup for {week.upper()} Round:")
            print("-" * 80)
            output_lines.append("")
            
            for slot in ['QB', 'RB1', 'RB2', 'RB3', 'WR1', 'WR2', 'WR3', 'TE1', 'TE2']:
                player = lineup[slot]
                if player:
                    proj = player.calculate_playoff_projection(te_premium=(player.position == 'TE'))
                    prob = self.team_probabilities[week].get(player.team, 0)
                    effective = proj * prob
                    line = f"{slot:5} | {player.name:25} | {player.team:4} | {player.position:3} | Proj: {proj:5.1f} | Prob: {prob:.0%} | Value: {effective:5.1f}"
                    print(line)
                    output_lines.append(line)
                else:
                    line = f"{slot:5} | {'EMPTY':25} |"
                    print(line)
                    output_lines.append(line)
            
            print("-" * 80)
            print(f"Total Projected Points: {lineup['total_projected']:.1f}")
            output_lines.append("-" * 80)
            output_lines.append(f"Total Projected Points: {lineup['total_projected']:.1f}")
            output_lines.append("")
            
            # Eliminate losing teams before next week
            self.eliminate_teams(week)
        
        # Print summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        total_points = sum(lineup['total_projected'] for lineup in self.lineups.values())
        print(f"\nTotal Projected Points Across All Weeks: {total_points:.1f}")
        print(f"Players Used: {len(self.used_players)}")
        
        output_lines.append("=" * 80)
        output_lines.append("SUMMARY")
        output_lines.append("=" * 80)
        output_lines.append(f"\nTotal Projected Points Across All Weeks: {total_points:.1f}")
        output_lines.append(f"Players Used: {len(self.used_players)}")
        
        # Print week by week breakdown
        print("\nWeek-by-Week Breakdown:")
        output_lines.append("\nWeek-by-Week Breakdown:")
        for week in weeks:
            lineup = self.lineups[week]
            line = f"{week.capitalize():15} | {lineup['total_projected']:6.1f} points"
            print(line)
            output_lines.append(line)
        
        # Save to file
        with open('/home/runner/work/fantasy2/fantasy2/optimal_lineups.txt', 'w') as f:
            f.write('\n'.join(output_lines))
        
        print("\n" + "=" * 80)
        print("Results saved to: optimal_lineups.txt")
        print("=" * 80)


def main():
    optimizer = PlayoffOptimizer()
    optimizer.run_optimization()


if __name__ == '__main__':
    main()
