# -*- coding: utf-8 -*-

from flask import Flask
import dash

import sys
import os
import json
import pandas as pd

import AirtableAPI as airtable
from flask_caching import Cache


local_version = False

if local_version:

    json_file = "../config/airtable.json"
    this_dir = os.path.dirname(__file__)
    config_filename = os.path.join(this_dir, json_file)
    config_file = open(config_filename)
    at_config = json.load(config_file)
    config_file.close()
    app = dash.Dash('Tav Dash')
    app.config.suppress_callback_exceptions = True
else:
    server = Flask('Tav Dash')
    server.secret_key = os.environ.get('secret_key', 'secret')
    at_config={}
    app = dash.Dash('Tav Dash', server=server)
    app.config.suppress_callback_exceptions = True   
    at_config["base_id"]=os.environ["base_id"]
    at_config["api_key"]=os.environ["airtable_api_key"]


cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})
timeout = 360


@cache.memoize(timeout=timeout)
def getBattingDataframe():
    at = airtable.TavsAirTable(at_config)
    data = at.getAllAirtableRecordsFromTableView(at.batting_table,
                                                 at.batting_table.tavs_innings_view)

    columns = at.batting_table.Record().fields.keys()
    data_list = [[record.fields[x].value for x in columns] for record in data]
    df = pd.DataFrame(data_list, columns=columns)

    return df

@cache.memoize(timeout=timeout)
def getBowlingDataframe():
    at = airtable.TavsAirTable(at_config)
    data = at.getAllAirtableRecordsFromTableView(at.bowling_table,
                                                 at.bowling_table.tavs_innings_view)

    columns = at.bowling_table.Record().fields.keys()
    data_list = [[record.fields[x].value for x in columns] for record in data]
    df = pd.DataFrame(data_list, columns=columns)

    return df

@cache.memoize(timeout=timeout)
def getMatchesDataframe():
    at = airtable.TavsAirTable(at_config)
    data = at.getAllAirtableRecordsFromTableView(at.matches_table,
                                                 at.matches_table.tavs_matches_view)

    columns = at.matches_table.Record().fields.keys()
    data_list = [[record.fields[x].value for x in columns] for record in data]
    df = pd.DataFrame(data_list, columns=columns)

    return df



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


