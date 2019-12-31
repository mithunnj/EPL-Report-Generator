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

# Print pretty JSON
def pp_json(json_thing, sort=True, indents=4):
    if type(json_thing) is str:
        print(json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))
    else:
        print(json.dumps(json_thing, sort_keys=sort, indent=indents))
    return None


def main():
    # Ask user for date.
    #date = input('Enter an upcoming date (NOTE: Specifiy date in the following format - YYYY-MM-DD): ') #NOTE: Uncomment when you're done testing
    date = '2020-01-01'

    # Get all the matchups for that day in a list.
    games = get_fixtures(date)

    # Get the past head2head matchup information for the games.
    for game in games:
        data = past_head2head(game)

        # Print pretty JSON data
        pp_json(data)
        print('\n')

main()