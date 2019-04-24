# -*- coding: utf-8 -*-
from flask import Flask
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
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
match_types = ['All', '20 Overs', 'Full length']

def getMasthead():

	return html.Div([
		#html.H1("Batting", className='masthead__title t-sans t-title'),
		html.Div(
			dcc.Dropdown(id='player-selection', 
						#options=[{'label': i, 'value': i} for i in player_names],
						placeholder='Choose Player...'),
			className='masthead__column_1',
			id='player-selection-div'
		),
		html.Div(
			dcc.Dropdown(
				id='season-selection',
				options=[{'label': i, 'value': i} for i in seasons],
				placeholder='Choose Season...'
			),
			className='masthead__column_2',
			id='season-selection-div'
		),
		html.Div(
			dcc.Dropdown(
				id='match-type-selection',
				options=[{'label': i, 'value': i} for i in match_types],
				placeholder='Choose Match Type...'
			),
			className='masthead__column_3',
			id='match-type-selection-div'
		),
	], className='masthead l-grid')

app.layout = html.Div([
		dcc.Location(id='url', refresh=False),
		html.Div([
					getMasthead(),
					html.Div(id='batting-stats-div',className='tavs__batting-stats'),
					html.Div(id='timeline-graph',className='tavs__batting-graph'),
					html.Div(id='mod-graph',className='tavs__batting-mod-graph'),
					#html.Div(id='batting-pos-graph',className='tavs__batting-pos-graph')

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
@app.callback(
	Output('player-selection', 'options'),
	[Input('url', 'pathname')])
def playerSelection(url):

	df_batting = getBattingDataframe()
	player_names = df_batting['name'].unique()
	player_names.sort()

	return [{'label': i, 'value': i} for i in player_names]

@app.callback(
	Output('batting-stats-div', 'children'),
	[Input('player-selection', 'value'),
	Input('season-selection', 'value'),
	Input('match-type-selection', 'value')])
def populateBattingStats(player,
						 season,
						 match_type):
	if player is None: return None
	df_batting = getBattingDataframe()
	df_player = df_batting[df_batting['name'] == player]

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

	if outs:
		average = float(runs)/float(outs)
	else:
		average = 0.0

	df_ts = df_player[df_player['runs'] == top_score]
	if df_ts['out_bool'].values[0]:
		top_score_md = dcc.Markdown("Highest Score: " + "{:,}".format(int(top_score)))
	else:
		top_score_md = dcc.Markdown("Highest Score: " + "{:,}".format(int(top_score)) + "*")

	return html.Div([
					html.Div(
						[
							#html.Img(src=df_player['photo_url'].values.tolist()[0], className='tavs-unit__media'),
							html.H2('Batting Stats', className='tavs-stat-title'),
							html.Div([
								dcc.Markdown("No. Innings: " + "{:,}".format(int(innings))),
								dcc.Markdown("Total Runs: " + "{:,}".format(int(runs))),
								dcc.Markdown("Average: " + "{:.2f}".format(average)),
								top_score_md,
								dcc.Markdown("Total Fours: " + "{:,}".format(int(fours))),
								dcc.Markdown("Total Sixes: " + "{:,}".format(int(sixes))),
							], className='tavs-unit__extra-content'),
						],
						className='tavs-unit',
					),
				], className='tavs-grid__unit tavs-grid__unit--half')

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
	[Input('player-selection', 'value'),
	Input('season-selection', 'value'),
	Input('match-type-selection', 'value')])
def updateDismissalMethods(player,
						 season,
						 match_type):
	if player is None: return None
	df_batting = getBattingDataframe()
	df_player = df_batting[df_batting['name'] == player]

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


'''@app.callback(
	Output('batting-pos-graph', 'children'),
	[Input('player-selection', 'value'),
	Input('season-selection', 'value'),
	Input('match-type-selection', 'value')])
def updateBattingPositionAverage(player,
						 season,
						 match_type):
	if player is None: return None
	df_batting = getBattingDataframe()
	df_player = df_batting[df_batting['name'] == player]

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

	mods=[]
	weights=[]
	for i in range(1,11):
		df_pos = df_player[df_player['batting_order'] == i]
		runs = df_pos['runs'].sum()
		outs = df_pos['out_bool'].sum()
		if outs:
			average = float(runs)/float(outs)
		else:
			average = 0.0

		mods.append(i)
		weights.append(average)

	print mods
	print weights

	return dcc.Graph(figure=getBarChart(mods,weights,bg_colour=True),
		             config={'displayModeBar': False},
		             id='bat-p-graph')'''

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
	[Input('player-selection', 'value'),
	Input('season-selection', 'value'),
	Input('match-type-selection', 'value')])
def updateBattingInningsTimeline(player,
						 season,
						 match_type):
	if player is None: return None
	df_batting = getBattingDataframe()
	df_player = df_batting[df_batting['name'] == player]
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
	[Input('player-selection', 'value'),
	Input('season-selection', 'value'),
	Input('match-type-selection', 'value')])
def populateBowlingStats(player,
						 season,
						 match_type):
	if player is None: return None
	df_bowling = getBowlingDataframe()
	df_player = df_bowling[df_bowling['name'] == player]
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
						[	html.H2('Bowling Stats', className='tavs-stat-title'),
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
	[Input('player-selection', 'value'),
	Input('season-selection', 'value'),
	Input('match-type-selection', 'value')])
def updateBowlingInningsTimeline(player,
						 season,
						 match_type):
	if player is None: return None
	df_bowling = getBowlingDataframe()
	df_player = df_bowling[df_bowling['name'] == player]
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
	[Input('player-selection', 'value'),
	Input('season-selection', 'value'),
	Input('match-type-selection', 'value')])
def updateBowlingDismissalMethods(player,
						 season,
						 match_type):
	if player is None: return None
	df_bowling = getBowlingDataframe()
	df_player = df_bowling[df_bowling['name'] == player]
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

