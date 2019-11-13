from selenium import webdriver
import time
import json
import pandas as pd
from pandas.io.json import json_normalize
import os
import getpass


def sc_login_selenium():
    sc_url = "https://supercoach.heraldsun.com.au/#/afl/draft/team"
    sc_user = 'richards_0123@hotmail.com'
    sc_pass = getpass.getpass()
    driver = webdriver.Chrome()
    driver.implicitly_wait(3)
    driver.get(sc_url)
    driver.find_element_by_xpath('//*[@id="mat-dialog-0"]/ng-component/div/div[2]/div/div[3]/button[2]').click()
    driver.find_element_by_name("email").send_keys(sc_user)
    driver.find_element_by_name("password").send_keys(sc_pass)
    driver.find_element_by_xpath('//*[@id="r-login-container"]/div/div[1]/form/div/div/button').click()
    return driver


def download_all_match_results():
    teams = {
        "Paul": "344",
        "Anthony": "831",
        "Lester": "7061",
        "Simon": "8740",
        "James": "11070",
        "Luke": "397",
        "Jordan": "25252"
    }
    rounds = 23

    driver = sc_login_selenium()
    time.sleep(5)
    driver.get("https://supercoach.heraldsun.com.au/#/afl/draft/gameday")
    time.sleep(5)

    for round_number in range(1, rounds + 1):
        for opponent_id in teams:
            print(teams[opponent_id])
            match_url = "https://supercoach.heraldsun.com.au/afl/draft/service/match_centre/update?" \
                        "opponent_id={}&round={}".format(teams[opponent_id], round_number)
            driver.get(match_url)
            match_source = driver.page_source
            remove_from_start = '<html><head></head><body><pre style="word-wrap: break-word; white-space: pre-wrap;">'
            remove_from_end = '</pre></body></html>'
            match_json = (match_source.split(remove_from_start))[1].split(remove_from_end)[0]
            match_json = json.loads(match_json)
            file_name = 'matches/round {} opponent {}.json'.format(round_number, opponent_id)
            print(file_name)
            with open(file_name, 'w') as outfile:
                json.dump(match_json, outfile, indent=2)


def get_fixture_data_from_results():
    path = "matches/"
    match_file_list = os.scandir(path)
    current_round = 0
    headings = [
        'Round',
        'Game Number',
        'Team One ID',
        'Team One Team Name',
        'Team One Points',
        'Team One Final',
        'Team Two ID',
        'Team Two Team Name',
        'Team Two Points',
        'Team Two Final'
    ]
    heading_text = ""
    counter = 0
    for heading in headings:
        counter = counter + 1
        if counter < len(headings):
            heading_text = heading_text + heading + "|"
        else:
            heading_text = heading_text + heading
    print(heading_text)
    for file in match_file_list:
        with open(file, 'r') as f:
            match_json = json.load(f)
            fixture = match_json['schedule']['games']
            round = match_json['round']
            if current_round != round:
                for game in fixture:
                    game_number = game['game_num']
                    team_one_team_id = game['team_1']['team_id']
                    team_one_team_name = game['team_1']['team_name']
                    team_one_points = game['team_1']['points']
                    team_one_final = game['team_1']['final']
                    team_two_team_id = game['team_2']['team_id']
                    team_two_team_name = game['team_2']['team_name']
                    team_two_points = game['team_2']['points']
                    team_two_final = game['team_2']['final']

                    line = (
                        str(round) + "|" +
                        str(game_number) + "|" +
                        str(team_one_team_id) + "|" +
                        str(team_one_team_name) + "|" +
                        str(team_one_points) + "|" +
                        str(team_one_final) + "|" +
                        str(team_two_team_id) + "|" +
                        str(team_two_team_name) + "|" +
                        str(team_two_final) + "|" +
                        str(team_two_points)
                    )
                    print(line)
            current_round = round


def get_match_name(round_number, team_id):
    fixture_df = pd.read_csv('inputs/2019_sc_fixture.csv')
    team_one = fixture_df[(fixture_df['Round'] == round_number) & (fixture_df['Team One ID'] == team_id)]
    team_two = fixture_df[(fixture_df['Round'] == round_number) & (fixture_df['Team Two ID'] == team_id)]
    if len(team_one) > 0:
        team_one_team_name = team_one.iloc[0]['Team One Team Name']
        team_two_team_name = team_one.iloc[0]['Team Two Team Name']
        return '{} vs {}'.format(team_one_team_name, team_two_team_name)
    elif len(team_two) > 0:
        team_one_team_name = team_two.iloc[0]['Team One Team Name']
        team_two_team_name = team_two.iloc[0]['Team Two Team Name']
        return '{} vs {}'.format(team_one_team_name, team_two_team_name)
    else:
        print("No matching round and team ID for round {} and team {}".format(round_number, team_id))


def get_player_info(round_number, team_id, team_name, players, on_field):
    df = json_normalize(players)
    df['Round'] = round_number
    match_name = get_match_name(round_number, team_id)
    df['Match Name'] = match_name
    df['Team ID'] = team_id
    df['Team Name'] = team_name
    df['Full Name'] = df['fn'] + ' ' + df['ln']
    df['On Field?'] = on_field
    return df


def get_match_data():
    path = "inputs/matches/"
    match_file_list = os.scandir(path)
    current_round = 0
    columns = [
        'Round',
        'Match Name',
        'Team ID',
        'Team Name',
        'id',
        'Full Name',
        'pos',
        'team',
        'team_opponent',
        'pts',
        'On Field?'
    ]
    all_matches_list = []

    for file in match_file_list:
        with open(file, 'r') as f:
            match_json = json.load(f)
            round_number = match_json['round']
            # MY TEAM
            if current_round != round_number:
                team_id = int(match_json['team']['id'])
                team_name = match_json['team']['name']
                my_on_field_players = match_json['team']['player_list']['field']['players']
                my_on_field_df = get_player_info(round_number, team_id, team_name, my_on_field_players, True)
                my_off_field_players = match_json['team']['player_list']['bench']['players']
                my_off_field_df = get_player_info(round_number, team_id, team_name, my_off_field_players, False)
                full_match_df = pd.concat([my_on_field_df, my_off_field_df])
                print(full_match_df[columns])
                all_matches_list.append(full_match_df)

            current_round = round_number
            # OTHER TEAMS
            team_id = int(match_json['opponent']['id'])
            team_name = match_json['opponent']['name']
            other_on_field_players = match_json['opponent']['player_list']['field']['players']
            other_on_field_df = get_player_info(round_number, team_id, team_name, other_on_field_players, True)
            other_off_field_players = match_json['opponent']['player_list']['bench']['players']
            other_off_field_df = get_player_info(round_number, team_id, team_name, other_off_field_players, False)
            full_match_df = pd.concat([other_on_field_df, other_off_field_df])
            all_matches_list.append(full_match_df)

    all_matches = pd.concat(all_matches_list)
    timestr = time.strftime("%Y%m%d-%H%M%S")
    all_matches.to_csv('outputs/all_matches_{}.csv'.format(timestr), columns=columns)
    # all_matches.to_csv(r'outputs/all_matches_detailed.csv')


def get_weekly_ladder():
    path = "inputs/matches/"
    match_file_list = os.scandir(path)
    current_round = 0
    all_weekly_ladder_list = []

    for file in match_file_list:
        with open(file, 'r') as f:
            match_json = json.load(f)
            round_number = match_json['round']
            if current_round != round_number:
                df_weekly_ladder_line = json_normalize(match_json['team']['league'])
                df_weekly_ladder_line['Team ID'] = int(match_json['team']['id'])
                df_weekly_ladder_line['Team Name'] = match_json['team']['name']
                df_weekly_ladder_line['Round'] = round_number
                all_weekly_ladder_list.append(df_weekly_ladder_line)
                print(df_weekly_ladder_line)
            current_round = round_number
            df_weekly_ladder_line = json_normalize(match_json['opponent']['league'])
            df_weekly_ladder_line['Team ID'] = int(match_json['opponent']['id'])
            df_weekly_ladder_line['Team Name'] = match_json['opponent']['name']
            df_weekly_ladder_line['Round'] = round_number
            all_weekly_ladder_list.append(df_weekly_ladder_line)
            print(df_weekly_ladder_line)

    df_combined_weekly_ladders = pd.concat(all_weekly_ladder_list, sort=False)
    # df_combined_weekly_ladders = df_combined_weekly_ladders.sort_values()
    timestr = time.strftime("%Y%m%d-%H%M%S")
    df_combined_weekly_ladders.to_csv('outputs/weekly_ladder_{}.csv'.format(timestr))


get_weekly_ladder()
