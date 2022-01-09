# -*- coding: utf-8 -*-
from dash import dcc
from dash import html

def getHeader(active):
	header_logo = html.Div([html.A(className="header__logo",
										   href='/')])
	header_items = [
		html.Li(
			dcc.Link("Team", href="/team", className="header__link"),
			className="header__item {0}".format("is-active" if active == "team" else "")
		),
		html.Li(
			dcc.Link("Players", href="/players", className="header__link"),
			className="header__item {0}".format("is-active" if active == "players" else "")
		),
	]
	header_list = html.Ul(header_items, className="header__list")


	return html.Div([
		header_logo,
		header_list,
	], className="header t-sans")
