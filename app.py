# -*- coding: utf-8 -*-
from flask import Flask
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import pandas as pd
import plotly.graph_objs as go

import AirtableAPI as airtable

import sys
import os
import json
import time

import functools32
import collections


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




seasons = ['2018','2019','All']
match_types = ['Full Length', '20 Overs','All']
disciplines = ['Batting', 'Bowling']
inter_tav_types = ["Railway Taverners CC","Inter Tavs","All"]

def getMasthead():

	return html.Div([
		html.Div(
			dcc.Dropdown(id='discipline-selection', 
						options=[{'label': i, 'value': i} for i in disciplines],
						value='Batting',
						placeholder='Choose Discipline...'),
			className='masthead__column_1',
			id='discipline-selection-div'
		),
		html.Div(
			dcc.Dropdown(
				id='season-selection',
				options=[{'label': i, 'value': i} for i in seasons],
				value='2019',
				placeholder='Choose Season...'
			),
			className='masthead__column_2',
			id='season-selection-div'
		),
		html.Div(
			dcc.Dropdown(
				id='match-type-selection',
				options=[{'label': i, 'value': i} for i in match_types],
				value='Full Length',
				clearable=False
			),
			className='masthead__column_3',
			id='match-type-selection-div'
		),
		html.Div(
			dcc.Dropdown(
				id='inter-tav-selection',
				options=[{'label': i, 'value': i} for i in inter_tav_types],
				value='Railway Taverners CC',
				clearable=False,
				placeholder='Choose Match Type...'
			),
			className='masthead__column_4',
			id='inter-tav-selection-div'
		),
		html.Div([
			dt.DataTable(
				id='player-table',
				columns=[
			        {"name": "Name", "id": "name"},
			        {"name": "Innings", "id": "innings"},
			        {"name": "Runs", "id": "bat_runs"},
			        {"name": "Average", "id": "bat_average"},
			        {"name": "HS", "id": "top_score"},
			        {"name": "Fours", "id": "fours"},
			        {"name": "Sixes", "id": "sixes"},
			        {"name": "Strike Rate", "id": "bat_strike_rate"},
			        {"name": "Overs", "id": "overs","hidden":True},
			        {"name": "Wickets", "id": "wickets","hidden":True},
			        {"name": "Runs", "id": "bowl_runs","hidden":True},
			        {"name": "Average", "id": "bowl_average","hidden":True},
			        {"name": "Economy Rate", "id": "economy_rate","hidden":True},
			        {"name": "Strike Rate", "id": "bowl_strike_rate","hidden":True},
			        {"name": "Catches", "id": "catches"},			        
			    ],
			    style_cell_conditional=[
					{'if': {'column_id': 'name'},
					 'width': '20%'},
					{'if': {'column_id': 'innings'},
					 'width': '10%'},
					{'if': {'column_id': 'bat_runs'},
					 'width': '10%'},
					{'if': {'column_id': 'bat_average'},
					 'width': '10%'},
					{'if': {'column_id': 'top_score'},
					 'width': '10%'},
					{'if': {'column_id': 'fours'},
					 'width': '10%'},
					{'if': {'column_id': 'sixes'},
					 'width': '10%'},
					{'if': {'column_id': 'bat_strike_rate'},
					 'width': '10%'},
					{'if': {'column_id': 'overs'},
					 'width': '12%'},
					{'if': {'column_id': 'wickets'},
					 'width': '12%'},
					{'if': {'column_id': 'bowl_runs'},
					 'width': '12%'},
					{'if': {'column_id': 'bowl_average'},
					 'width': '12%'},
					{'if': {'column_id': 'economy_rate'},
					 'width': '12%'},
					{'if': {'column_id': 'bowl_strike_rate'},
					 'width': '12%'},
					{'if': {'column_id': 'catches'},
					 'width': '7%'},
				],
				style_header={
			        'fontWeight': 'bold',
				    'font-family':'sans-serif',
				    'fontSize':15,
				    'background': 'rgb(242, 242, 242)'
			    },
			    style_table={
				    'maxHeight': 345,
				    'overflowY': 'auto',
				},
				style_cell={
				    'textAlign': 'center',
				    'font-family':'sans-serif',
				    'fontSize':20
				},
				editable=False,
				n_fixed_rows=1,
				sorting=True,
				sorting_type="single",
				row_selectable="single",
				selected_rows=[0],
				style_as_list_view=True				
			)
		],id='player-table-div',
			className='tavs__player-table')
	], className='masthead l-grid')

app.layout = html.Div([
		dcc.Location(id='url', refresh=False),
		html.Div([
					getMasthead(),
					html.Div(id='batting-stats-div',className='tavs__batting-stats'),
					html.Div(id='timeline-graph',className='tavs__batting-graph'),
					html.Div(id='mod-graph',className='tavs__batting-mod-graph'),

		], className='l-subgrid'),
		html.Div([
					html.Div(id='bowling-stats-div',className='tavs__bowling-stats'),
					html.Div(id='bowling-timeline-graph',className='tavs__bowling-graph'),
					html.Div(id='bowling-mod-graph',className='tavs__bowling-mod-graph')
		], className='bowling-grid l-subgrid')
	], className='l-grid')

'''*********************************************************************************************************8
	GET DATA
*****************************************************************************************************************'''


def getBattingDataTable(season,
						match_type,
						inter_tav_type):

	df_batting = getBattingDataframe()	
	df_bowling = getBowlingDataframe()
	df_catching = df_batting[df_batting['catcher'] != ""]

	df_tavs = df_batting[df_batting['team'] == "Railway Taverners CC"]
	df_pres = df_batting[df_batting['team'] == "President's XI"]
	df_moors = df_batting[df_batting['team'] == "Andy James Invitational XI"]
	df_tavs_xi = df_batting[df_batting['team'] == "Railway Taverners XI"]
	if inter_tav_type == "All":
		df_batting = pd.concat([df_tavs, df_pres, df_moors, df_tavs_xi]) 
	elif inter_tav_type == "Inter Tavs":
		df_batting = pd.concat([df_pres, df_moors, df_tavs_xi])
		df_catching1 = df_catching[df_catching['match'] == "President's XI"]
		df_catching2 = df_catching[df_catching['match'] == "Andy James Invitational XI"]
		df_catching = pd.concat([df_catching1, df_catching2]) 
	else:
		df_batting = df_tavs
		df_catching = df_catching[df_catching['match'] != "President's XI"]
		df_catching = df_catching[df_catching['match'] != "Andy James Invitational XI"]	

	if season:
		if season != "All":
			df_batting = df_batting[df_batting['season'] == season]
			df_bowling = df_bowling[df_bowling['season'] == season]
			df_catching = df_catching[df_catching['season'] == season]
	if df_batting.empty: return []

	if match_type:
		if match_type != "All":
			if match_type == "20 Overs":
				df_batting = df_batting[df_batting['match_type'] == match_type]
				df_bowling = df_bowling[df_bowling['match_type'] == match_type]
				df_catching = df_catching[df_catching['match_type'] == match_type]
			else:
				df_batting = df_batting[df_batting['match_type'] != "20 Overs"]
				df_bowling = df_bowling[df_bowling['match_type'] != "20 Overs"]
				df_catching = df_catching[df_catching['match_type'] != "20 Overs"]
	if df_batting.empty: return []

	data = []

	for player in df_batting['name'].unique():
		#print player
		df_player = df_batting[df_batting['name'] == player]
		innings = df_player['innings_bool'].sum()
		runs = df_player['runs'].sum()
		top_score = df_player['runs'].max()
		outs = df_player['out_bool'].sum()
		
		if outs:
			average = round(float(runs)/float(outs),2)
		else:
			average = None
		sixes = df_player['sixes'].sum()
		fours = df_player['fours'].sum()
		balls_faced = df_player['balls_faced'].sum()
		if balls_faced:
			strike_rate = round(100.0*float(runs)/float(balls_faced),2)
		else:
			strike_rate = 0.0
		if season!="2019":
			strike_rate = "-"

		df_player = df_bowling[df_bowling['name'] == player]
		overs = df_player['overs'].sum()
		if overs:
			bowl_runs = df_player['runs'].sum()
			wickets = df_player['wickets'].sum()

			economy = round(float(bowl_runs)/float(overs),2)
			
			if wickets:
				bowl_average = round(float(bowl_runs)/float(wickets),2)
				bowl_strike_rate = round(6.0*float(overs)/float(wickets),2)
			else:
				bowl_average = None
				bowl_strike_rate = None
		else:
			bowl_runs = None
			wickets = None
			economy = None
			bowl_average = None
			bowl_strike_rate = None

		catches = len(df_catching[df_catching['catcher'] == player].index)
	 
		#print average
		data.append([player,
					 innings,
					 runs,
					 average,
					 top_score,
					 fours,
					 sixes,
					 strike_rate,
					 overs,
					 bowl_runs,
					wickets,
					economy,
					bowl_average,
					bowl_strike_rate,
					catches])

	#print data
	df_data = pd.DataFrame(data,columns=["name",
									  "innings",
									  "bat_runs",
									  "bat_average",
									  "top_score",
									  "fours",
									  "sixes",
									  "bat_strike_rate",
									  "overs",
									 "bowl_runs",
									"wickets",
									"economy_rate",
									"bowl_average",
									"bowl_strike_rate",
									"catches"])
	df_data = df_data.sort_values('innings',ascending=0)

	data_dict = df_data.to_dict('records')

	return data_dict


@app.callback(
	Output('player-table', 'columns'),
	[Input('discipline-selection', 'value')
])
def playerTableColumns(discipline):
	if discipline == "Batting":
		return [
			        {"name": "Name", "id": "name"},
			        {"name": "Innings", "id": "innings"},
			        {"name": "Runs", "id": "bat_runs"},
			        {"name": "Average", "id": "bat_average"},
			        {"name": "HS", "id": "top_score"},
			        {"name": "Fours", "id": "fours"},
			        {"name": "Sixes", "id": "sixes"},
			        {"name": "Strike Rate", "id": "bat_strike_rate"},
			        {"name": "Overs", "id": "overs","hidden":True},
			        {"name": "Wickets", "id": "wickets","hidden":True},
			        {"name": "Runs", "id": "bowl_runs","hidden":True},
			        {"name": "Average", "id": "bowl_average","hidden":True},
			        {"name": "Economy Rate", "id": "economy_rate","hidden":True},
			        {"name": "Strike Rate", "id": "bowl_strike_rate","hidden":True},
			        {"name": "Catches", "id": "catches"},			        			        
			    ]
	if discipline == "Bowling":
		return [
			        {"name": "Name", "id": "name"},
			        {"name": "Innings", "id": "innings","hidden":True},
			        {"name": "Runs", "id": "bat_runs","hidden":True},
			        {"name": "Average", "id": "bat_average","hidden":True},
			        {"name": "HS", "id": "top_score","hidden":True},
			        {"name": "Fours", "id": "fours","hidden":True},
			        {"name": "Sixes", "id": "sixes","hidden":True},
			        {"name": "Strike Rate", "id": "bat_strike_rate","hidden":True},
			        {"name": "Overs", "id": "overs"},
			        {"name": "Wickets", "id": "wickets"},
			        {"name": "Runs", "id": "bowl_runs"},
			        {"name": "Average", "id": "bowl_average"},
			        {"name": "Economy Rate", "id": "economy_rate"},
			        {"name": "Strike Rate", "id": "bowl_strike_rate"},		
			        {"name": "Catches", "id": "catches"},			        	        
			    ]
	return [
			        {"name": "Name", "id": "name"},
			        {"name": "Innings", "id": "innings","hidden":True},
			        {"name": "Runs", "id": "bat_runs","hidden":True},
			        {"name": "Average", "id": "bat_average","hidden":True},
			        {"name": "HS", "id": "top_score","hidden":True},
			        {"name": "Fours", "id": "fours","hidden":True},
			        {"name": "Sixes", "id": "sixes","hidden":True},
			        {"name": "Strike Rate", "id": "bat_strike_rate","hidden":True},
			        {"name": "Overs", "id": "overs","hidden":True},
			        {"name": "Wickets", "id": "wickets","hidden":True},
			        {"name": "Runs", "id": "bowl_runs","hidden":True},
			        {"name": "Average", "id": "bowl_average","hidden":True},
			        {"name": "Economy Rate", "id": "economy_rate","hidden":True},
			        {"name": "Strike Rate", "id": "bowl_strike_rate","hidden":True}
			]

@app.callback(
	Output('player-table', 'sorting_settings'),
	[Input('discipline-selection', 'value')
])
def playerTableColumnDirection(discipline):
	if discipline == "Batting":
		return [{'column_id':'bat_runs','direction':'desc'}]
	if discipline == "Bowling":
		return [{'column_id':'wickets','direction':'desc'}]
	return None 

	
@app.callback(
	Output('player-table', 'data'),
	[Input('season-selection', 'value'),
	Input('match-type-selection', 'value'),
	Input('discipline-selection', 'value'),
	Input('inter-tav-selection', 'value')
])
def playerTableRender(season,
						 match_type,
						 discipline,
						 inter_tav_type):
	return getBattingDataTable(season, match_type,inter_tav_type)
	

@app.callback(
	Output('batting-stats-div', 'children'),
	[Input('player-table', "derived_virtual_data"),
     Input('player-table', "derived_virtual_selected_rows"),
	Input('season-selection', 'value'),
	Input('match-type-selection', 'value'),
	Input('discipline-selection', 'value'),
	Input('inter-tav-selection', 'value')])
def populateBattingStats(table_data,
						 player,
						 season,
						 match_type,
						 discipline,
						 inter_tav_type):
	if discipline != "Batting": return None
	if not player: return None
	df_batting = pd.DataFrame(table_data)#getBattingDataframe()
	player_name = df_batting.iloc[player[0]]["name"]#df_batting[df_batting['name'] == player]
	df_batting = getBattingDataframe()
	df_tavs = df_batting[df_batting['team'] == "Railway Taverners CC"]
	df_pres = df_batting[df_batting['team'] == "President's XI"]
	df_moors = df_batting[df_batting['team'] == "Andy James Invitational XI"]
	df_tavs_xi = df_batting[df_batting['team'] == "Railway Taverners XI"]
	if inter_tav_type == "All":
		df_batting = pd.concat([df_tavs, df_pres, df_moors, df_tavs_xi]) 
	elif inter_tav_type == "Inter Tavs":
		df_batting = pd.concat([df_pres, df_moors, df_tavs_xi]) 
	else:
		df_batting = df_tavs

	if df_batting.empty: return None
	df_player = df_batting[df_batting['name'] == player_name]

	if season:
		if season != "All":
			df_player = df_player[df_player['season'] == season]

	if match_type:
		if match_type != "All":
			if match_type == "20 Overs":
				df_player = df_player[df_player['match_type'] == match_type]
			else:
				df_player = df_player[df_player['match_type'] != "20 Overs"]

	if df_player.empty: return None

	innings = df_player['innings_bool'].sum()
	runs = df_player['runs'].sum()
	top_score = df_player['runs'].max()
	outs = df_player['out_bool'].sum()
	sixes = df_player['sixes'].sum()
	fours = df_player['fours'].sum()
	balls_faced = df_player['balls_faced'].sum()
	strike_rate = 100.0*float(runs)/float(balls_faced)
	if season!="2019":
		strike_rate_md = dcc.Markdown("Strike Rate: -")
	else:
		strike_rate_md = dcc.Markdown("Strike Rate: " + "{:.2f}".format(strike_rate))

	if outs:
		average = float(runs)/float(outs)
	else:
		average = 0.0

	df_ts = df_player[df_player['runs'] == top_score]
	try:
		if df_ts['out_bool'].values[0]:
			top_score_md = dcc.Markdown("Highest Score: " + "{:,}".format(int(top_score)))
		else:
			top_score_md = dcc.Markdown("Highest Score: " + "{:,}".format(int(top_score)) + "*")
	except IndexError:
		top_score_md = dcc.Markdown("Highest Score: ")

	try:
		return html.Div([
						html.Div(
							[
								#html.Img(src=df_player['photo_url'].values.tolist()[0], className='tavs-unit__media'),
								html.H2(player_name + ' Batting', className='tavs-stat-title'),
								html.Div([
									dcc.Markdown("No. Innings: " + "{:,}".format(int(innings))),
									dcc.Markdown("Total Runs: " + "{:,}".format(int(runs))),
									dcc.Markdown("Average: " + "{:.2f}".format(average)),
									top_score_md,
									dcc.Markdown("Total Fours: " + "{:,}".format(int(fours))),
									dcc.Markdown("Total Sixes: " + "{:,}".format(int(sixes))),
									strike_rate_md,
								], className='tavs-unit__extra-content'),
							],
							className='tavs-unit',
						),
					], className='tavs-grid__unit tavs-grid__unit--half')
	except (IndexError, ValueError):
		return None

def getBarChart(words,
				 weights,
				 bg_colour=False):
	words.reverse()
	weights.reverse()
	data = [go.Bar(
			    y=words,
			    x=weights,
			    text=words,
			    orientation = 'h',
			    marker = dict(
			        color = 'rgba(6,193,95, 1.0)',
			        line = dict(
			            color = 'rgba(6,193,95, 1.0)',
			            width = 1)
			    )
			)]
	if bg_colour:
		layout = go.Layout(title='Methods of Dismissal',
							yaxis=dict(visible=False),
							showlegend=False,
							margin=dict(t=50),
							height=400,
							autosize=True,
			                paper_bgcolor='rgba(0,0,0,0)',
	        				plot_bgcolor='rgba(0,0,0,0)')
	else:
		layout = go.Layout(title='Methods of Dismissal',
							yaxis=dict(visible=False),
							showlegend=False,
							margin=dict(t=50),
							height=400,
							autosize=True)
	annotations = []
	for i in range(0, len(words)):
		annotations.append(dict(x=0, y=i, text=words[i],
		                              font=dict(family='Arial', size=14,
		                              color='rgba(0, 0, 0, 0.8)'),
		                              showarrow=False,
		                              xanchor='left'))
		layout['annotations'] = annotations
	figure = {	'data': data,
				'layout': layout }
	return figure

@app.callback(
	Output('mod-graph', 'children'),
	[Input('player-table', "derived_virtual_data"),
     Input('player-table', "derived_virtual_selected_rows"),
	Input('season-selection', 'value'),
	Input('match-type-selection', 'value'),
	Input('discipline-selection', 'value'),
	Input('inter-tav-selection', 'value')])
def updateDismissalMethods(table_data,
						 player,
						 season,
						 match_type,
						 discipline,
						 inter_tav_type):
	if discipline != "Batting": return None
	if not player: return None
	df_batting = pd.DataFrame(table_data)#getBattingDataframe()
	player_name = df_batting.iloc[player[0]]["name"]#df_batting[df_batting['name'] == player]
	df_batting = getBattingDataframe()

	df_tavs = df_batting[df_batting['team'] == "Railway Taverners CC"]
	df_pres = df_batting[df_batting['team'] == "President's XI"]
	df_moors = df_batting[df_batting['team'] == "Andy James Invitational XI"]
	df_tavs_xi = df_batting[df_batting['team'] == "Railway Taverners XI"]
	if inter_tav_type == "All":
		df_batting = pd.concat([df_tavs, df_pres, df_moors, df_tavs_xi]) 
	elif inter_tav_type == "Inter Tavs":
		df_batting = pd.concat([df_pres, df_moors, df_tavs_xi]) 
	else:
		df_batting = df_tavs

	if df_batting.empty: return None
	df_player = df_batting[df_batting['name'] == player_name]

	if season:
		if season != "All":
			df_player = df_player[df_player['season'] == season]

	if match_type:
		if match_type != "All":
			if match_type == "20 Overs":
				df_player = df_player[df_player['match_type'] == match_type]
			else:
				df_player = df_player[df_player['match_type'] != "20 Overs"]

	if df_player.empty: return None

	counter=collections.Counter(df_player['dismissal'].tolist())
	most_common = counter.most_common(6)

	mods = []
	weights = []
	for mod in most_common:
		mods.append(mod[0])
		weights.append(mod[1])	
	return dcc.Graph(figure=getBarChart(mods,weights,bg_colour=True),
		             config={'displayModeBar': False},
		             id='bat-m-graph')



def updateBattingInningsGraph(df_player):
	df = df_player.dropna(subset = ['runs'])

	df_out = df[df['out_bool']==True]
	df_not_out = df[df['out_bool']==False]
	
	data = []
	if not df_out.empty:
		data.append(go.Bar( x=df_out["date"],
					    y=df_out['runs'],
					    marker=dict(
					        color='rgb(240,21,22)',
					    ),
					    opacity=1.0,
					    text=df_out['match'],
					    width=50000000,
					    name='Out'
					))

	if not df_not_out.empty:
		data.append(go.Bar( x=df_not_out["date"],
					    y=df_not_out['runs'],
					    marker=dict(
					        color='rgb(22,96,185)',
					    ),
					    opacity=1.0,
					    text=df_not_out['match'],
					    width=50000000,
					    name='Not Out'
					))

	figure = {
			'data': data,
			'layout': go.Layout(
			                legend=dict(orientation="h",
		                                x=0,
		                                y=1.1),
			                font=dict(family='Arial', size=15, color='#000000'),
			                hovermode='closest',
			                margin=dict(t=50),
			                xaxis=dict(
			                        tickfont=dict(
			                                family='Arial',
			                                size=14,
			                                color='#000000'
			                            ),
			                ),
			                yaxis=dict(
			                        #range=y_axis_range,
			                        tickfont=dict(
			                                family='Arial',
			                                size=14,
			                                color='#000000'
			                            ),
			                ),
			                height=400,
			                autosize=True
			          )
			}
	return figure


@app.callback(
	Output('timeline-graph', 'children'),
	[Input('player-table', "derived_virtual_data"),
     Input('player-table', "derived_virtual_selected_rows"),
	Input('season-selection', 'value'),
	Input('match-type-selection', 'value'),
	Input('discipline-selection', 'value'),
	Input('inter-tav-selection', 'value')])
def updateBattingInningsTimeline(table_data,
								 player,
								 season,
								 match_type,
								 discipline,
								 inter_tav_type):
	if discipline != "Batting": return None
	if not player: return None
	df_batting = pd.DataFrame(table_data)#getBattingDataframe()
	player_name = df_batting.iloc[player[0]]["name"]#df_batting[df_batting['name'] == player]
	df_batting = getBattingDataframe()

	df_tavs = df_batting[df_batting['team'] == "Railway Taverners CC"]
	df_pres = df_batting[df_batting['team'] == "President's XI"]
	df_moors = df_batting[df_batting['team'] == "Andy James Invitational XI"]
	df_tavs_xi = df_batting[df_batting['team'] == "Railway Taverners XI"]
	if inter_tav_type == "All":
		df_batting = pd.concat([df_tavs, df_pres, df_moors, df_tavs_xi]) 
	elif inter_tav_type == "Inter Tavs":
		df_batting = pd.concat([df_pres, df_moors, df_tavs_xi]) 
	else:
		df_batting = df_tavs

	if df_batting.empty: return None
	df_player = df_batting[df_batting['name'] == player_name]

	if season:
		if season != "All":
			df_player = df_player[df_player['season'] == season]

	if match_type:
		if match_type != "All":
			if match_type == "20 Overs":
				df_player = df_player[df_player['match_type'] == match_type]
			else:
				df_player = df_player[df_player['match_type'] != "20 Overs"]

	if df_player.empty: return None

	return dcc.Graph(figure=updateBattingInningsGraph(df_player),
		             config={'displayModeBar': False},
		             id='bat-t-graph')




@app.callback(
	Output('bowling-stats-div', 'children'),
	[Input('player-table', "derived_virtual_data"),
     Input('player-table', "derived_virtual_selected_rows"),
	Input('season-selection', 'value'),
	Input('match-type-selection', 'value'),
	Input('discipline-selection', 'value'),
	Input('inter-tav-selection', 'value')])
def populateBowlingStats(table_data,
						 player,
						 season,
						 match_type,
						 discipline,
						 inter_tav_type):
	if discipline != "Bowling": return None
	if not player: return None
	df_bowling = pd.DataFrame(table_data)#getBattingDataframe()
	player_name = df_bowling.iloc[player[0]]["name"]#df_batting[df_batting['name'] == player]

	df_bowling = getBowlingDataframe()

	df_tavs = df_bowling[df_bowling['team'] == "Railway Taverners CC"]
	df_pres = df_bowling[df_bowling['team'] == "President's XI"]
	df_moors = df_bowling[df_bowling['team'] == "Andy James Invitational XI"]
	df_tavs_xi = df_bowling[df_bowling['team'] == "Railway Taverners XI"]
	if inter_tav_type == "All":
		df_bowling = pd.concat([df_tavs, df_pres, df_moors, df_tavs_xi]) 
	elif inter_tav_type == "Inter Tavs":
		df_bowling = pd.concat([df_pres, df_moors, df_tavs_xi]) 
	else:
		df_bowling = df_tavs

	df_player = df_bowling[df_bowling['name'] == player_name]
		
	if season:
		if season != "All":
			df_player = df_player[df_player['season'] == season]

	if match_type:
		if match_type != "All":
			if match_type == "20 Overs":
				df_player = df_player[df_player['match_type'] == match_type]
			else:
				df_player = df_player[df_player['match_type'] != "20 Overs"]

	if df_player.empty: return None

	
	overs = df_player['overs'].sum()
	if not overs: return None

	runs = df_player['runs'].sum()
	wickets = df_player['wickets'].sum()

	if overs:
		economy = float(runs)/float(overs)
	else:
		economy = 0.0
	
	if wickets:
		average = float(runs)/float(wickets)
		strike_rate = 6.0*float(overs)/float(wickets)
	else:
		average = 0.0
		strike_rate = 0.0

	return html.Div([
					html.Div(
						[	html.H2(player_name + ' Bowling', className='tavs-stat-title'),
							html.Div([
								dcc.Markdown("Overs: " + "{:.1f}".format(overs)),
								dcc.Markdown("Wickets: " + "{:,}".format(int(wickets))),
								dcc.Markdown("Runs: " + "{:,}".format(int(runs))),
								dcc.Markdown("Average: " + "{:.2f}".format(average)),
								dcc.Markdown("Economy Rate: " + "{:.2f}".format(economy)),
								dcc.Markdown("Strike Rate: " + "{:.2f}".format(strike_rate)),
							], className='tavs-unit__extra-content'),
						],
						className='tavs-unit',
					),
				], className='tavs-grid__unit tavs-grid__unit--half')


def updateBowlingInningsGraph(df_player):
	df = df_player.dropna(subset = ['wickets'])

	data = []

	if not df.empty:
		data.append(go.Bar( x=df["date"],
					    y=df['wickets'],
					    marker=dict(
					        color='rgb(240,21,22)',
					    ),
					    opacity=1.0,
					    text=df['match'],
					    width=50000000,
					    name='Out'
					))

	figure = {
			'data': data,
			'layout': go.Layout(
			                legend=dict(orientation="h",
		                                x=0,
		                                y=1.1),
			                 font=dict(family='Arial', size=15, color='#000000'),
			                hovermode='closest',
			                margin=dict(t=50),
			                xaxis=dict(
			                        tickfont=dict(
			                                family='Arial',
			                                size=14,
			                                color='#000000'
			                            ),
			                ),
			                yaxis=dict(
			                        #range=y_axis_range,
			                        tickfont=dict(
			                                family='Arial',
			                                size=14,
			                                color='#000000'
			                            ),
			                ),
			                height=400,
			                autosize=True,
			                paper_bgcolor='rgba(0,0,0,0)',
            				plot_bgcolor='rgba(0,0,0,0)'
			          )
			}
	return figure


@app.callback(
	Output('bowling-timeline-graph', 'children'),
	[Input('player-table', "derived_virtual_data"),
     Input('player-table', "derived_virtual_selected_rows"),
	Input('season-selection', 'value'),
	Input('match-type-selection', 'value'),
	Input('discipline-selection', 'value'),
	Input('inter-tav-selection', 'value')])
def updateBowlingInningsTimeline(table_data,
								player,
								 season,
								 match_type,
								 discipline,
								 inter_tav_type):
	if discipline != "Bowling": return None
	if not player: return None	
	df_bowling = pd.DataFrame(table_data)#getBattingDataframe()
	player_name = df_bowling.iloc[player[0]]["name"]#df_batting[df_batting['name'] == player]
	df_bowling = getBowlingDataframe()

	df_tavs = df_bowling[df_bowling['team'] == "Railway Taverners CC"]
	df_pres = df_bowling[df_bowling['team'] == "President's XI"]
	df_moors = df_bowling[df_bowling['team'] == "Andy James Invitational XI"]
	df_tavs_xi = df_bowling[df_bowling['team'] == "Railway Taverners XI"]
	if inter_tav_type == "All":
		df_bowling = pd.concat([df_tavs, df_pres, df_moors, df_tavs_xi]) 
	elif inter_tav_type == "Inter Tavs":
		df_bowling = pd.concat([df_pres, df_moors, df_tavs_xi]) 
	else:
		df_bowling = df_tavs

	df_player = df_bowling[df_bowling['name'] == player_name]

	if season:
		if season != "All":
			df_player = df_player[df_player['season'] == season]

	if match_type:
		if match_type != "All":
			if match_type == "20 Overs":
				df_player = df_player[df_player['match_type'] == match_type]
			else:
				df_player = df_player[df_player['match_type'] != "20 Overs"]

	if df_player.empty: return None

	return  dcc.Graph(figure=updateBowlingInningsGraph(df_player),
		             config={'displayModeBar': False},
		             id='bowl-t-graph')


@app.callback(
	Output('bowling-mod-graph', 'children'),
	[Input('player-table', "derived_virtual_data"),
     Input('player-table', "derived_virtual_selected_rows"),
	Input('season-selection', 'value'),
	Input('match-type-selection', 'value'),
	Input('discipline-selection', 'value'),
	Input('inter-tav-selection', 'value')])
def updateBowlingDismissalMethods(table_data,
									player,
									 season,
									 match_type,
									 discipline,
									 inter_tav_type):
	if discipline != "Bowling": return None
	if not player: return None	
	df_bowling = pd.DataFrame(table_data)#getBattingDataframe()
	player_name = df_bowling.iloc[player[0]]["name"]#df_batting[df_batting['name'] == player]
	df_bowling = getBowlingDataframe()
	
	df_tavs = df_bowling[df_bowling['team'] == "Railway Taverners CC"]
	df_pres = df_bowling[df_bowling['team'] == "President's XI"]
	df_moors = df_bowling[df_bowling['team'] == "Andy James Invitational XI"]
	df_tavs_xi = df_bowling[df_bowling['team'] == "Railway Taverners XI"]
	if inter_tav_type == "All":
		df_bowling = pd.concat([df_tavs, df_pres, df_moors, df_tavs_xi]) 
	elif inter_tav_type == "Inter Tavs":
		df_bowling = pd.concat([df_pres, df_moors, df_tavs_xi]) 
	else:
		df_bowling = df_tavs

	df_player = df_bowling[df_bowling['name'] == player_name]

	if season:
		if season != "All":
			df_player = df_player[df_player['season'] == season]

	if match_type:
		if match_type != "All":
			if match_type == "20 Overs":
				df_player = df_player[df_player['match_type'] == match_type]
			else:
				df_player = df_player[df_player['match_type'] != "20 Overs"]

	if df_player.empty: return None

	mod_list = [item for sublist in df_player['dismissal_types'].tolist() for item in sublist]
	counter=collections.Counter(mod_list)
	most_common = counter.most_common(6)

	mods = []
	weights = []
	for mod in most_common:
		mods.append(mod[0])
		weights.append(mod[1])	
	return dcc.Graph(figure=getBarChart(mods,weights,bg_colour=True),
		             config={'displayModeBar': False},
		             id='bowl-m-graph')


if __name__ == '__main__':
    app.run_server(debug=True)

