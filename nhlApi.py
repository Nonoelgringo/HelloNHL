#! python3

import requests
import json
import logging

#res = requests.get('https://statsapi.web.nhl.com/api/v1/draft/prospects/58581')

#print(res.text)

def getTeam(teamid):
    team_request = requests.get('https://statsapi.web.nhl.com/api/v1/teams/' + str(teamid))
    try:
        team_request.raise_for_status()
    except Exception as exc:
        print('There was an problem: %s' % (exc))
    team = team_request.text
    team_json = json.loads(team)
    print('Team name : ' + team_json['teams'][0]['name'] + '\n' + 'Division : ' + team_json['teams'][0]['division']['name'] )

#getTeam(3)

print('Enter a team id')
team = input()
getTeam(team)