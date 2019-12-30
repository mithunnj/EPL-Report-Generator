#!/usr/bin/env python3
'''
Owner: Mit
Main task execution script.
'''

from data import get_fixtures, past_head2head
import sys
import json

# Coloured text
CGREEN = '\n' + '\33[32m'
CRED = '\n' + '\33[31m'
CYELLOW = '\n' + '\33[33m'
CEND = '\033[0m' + '\n'

def main():
    ''' 
    '''
    # Print welcome message
    print(CYELLOW + ' ==== Welcome to Automated Data Tracking ====' + CEND)

    # Ask user for date.
    #date = input('Enter an upcoming date (NOTE: Specifiy date in the following format - YYYY-MM-DD): ') #NOTE: Uncomment when you're done testing
    date = '2020-01-01'

    # Get all the matchups for that day
    games = get_fixtures(date)

    with open('{}.txt'.format(date), 'w+') as write_file:
        
        for game in games:
            try:
                data = past_head2head(game)
            except Exception as e:
                print('Error for {}: {} \n\n'.format(game, e))
                continue

            content = []

            # Open a text file the game information to
            content.append('\n\n=== {} Historical Data === \n'.format(data['matchup'])) # Title for the matchup entry

            # Parse the two teams from the heading.
            teamA = data['matchup'].split('-')[0]
            teamB = data['matchup'].split('-')[1]

            entries = len(data['lineups']) # Get the total number of historical data entries.

            for num in range(entries):

                # Seperate the player stats for each team.
                teamA_player_stats, teamB_player_stats = "", ""
                for player in data['player_stats'][num]:
                    if teamA in player['team_name']:
                        teamA_player_stats += json.dumps(player)
                    else:
                        teamB_player_stats += json.dumps(player)

                content.append('\n\n' + str(num+1) + '.\n') # Ordered list 

                try:
                    lineupA = json.dumps(data['lineups'][num][teamA])
                except:
                    lineupA = 'Error fetching lineup information for {}.'.format(teamA)
                try:
                    lineupB = json.dumps(data['lineups'][num][teamB])
                except:
                    lineupB = 'Error fetching lineup information for {}.'.format(teamB)
                
                content.append(
                    '== {} == \n'.format(teamA) +
                    '= Lineup info =\n' + 
                    lineupA +
                    '\n = Player Stats = \n' + 
                    teamA_player_stats +

                    '\n\n== {} == \n'.format(teamB) +
                    '= Lineup info =\n' + 
                    lineupB +
                    '\n = Player Stats = \n' + 
                    teamB_player_stats 
                )   

            write_file.writelines(content)
    
    write_file.close()


main()