#! /usr/bin/python3

import requests
import json
import sys
from functools import partial

# Global dictionnary used to store team ids, filled in get_teams()
team_dict = {}


def get_team_name(teamid):
    """
    Returns a team name
    :param teamid: Id of team. Can be obtain with get_teams()
    :return: Name of team with teamid
    """
    team_request = requests.get('https://statsapi.web.nhl.com/api/v1/teams/' + str(teamid))
    try:
        team_request.raise_for_status()
    except Exception as exc:
        print('There was an problem: %s' % exc)
    team_text = team_request.text
    team_json = json.loads(team_text)
    return team_json['teams'][0]['name']


def get_player(playerid):
    """ Returns a dictionnary with player infos from player id. Used in get_stats() """
    player_request = requests.get('https://statsapi.web.nhl.com/api/v1/people/' + str(playerid))
    player_dict = {}
    try:
        player_request.raise_for_status()
    except Exception as exc:
        print('There was an problem: %s' % exc)
    player_text = player_request.text
    player_json = json.loads(player_text)
    player_info = player_json["people"][0]
    player_fullname = player_info["fullName"]
    player_position = player_info["primaryPosition"]["abbreviation"]
    player_dict["name"] = player_fullname
    player_dict["position"] = player_position
    return player_dict


def get_standings(season=None):
    """
    Gets and prints standings for wanted season
    :param season: Wanted season (YYYYYY format)
    """
    if season:
        if len(season) != 8 or not season.isdigit():
            print("Please enter a season with following format : 20162017")
            print("Continuing with current season ...")
            standings_requests = requests.get('https://statsapi.web.nhl.com/api/v1/standings/')
        else:
            print("Season: " + season)
            standings_requests = requests.get('https://statsapi.web.nhl.com/api/v1/standings/?season=' + season)
    else:
        print("Season : current")
        standings_requests = requests.get('https://statsapi.web.nhl.com/api/v1/standings/')
    try:
        standings_requests.raise_for_status()
    except Exception as exc:
        print('There was an problem: %s' % exc)
    standings_text = standings_requests.text
    standings_json = json.loads(standings_text)
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


# TODO : manage year using current year
def get_draft_year(arg_list=[]):
    """
    Gets and prints drafted rookies for a Draft year.
    :param arg_list: Optionnal. List is composed of year, round and picks. Values by default are 2018, 0 (round 1), 25.
    """
    year = 2018
    round_nb = 0
    picks = 25
    if len(arg_list) == 1:
        year = int(arg_list[0])
    elif len(arg_list) == 2:
        year = int(arg_list[0])
        round_nb = int(arg_list[1])-1
    elif len(arg_list) == 3:
        year = int(arg_list[0])
        round_nb = int(arg_list[1])-1
        picks = int(arg_list[2])
    if 1980 < year < 2019:
        draft_request = requests.get('https://statsapi.web.nhl.com/api/v1/draft/' + str(year))
    else:
        print("Please pick a draft year between 1980 and 2018. Continuing with 2018 Draft.")
        draft_request = requests.get('https://statsapi.web.nhl.com/api/v1/draft/2018')
    print(str(year) + ' Draft ! Round n°' + str(round_nb + 1) + ' Picks:' + str(picks))
    try:
        draft_request.raise_for_status()
    except Exception as exc:
        print('There was an problem: %s' % exc)
    draft_text = draft_request.text
    draft_json = json.loads(draft_text)
    draft_round = draft_json['drafts'][0]['rounds'][round_nb]
    print('#'*46)
    for player in draft_round["picks"][:picks]:
        draft_info = '{}-{} {}'.format(player["round"], player["pickInRound"], player['prospect']['fullName'])
        team = player["team"]["name"]
        print(draft_info.ljust(25, ' ') + team.ljust(25, ' '))
    print('#'*46)


def get_today():
    """ Gets and prints today's games with score and status """
    live_request = requests.get('https://statsapi.web.nhl.com/api/v1/schedule')
    try:
        live_request.raise_for_status()
    except Exception as exc:
        print('There was an problem: %s' % exc)
    live_text = live_request.text
    live_json = json.loads(live_text)
    print('{} game(s) today ({})'.format(live_json["totalGames"], live_json["dates"][0]["date"]))
    print('#'*60)
    for game in live_json["dates"][0]["games"]:
        team1 = game["teams"]["away"]["team"]["name"]
        team2 = game["teams"]["home"]["team"]["name"]
        scoreboard = "  {}-{}  ".format(game["teams"]["away"]["score"], game["teams"]["home"]["score"])
        status = "({})".format(game["status"]["abstractGameState"])
        print(team1.rjust(22, ' ') + scoreboard + team2.ljust(22, ' ') + status)
    print('#'*60)


def get_teams():
    """ Retrieves teams info into a global team_dict """
    global team_dict
    teams_request = requests.get('https://statsapi.web.nhl.com/api/v1/teams')
    try:
        teams_request.raise_for_status()
    except Exception as exc:
        print('There was an problem: %s' % exc)
    teams_text = teams_request.text
    teams_json = json.loads(teams_text)
    for team in range(len(teams_json["teams"])):
        team_id = teams_json["teams"][team]["id"]
        team_dict[team_id] = {}
        team_dict[team_id]["name"] = teams_json["teams"][team]["name"]
        team_dict[team_id]["abbrev"] = teams_json["teams"][team]["abbreviation"]
        team_dict[team_id]["firstyear"] = teams_json["teams"][team]["firstYearOfPlay"]
        team_dict[team_id]["conf"] = teams_json["teams"][team]["conference"]["name"]
        team_dict[team_id]["div"] = teams_json["teams"][team]["division"]["name"]


def print_teams():
    """ Prints teams w/ infos using team_dict """
    print("ID Name" + ' ' * 18 + "Abbr 1stY Conf    Div")
    print('*'*55)
    for teamid, team in team_dict.items():
        team_id = str(teamid)
        team_name = team["name"]
        team_other_infos = "{}  {} {} {}".format(team["abbrev"], team["firstyear"], team["conf"], team["div"])
        print(team_id.ljust(3) + team_name.ljust(22) + team_other_infos)
    print('*'*55)


# TODO : sort by position
def get_roster(arg_list):
    """
    Prints team roster from teamid
    :param arg_list: List is composed of teamid and season.(in order)(season is optionnal)
    """
    if len(arg_list) == 1:
        teamid = str(arg_list[0])
        team_request = requests.get('https://statsapi.web.nhl.com/api/v1/teams/' + str(teamid) + '?expand=team.roster')
        print("Current season roster")
    elif len(arg_list) == 2:
        teamid = str(arg_list[0])
        season = str(arg_list[1])
        team_request = requests.get('https://statsapi.web.nhl.com/api/v1/teams/' + str(teamid)
                                    + '?expand=team.roster&season=' + season)
        print(season + ' roster')
    try:
        team_request.raise_for_status()
    except Exception as exc:
        print('There was an problem: %s' % exc)
    team_name = get_team_name(teamid)
    team_text = team_request.text
    team_roster_json = json.loads(team_text)
    roster = team_roster_json["teams"][0]["roster"]["roster"]
    print(team_name.center(47, '#'))
    for player in roster:
        player_fullname = player["person"]["fullName"]
        position = player["position"]["name"]
        player_id = player["person"]["id"]
        print(player_fullname.ljust(25) + position.ljust(15) + str(player_id))
    print('#'*47)


def get_stats(arg_list):
    """
    Gets and prints stats of a player.
    :param arg_list: List is composed of playerid and season.(in order)(season is optionnal)
    """
    if len(arg_list) == 1:
        playerid = str(arg_list[0])
        player_request = requests.get('https://statsapi.web.nhl.com/api/v1/people/' + str(playerid)
                                      + '/stats?stats=statsSingleSeason')
    elif len(arg_list) == 2:
        playerid = str(arg_list[0])
        season = str(arg_list[1])
        player_request = requests.get('https://statsapi.web.nhl.com/api/v1/people/' + str(playerid)
                                      + '/stats?stats=statsSingleSeason&season=' + season)
    try:
        player_request.raise_for_status()
    except Exception as exc:
        print('There was an problem: %s' % exc)
    player_text = player_request.text
    player_roster_json = json.loads(player_text)
    player_stats = player_roster_json["stats"][0]["splits"][0]
    # getting player infos
    player_dict = get_player(playerid)
    player_name = player_dict.get("name")
    player_position = player_dict.get("position")
    season = player_stats["season"]
    print('###### {} - {} ({} stats)'.format(player_name, player_position, season))
    if 'G' not in player_position:
        print('Games : {}'.format(player_stats["stat"]["games"]))
        print('goals-assists-points : {}-{}-({})'.format(player_stats["stat"]["goals"], player_stats["stat"]["assists"],
                                                         player_stats["stat"]["points"]))
        print('+/- : {}'.format(player_stats["stat"]["plusMinus"]))
        print('GWG : {}'.format(player_stats["stat"]["gameWinningGoals"]))
        print('SHG : {}'.format(player_stats["stat"]["shortHandedGoals"]))
        print('PPGoals - PPPoints : {}-{}'.format(player_stats["stat"]["powerPlayGoals"],
                                                  player_stats["stat"]["powerPlayPoints"]))
        print('Pims : {}'.format(player_stats["stat"]["pim"]))
        print('TOI : {}'.format(player_stats["stat"]["timeOnIcePerGame"]))
    else:
        print('Games : {}'.format(player_stats["stat"]["games"]))
        print('W-L-OT : {} - {} - {}'.format(player_stats["stat"]["wins"], player_stats["stat"]["losses"],
                                             player_stats["stat"]["ot"]))
        print('SO : {}'.format(player_stats["stat"]["shutouts"]))
        print('Save %: {}'.format(player_stats["stat"]["savePercentage"]))
        print('GAA : {}'.format(player_stats["stat"]["goalAgainstAverage"]))


def choice_to_function(choice, args=None):
    """
    Switcher
    :param choice: User choice, corresponds to a function
    :param args: optional args depending on choice
    :return: chosen function
    """
    if args:
        switcher = {
            "standings": partial(get_standings, *args),
            "draft": partial(get_draft_year, args),
            "roster": partial(get_roster, args),
            "stats": partial(get_stats, args)
        }
    else:
        switcher = {
            "standings": get_standings,
            "draft": get_draft_year,
            "today": get_today,
            "teams": print_teams,
            "quit": sys.exit
        }
    # Switcher
    func = switcher.get(choice, lambda: "nothing")
    # Execute the function
    return func()


if __name__ == '__main__':
    # Fills team_dict
    get_teams()

    help = " Welcome. Supported calls: \n" \
                  " - today : get today's games \n" \
                  " - standings [season] : print the standings \n" \
                  " - teams : print teams with some infos (including ids, useful for roster) \n" \
                  " - roster teamid [season] : print roster of specified team (useful for stats) \n" \
                  " - stats playerid [season] : print player stats \n" \
                  " - draft [year] [round] [picks] : print the draft results \n" \
                  " - help : print this description \n" \
                  " - quit : to quit lul \n" \
                  "[] = optionnal argument"

    print(help)
    print("\n Choice?")
    while True:
        input_user = input().split()
        if input_user[0] == 'help':
            print(help)
        elif len(input_user) >= 2:
            choice_to_function(input_user[0], input_user[1:])
        else:
            choice_to_function(input_user[0])
        print("\n Next choice?")
