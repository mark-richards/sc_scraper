import requests
from bs4 import BeautifulSoup
import json
from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session
import getpass
import time


def get_sc_token():
    # Credentials to generate token
    client_id = "Lf7m0371XCbMBlQ0fAFoGRJlfCs2JZpYvLU1uEvd"
    client_secret = ''
    get_token_url = 'https://supercoach.heraldsun.com.au/2019/api/afl/classic/v1/access_token'

    # Supercoach credentials
    sc_user = 'richards_0123@hotmail.com'
    sc_pass = getpass.getpass()


    # Create Token
    oauth = OAuth2Session(client=LegacyApplicationClient(client_id=client_id))
    token = oauth.fetch_token(
        token_url=get_token_url,
        username=sc_user,
        password=sc_pass,
        client_id=client_id,
        client_secret=client_secret)

    # Get token value from the Access Token Key
    sc_token = token["access_token"]
    return sc_token


def download_all_player_stats():
    # Get a token
    sc_token = get_sc_token()
    # Append token to the end of the State Centre URL
    sc_url = "https://supercoach.heraldsun.com.au/afl/draft/statscentre?access_token=" + sc_token
    # Create text file to store AFL stats
    timestr = time.strftime("%Y%m%d-%H%M%S")
    file_output = open("outputs/all_player_stats_{}.txt".format(timestr), "w")
    # HTTP request to stats centre URL
    res = requests.get(sc_url)
    # Parse the response as HTML using the BeautifulSoup Library
    soup = BeautifulSoup(res.text, 'html.parser')
    # Find the start and end position of the data which is stored in the researchGridData variable
    start_id = "var researchGridData = "
    end_id = "}]"
    stat_start = str(soup).find(start_id) + len(start_id)
    soup_len = len(str(soup))
    stat_end = str(soup)[stat_start:soup_len].find(end_id) + len(end_id) + stat_start
    # Format it to JSON
    raw_stats = str("{\n\"researchGridData\": " + str(soup)[stat_start:stat_end] + "}").encode('utf8')
    # Parse to JSON to make extracting key values much easier
    json_stats = json.loads(raw_stats)
    # Write to file
    # Starting with the heading
    headings = [
        'Player ID',
        'First Name',
        'Last Name',
        'Pos1',
        'Pos2',
        'Team',
        'Playing Next',
        'In 2 Rds',
        'In 3 Rds',
        'Playing Next',
        'Owner',
        'Waiver',
        'Free Agent',
        'Trade Status',
        'Total Pts',
        'Rds',
        'Rd Pts',
        'Avg',
        'Avg 3',
        'Avg 5',
        'Status Comment',
        'Player Note'
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
    file_output.write(heading_text + "\n")
    # Then write each player to file
    for each in json_stats['researchGridData']:
        player_note = each.get('player_note', "N/A")
        status_comment = each.get('status_comment', "N/A")
        opp1 = each.get('opp1', "N/A")
        opp2 = each.get('opp2', "N/A")
        opp3 = each.get('opp3', "N/A")
        line = (
            str(each['id']) + '|' +
            str(each['fn']) + '|' +
            str(each['ln']) + '|' +
            str(each['pos']) + '|' +
            str(each['pos2']) + '|' +
            str(each['team']) + '|' +
            str(opp1) + '|' +
            str(opp2) + '|' +
            str(opp3) + '|' +
            str(each['owner']) + '|' +
            str(each['waiver']) + '|' +
            str(each['free_agent']) + '|' +
            str(each['trade_status']) + '|' +
            str(each['tpts']) + '|' +
            str(each['rds']) + '|' +
            str(each['pts']) + '|' +
            str(each['avg']) + '|' +
            str(each['avg3']) + '|' +
            str(each['avg5']) + '|' +
            str(status_comment) + '|' +
            str(player_note) + '\n'
        )
        print(line)
        file_output.write(line)
    file_output.close()


download_all_player_stats()
