#!/usr/bin/env python3
'''
Owner: Mit
Contains all the helper functions to fetch data from API-FOOTBALL: https://rapidapi.com/api-sports/api/api-football?endpoint=apiendpoint_c8a3886a-cfdb-403f-a6ba-b5a3e84cfbb7
'''

import requests
import datetime
import os
import sys
import json

# Fetch the authentication token for the FOOTBALL API tool.
try:
    AUTH = os.environ.get('API')
except Exception as e:
    sys.exit('Set the authentication token environment variable (set the name to: API) to use FOOTBALL API.')

# Change this variable to get information for other leagues - default league is the English Premiere League.
LEAGUE = 524 # League ID for the Prem

def API(url):
    '''
    Input: url <str> - This is the API get request url.
    Output: A parseable response from the API get request.

    Description: A helper function that will make the API request for you and return data.
    '''
    headers = {
        'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
        'x-rapidapi-key': AUTH
        }
    
    # Submit a GET request to the FOOTBALL API.
    response = requests.request("GET", url, headers=headers)
    
    # Convert string response from the API, into a parseable dict format.
    return json.loads(response.text)

def get_fixtures(date, ID=None):
    '''
    Input: ID <int> <optional> - This is the ID of the league to look for in the API request. By default, we will look at the English Premiere League.
        date <str> - Date from the datetime module in the following format: YYYY-MM-DD ex. 2019-12-25.
    Output: <arr> - A list of all the fixtures for today in the specified league. 

    Description: Given a league, this will return all the open games for the specified day.

    Sample output: [{'fixture_id': 157205, 'league_id': 524, 'league': 
        {'name': 'Premier League', 'country': 'England', 'logo': 'https://media.api-football.com/leagues/2.png', 'flag': 'https://media.api-football.com/flags/gb.svg'}, 'event_date': '2019-12-29T14:00:00+00:00', 
            'event_timestamp': 1577628000, 'firstHalfStart': 1577628000, 'secondHalfStart': 1577631600, 'round': 'Regular Season - 20', 'status': 'Match Finished', 'statusShort': 'FT', 'elapsed': 90, 'venue': 'Emirates Stadium', 'referee': 'Craig Pawson, England', 
            'homeTeam': {'team_id': 42, 'team_name': 'Arsenal', 'logo': 'https://media.api-football.com/teams/42.png'}, 'awayTeam': {'team_id': 49, 'team_name': 'Chelsea', 'logo': 'https://media.api-football.com/teams/49.png'}, 'goalsHomeTeam': 1, 'goalsAwayTeam': 2, 
            'score': {'halftime': '1-0', 'fulltime': '1-2', 'extratime': None, 'penalty': None}}]
    '''
    url = "https://api-football-v1.p.rapidapi.com/v2/fixtures/league/{}/{}".format(str(LEAGUE), date)
    
    # Convert string response from the API, into a parseable dict format.
    response = API(url)

    return response['api']['fixtures']

def generate_rankings():
    '''
    Input: None
    Output: RANK_TABLE <arr> - Array containing the ranks of the teams in the league.

    Description: To save on API calls, only fetch the updated rank information if it hasn't been done before. Otherwise save the information
        so that it can be used for later.
    '''
    url = "https://api-football-v1.p.rapidapi.com/v2/leagueTable/{}".format(str(LEAGUE))
    response = API(url)
    RANK_TABLE = response['api']['standings'][0]
    
    return RANK_TABLE


def past_head2head(fixture_info):
    '''
    Input: fixture_info <dict> - Contains all the fixture information of the upcoming game.
    Output: info <dict> - This contains the historical data on the head 2 head matchup game that was passed into the function.

    Description: Given a match up, fetch all the historical match information when these two teams played including the lineup information
        and the player stats.
    '''
    venue = fixture_info['venue']
    home_team_ID = fixture_info['homeTeam']['team_id']
    home_team_name = fixture_info['homeTeam']['team_name']
    away_team_ID = fixture_info['awayTeam']['team_id']
    away_team_name = fixture_info['awayTeam']['team_name']

    # Search for historical data on head 2 heads with the selected teams.
    url = "https://api-football-v1.p.rapidapi.com/v2/fixtures/h2h/{}/{}".format(home_team_ID, away_team_ID)
    response = API(url)
    fixture_IDs = []

    # Store a list of all the fixture IDs from historical head 2 head matchups.
    for fixture in response['api']['fixtures']:
        fixture_IDs.append(fixture['fixture_id'])

    lineups, player_stats = [], []

    # Store all the lineups and player stats from historical games.
    for fixture_ID in fixture_IDs:
        lineup_url = "https://api-football-v1.p.rapidapi.com/v2/lineups/{}".format(fixture_ID)
        player_stats_url = "https://api-football-v1.p.rapidapi.com/v2/players/fixture/{}".format(fixture_ID)

        lineups.append(API(lineup_url)['api']['lineUps'])
        player_stats.append(API(player_stats_url)['api']['players'])
    
    # Return a dict containing the historical information
    info = {
        'matchup' : '{}-{}'.format(home_team_name, away_team_name),
        'lineups': lineups,
        'player_stats': player_stats
    }

    return info
