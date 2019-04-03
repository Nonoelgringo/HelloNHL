#! python3

import requests
import json
import sys
from functools import partial


def get_team(teamid):
    team_request = requests.get('https://statsapi.web.nhl.com/api/v1/teams/' + str(teamid))
    try:
        team_request.raise_for_status()
    except Exception as exc:
        print('There was an problem: %s' % exc)
    team = team_request.text
    team_json = json.loads(team)
    print('Team name : ' + team_json['teams'][0]['name']
          + '\n Division : ' + team_json['teams'][0]['division']['name'])


def get_standings(season=None):
    if season:
        if len(season) != 8:
            print("Please enter a season like this : 20162017")
            sys.exit()
        else:
            standings_requests = requests.get('https://statsapi.web.nhl.com/api/v1/standings/?season=' + season)
    else:
        standings_requests = requests.get('https://statsapi.web.nhl.com/api/v1/standings/')
    try:
        standings_requests.raise_for_status()
    except Exception as exc:
        print('There was an problem: %s' % exc)
    standings_data = standings_requests.text
    standings_json = json.loads(standings_data)
    for division in range(len(standings_json["records"])):
        print(standings_json["records"][division]["division"]["name"])
        for team in standings_json["records"][division]["teamRecords"]:
            if 'clinchIndicator' in team:
                team_name = '{} ({})'.format(team["team"]["name"], team["clinchIndicator"])
            else:
                team_name = team["team"]["name"]
            team_stats = '{}pt  {}-{}-{}'.format(team["points"], team["leagueRecord"]["wins"],
                                                 team["leagueRecord"]["losses"], team["leagueRecord"]["ot"])
            print('   ' + team_name.ljust(25, ' ') + team_stats)


def get_draft_year(year='2018', round=0, picks=25):
    draft_request = requests.get('https://statsapi.web.nhl.com/api/v1/draft/' + year)
    print(year + ' Draft ! Round n°' + str(round + 1) + ' Picks:' + str(picks))
    try:
        draft_request.raise_for_status()
    except Exception as exc:
        print('There was an problem: %s' % exc)
    draft = draft_request.text
    draft_json = json.loads(draft)
    try:
        draft_round = draft_json['drafts'][0]['rounds'][round]
    except KeyError:
        print('Please pick a valid draft year ;)')
        sys.exit()
    print('#'*46)
    for player in draft_round["picks"][:picks]:
        draft_info = '{}-{} {}'.format(player["round"], player["pickInRound"], player['prospect']['fullName'])
        team = player["team"]["name"]
        print(draft_info.ljust(25, ' ') + team.ljust(25, ' '))
    print('#'*46)


def get_today():
    live_request = requests.get('https://statsapi.web.nhl.com/api/v1/schedule')
    try:
        live_request.raise_for_status()
    except Exception as exc:
        print('There was an problem: %s' % exc)

    live = live_request.text
    live_json = json.loads(live)

    print('{} games today ({})'.format(live_json["totalGames"], live_json["dates"][0]["date"]))
    print('#'*60)
    for game in live_json["dates"][0]["games"]:
        team1 = game["teams"]["away"]["team"]["name"]
        team2 = game["teams"]["home"]["team"]["name"]
        scoreboard = "  {}-{}  ".format(game["teams"]["away"]["score"], game["teams"]["home"]["score"])
        status = "({})".format(game["status"]["abstractGameState"])
        print(team1.rjust(22, ' ') + scoreboard + team2.ljust(22, ' ') + status)
    print('#'*60)


def choice_to_function(choice, *args):
    if args:
        switcher = {
            "standings": partial(get_standings, *args),
            "draft": partial(get_draft_year, *args)
        }
    else:
        switcher = {
            "standings": get_standings,
            "draft": get_draft_year,
            "today": get_today,
            "quit": sys.exit
        }
    # switcher
    func = switcher.get(choice, lambda: "nothing")
    # Execute the function
    return func()


choices = {"standing"}
description = " Welcome. Supported calls \n" \
                  " - standings : print the standings \n" \
                  " - draft : print the draft result (you can choose the year, round and picks) \n" \
                  " - today : get today's schedule \n" \
                  " - quit : to quit lul"
print(description)
while True:
    input_user = input().split()
    if len(input_user) == 2:
        choice_to_function(input_user[0], input_user[1])
    else:
        choice_to_function(input_user[0])
    print("next choice.")
