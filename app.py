# -*- coding: utf-8 -*-

from flask import Flask
import dash

import sys
import os
import json

import AirtableAPI as airtable
import functools32


local_version = False

if local_version:

    json_file = "../config/airtable.json"
    this_dir = os.path.dirname(__file__)
    config_filename = os.path.join(this_dir, json_file)
    config_file = open(config_filename)
    at_config = json.load(config_file)
    config_file.close()
    app = dash.Dash('Tav Dash')
    app.config.supress_callback_exceptions = True
else:
    server = Flask('Tav Dash')
    server.secret_key = os.environ.get('secret_key', 'secret')
    at_config={}
    app = dash.Dash('Tav Dash', server=server)
    app.config.supress_callback_exceptions = True   
    at_config["base_id"]=os.environ["base_id"]
    at_config["api_key"]=os.environ["airtable_api_key"]


@functools32.lru_cache(maxsize=32)
def getBattingDataframe():
    #print at_config
    batting_airtable = airtable.AirTable(at_config)

    df = batting_airtable.getAllBattingDataFromBattingTable()
    return df

@functools32.lru_cache(maxsize=32)
def getBowlingDataframe():
    #print at_config
    bowling_airtable = airtable.AirTable(at_config)

    df = bowling_airtable.getAllBowlingDataFromBowlingTable()
    return df

@functools32.lru_cache(maxsize=32)
def getMatchesDataframe():
    #print at_config
    matches_airtable = airtable.AirTable(at_config)

    df = matches_airtable.getAllMatchDataFromMatchesTable()
    return df

print "FUCK THIS SHIT"


app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Taverages</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''


