# -*- coding: utf-8 -*-
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import flask
import base64

from app import app
import app_team, app_players

seasons = ['2018','2019','All']
match_types = ['Full Length', '20 Overs','All']
disciplines = ['Batting', 'Bowling']
inter_tav_types = ["Railway Taverners CC","Inter Tavs","All"]
inter_tav_teams = ["President's XI", "Andy James Invitational XI", "Railway Taverners XI"]


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
                value='All',
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

    ], id='masthead-div',
       className='hidden-grid l-grid')


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    #getMasthead(),

    html.Div(id='page-content', className='l-grid'),
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if not pathname: 
        return app_team.getLayout()

    if pathname == "/team": 
        layout = app_team.getLayout()
        print "We here or what?"
        return layout
    if pathname == '/players':
        return app_players.getLayout()
    else:
        return app_team.getLayout()





if __name__ == '__main__':
    app.run_server(debug=True)
