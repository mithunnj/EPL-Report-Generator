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

def get_fixtures(date):
    '''
    Input: date <str> - Date from the datetime module in the following format: YYYY-MM-DD ex. 2019-12-25.
    Output: <arr> - A list of all the fixtures for today in the specified league. 

    Description: Given a league, this will return all the open games for the specified day.

    Sample output: [{'fixture_id': 157205, 'league_id': 524, 'league': 
        {'name': 'Premier League', 'country': 'England', 'logo': 'https://media.api-football.com/leagues/2.png', 'flag': 'https://media.api-football.com/flags/gb.svg'}, 'event_date': '2019-12-29T14:00:00+00:00', 
            'event_timestamp': 1577628000, 'firstHalfStart': 1577628000, 'secondHalfStart': 1577631600, 'round': 'Regular Season - 20', 'status': 'Match Finished', 'statusShort': 'FT', 'elapsed': 90, 'venue': 'Emirates Stadium', 'referee': 'Craig Pawson, England', 
            'homeTeam': {'team_id': 42, 'team_name': 'Arsenal', 'logo': 'https://media.api-football.com/teams/42.png'}, 'awayTeam': {'team_id': 49, 'team_name': 'Chelsea', 'logo': 'https://media.api-football.com/teams/49.png'}, 'goalsHomeTeam': 1, 'goalsAwayTeam': 2, 
            'score': {'halftime': '1-0', 'fulltime': '1-2', 'extratime': None, 'penalty': None}}]
    '''
    url = "https://api-football-v1.p.rapidapi.com/v2/fixtures/league/{}/{}".format(str(LEAGUE), date)
    
    # Retrieve API response given GET request url for all fixtures for a given date.
    response = API(url)

    # Check that the response included the api key.
    api_result = response.get('api')
    if not api_result:
        return None
    
    # Check that the response included the fixtures key. If it returned fixtures, give that back to the user call.
    fixture_result = api_result.get('fixtures')
    if not fixture_result:
        return None
    else:
        return fixture_result

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

def validate_JSON(info, check_type):
    '''
    Input: info <dict> - This is the JSON response object.
        check_fixture <str> - Specify the type of JSON response we are analyzing, to ensure that we use the proper expected parameter checks.
    Output: ValueError if the parameter doesn't exist in the JSON object, otherwise will return to continue the task execution.

    Description: Check that the incoming information contains the appropriate parameters, and if there is an issue, raise ValueError.
    '''
    expected_param = [] # These are parameters that should be validated in the incoming JSON.
    if check_type == 'fixture_info':
        expected_param = [
            'fixture_id',
            'league_id',
            'event_date',
            'homeTeam',
            'awayTeam'
        ]
    elif check_type == 'h2h':
        expected_param = [
            'teams',
            'results',
            'fixtures'
        ]
    else: # Handle corner case of unexpected check parameter that is passed in.
        raise ValueError('Unexpected check parameter value was passed into validate_JSON: {}'.format(check_type))

    # Check that the parameter exists in the incoming JSON.
    for parameter in expected_param:
        if not info.get(parameter):
            raise ValueError('JSON validation error - Does not contain the following parameter: {}.'.format(parameter))

    return


def past_head2head(fixture_info):
    '''
    Input: fixture_info <dict> - Contains all the fixture information of the upcoming game.
    Output: info <dict> - This contains the historical data on the head 2 head matchup game that was passed into the function.

    Description: Given a match up, fetch all the historical match information when these two teams played including the lineup information
        and the player stats.
    '''
    try:
        # Validate incoming JSON information
        validate_JSON(fixture_info, 'fixture_info')

        home_team_ID = fixture_info['homeTeam']['team_id']
        home_team_name = fixture_info['homeTeam']['team_name']
        away_team_ID = fixture_info['awayTeam']['team_id']
        away_team_name = fixture_info['awayTeam']['team_name']
        teams = [home_team_name, away_team_name]

        # Search for historical data on head 2 heads with the selected teams.
        url = "https://api-football-v1.p.rapidapi.com/v2/fixtures/h2h/{}/{}".format(home_team_ID, away_team_ID)
        response = API(url)

        # Validate incoming JSON information
        validate_JSON(response['api'], 'h2h')

        fixture_IDs = {}
        # Store a list of all the fixture IDs from historical head 2 head matchups, including the dates.
        for num in range(len(response['api']['fixtures'])):
            fixture_IDs[num] = {
                'date': response['api']['fixtures'][num]['event_date'],
                'fixture_id': response['api']['fixtures'][num]['fixture_id']
            }

        # I want an ordered list by date
        stats = {}

        for key in fixture_IDs.keys():
            lineup_url = "https://api-football-v1.p.rapidapi.com/v2/lineups/{}".format(fixture_IDs[key]['fixture_id'])
            player_stats_url = "https://api-football-v1.p.rapidapi.com/v2/players/fixture/{}".format(fixture_IDs[key]['fixture_id'])

            payload = {}

            # Store all the lineups and player stats from the game.
            lineup_data = API(lineup_url)
            player_stat_data = API(player_stats_url)

            # Validate that there is historical data available for the key
            try:
                if lineup_data['api']['results'] == 0 or player_stat_data['api']['results'] == 0:
                    continue
            except Exception as e:
                print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
                print('Occured for the following fixture_ID: {}'.format(fixture_IDs[key]))

            for team in teams:
                coach = lineup_data['api']['lineUps'][team]['coach']
                formation = lineup_data['api']['lineUps'][team]['formation']
                startingXI = {}

                for num in range(len(lineup_data['api']['lineUps'][team]['startXI'])):
                    name = lineup_data['api']['lineUps'][team]['startXI'][num]['player']
                    number = lineup_data['api']['lineUps'][team]['startXI'][num]['number']
                    position = lineup_data['api']['lineUps'][team]['startXI'][num]['pos']
                    player_ID = lineup_data['api']['lineUps'][team]['startXI'][num]['player_id']
                    player_stat = {}

                    for specific_player in player_stat_data['api']['players']:
                        if specific_player['player_id'] == player_ID:
                            player_stat = {
                                'rating': specific_player['rating'],
                                'minutes_played': specific_player['minutes_played'],
                                'captain': specific_player['captain'],
                                'subtitute': specific_player['substitute'],
                                'offsides': specific_player['offsides'],
                                'shots': specific_player['shots'],
                                'goals': specific_player['goals'],
                                'passes': specific_player['passes'],
                                'tackles': specific_player['tackles'],
                                'duels': specific_player['duels'],
                                'dribbles': specific_player['dribbles'],
                                'fouls': specific_player['fouls'],
                                'cards': specific_player['cards'],
                                'penalty': specific_player['penalty']
                            }
                            break

                    startingXI[name] = {
                        'number': number,
                        'position': position,
                        'stat': player_stat
                    }

                payload[team] = {
                    'coach': coach,
                    'formation': formation,
                    'startingXI': startingXI
                }
            
            stats[fixture_IDs[key]['date']] = payload

        # Return a dict containing the historical information
        info = {
            'matchup' : '{}-{}'.format(home_team_name, away_team_name),
            'stats': stats
        }

        return info
    except Exception as e:
        print('Error: {}, returned for the following fixture: {}.'.format(e, fixture_info))
        return

def payload_generator(game, date):
    '''
    Input:
    Output:

    Description:
    '''

    # Get matchup, lineups, and player_stats for the game
    data = past_head2head(game)

    # Initial payload structure
    payload = {
        'gameday': date,
        'matchup': {
            'teams': {
                'teamA': data['matchup'].split('-')[0],
                'teamB': data['matchup'].split('-')[0]
            },
            'historicalData': data['stats']
        }
    }

    return payload




