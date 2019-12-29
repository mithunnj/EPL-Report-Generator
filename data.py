#!/usr/bin/env python3
'''

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


def get_fixtures(ID=None, date):
    '''
    Input: ID <int> <optional> - This is the ID of the league to look for in the API request. By default, we will look at the English Premiere League.
        date <str> - Date from the datetime module in the following format: YYYY-MM-DD ex. 2019-12-25.
    Output: <arr> - A list of all the fixtures for today in the specified league. 

    Description: Given a league, this will return all the open games for the specified day.
    '''
    url = "https://api-football-v1.p.rapidapi.com/v2/fixtures/league/{}/{}".format(str(LEAGUE), date)
    headers = {
        'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
        'x-rapidapi-key': AUTH
        }
    
    # Submit a GET request to the FOOTBALL API.
    response = requests.request(
        "GET", 
        "https://api-football-v1.p.rapidapi.com/v2/teams/league/{}/{}".format(ID, date) if ID else url, 
        headers=headers)
    
    # Convert string response from the API, into a parseable dict format.
    parseable_response = json.loads(response.text)

    return parseable_response['api']['fixtures']

get_fixtures()
