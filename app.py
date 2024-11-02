#!/usr/bin/env python3
"""
Flask
Django
Dash-Plotly (Flask + React js) - Web application


"""
import pandas as pd
import dash
from dash import html
import webbrowser
from dash.dependencies import Input as In
from dash.dependencies import Output as Out
from dash import dcc
import plotly.graph_objects as go
import plotly.express as px
from dash.exceptions import PreventUpdate
from flask import Flask, request, jsonify
import os
import requests

# Global variables
app = dash.Dash(__name__)
server = app.server  # Access the underlying Flask server instance




def load_data():
    global df, countries, years, year_list, month, day_list, day, region, state, city, attack_type,\
           world_chart_options, token
    token = 'pk.eyJ1IjoiZGVldmVzaGl6bSIsImEiOiJja2VrenI3amEwZXJtMnNwd242YW42ajJpIn0.FqsxGZu5Q5vUAjNRIq6IvA'
    
    file_name = "global_terror.csv"
    df = pd.read_csv(file_name)
    
    pd.options.mode.chained_assignment = None
    
    month_dict = {'January': 1,
                  'February': 2,
                  'March': 3,
                  'April': 4,
                  'May': 5,
                  'June': 6,
                  'July': 7,
                  'August': 8,
                  'September': 9,
                  'October': 10,
                  'November': 11,
                  'December': 12}
    month = [{'label': key, 'value': value} for key, value in month_dict.items()]
    
    day_list = [x for x in range(1, 32)]
    day = [{'label': str(x), 'value': x} for x in day_list]
    
    region = [{'label': str(i), 'value': str(i)} for i in sorted(df['region_txt'].unique().tolist())]
    
    # Taking all the countries in the form of a list
    # temp_list = sorted(df["country_txt"].unique().tolist())
    # Converting that country list (temp_list) to a list of Dictionary as the in dcc.Dropdown,
    # The option argument accepts list of dictionary only
    # countries = [{'label': str(i), 'value': str(i)} for i in sorted(df["country_txt"].unique().tolist())]
    countries = df.groupby('region_txt')['country_txt'].unique().apply(list).to_dict()
    
    # state = [{'label': str(i), 'value': str(i)} for i in df['provstate'].unique().tolist()]
    state = df.groupby('country_txt')['provstate'].unique().apply(list).to_dict()
    
    # city = [{'label': str(i), 'value': str(i)} for i in df['city'].unique().tolist()]
    city = df.groupby('provstate')['city'].unique().apply(list).to_dict()
    
    attack_type = [{'label': str(i), 'value': str(i)} for i in df['attacktype1_txt'].unique().tolist()]
    
    # Creating a year_list
    year_list = sorted(df['iyear'].unique().tolist())
    # converting the year_list into a dictionary as the dcc.Slider takes a dictionary as an input in the marks argument
    years = {str(year): str(year) for year in year_list}
    
    # Global Chart tool options
    chart_dropdown_values = {
        'Terrorist Organisation': 'gname',
        'Target Nationality': 'natlty1_txt',
        'Target Type': 'targtype1_txt',
        'Type of Attack': 'attacktype1_txt',
        'Weapon Type': 'weaptype1_txt',
        'Region': 'region_txt',
        'Country Attacked': 'country_txt'
    }
    world_chart_options = [{'label': key, 'value': value} for key, value in chart_dropdown_values.items()]


def open_webbrowser():
    url = "http://127.0.0.1:8080/"  # Dash always runs the server on this ip:port address http://127.0.0.1:8050/
    webbrowser.open_new(url)

@server.route('/api/filter-data', methods=['POST'])
def filter_data():
    data = request.json  # Get the JSON data from the request

    # Retrieve filter values from the JSON payload
    region = data.get("region", [])
    country = data.get("country", [])
    attack_type = data.get("attack_type", [])
    year_start = data.get("year_start", min(year_list))  # Default to the earliest year if not provided
    year_end = data.get("year_end", max(year_list))      # Default to the latest year if not provided

    # Create a year range from year_start and year_end
    year_range = range(year_start, year_end + 1)

    # Apply filters to the DataFrame
    filtered_df = df.copy()
    filtered_df = filtered_df[filtered_df['iyear'].isin(year_range)]
    if region:
        filtered_df = filtered_df[filtered_df['region_txt'].isin(region)]
    if country:
        filtered_df = filtered_df[filtered_df['country_txt'].isin(country)]
    if attack_type:
        filtered_df = filtered_df[filtered_df['attacktype1_txt'].isin(attack_type)]

    # Return the filtered data as a JSON response
    result = filtered_df.to_dict(orient='records')
    return jsonify(result)


def create_app_ui():
    main_layout = html.Div(id='body', style={'fontFamily': 'Arial, Helvetica, sans-serif'}, children=[
        html.Div(id='heading', children=[
            html.H1(id='head', style={'textAlign': 'center'}, children='TERRORISM ANALYSIS AND INSIGHTS'),
            html.Br(),
            
            dcc.Tabs(id='tabs', value='Map', children=[
                dcc.Tab(label='Map Tool', id='map tool', value='Map', children=[
                    dcc.Tabs(id='subtabs', value='WorldMap', children=[
                        dcc.Tab(label='World Map', id='world map', value='WorldMap', children=[
                        ]),
                        dcc.Tab(label='India Map', id='india map', value='IndiaMap', children=[
                        ])
                    ]),
                    html.Br(),
                    html.H2(children='Map Filters', id='filter'),
                    dcc.Dropdown(id='month',
                                 options=month,
                                 placeholder='Select Month',  # default value
                                 style={'width': 300, 'borderRadius': '15px', 'position': 'relative'},
                                 multi=True
                                 ),
                    dcc.Dropdown(id='day',
                                 options=day,
                                 placeholder='Select Day',  # default value
                                 style={'width': 300, 'borderRadius': '15px', 'position': 'relative'},
                                 multi=True
                                 ),
                    dcc.Dropdown(id='region',
                                 options=region,
                                 placeholder='Select Region',  # default value
                                 style={'width': 300, 'borderRadius': '15px', 'position': 'relative'},
                                 multi=True
                                 ),
                    dcc.Dropdown(id='country',
                                 options=[{'label': 'All', 'value': 'All'}],
                                 placeholder='Select Country',  # default value
                                 style={'width': 300, 'borderRadius': '15px', 'position': 'relative'},
                                 multi=True
                                 ),
                    dcc.Dropdown(id='state',
                                 options=[{'label': 'All', 'value': 'All'}],
                                 placeholder='Select State',  # default value
                                 style={'width': 300, 'borderRadius': '15px', 'position': 'relative'},
                                 multi=True
                                 ),
                    dcc.Dropdown(id='city',
                                 options=[{'label': 'All', 'value': 'All'}],
                                 placeholder='Select City',  # default value
                                 style={'width': 300, 'borderRadius': '15px', 'position': 'relative'},
                                 multi=True
                                 ),
                    dcc.Dropdown(id='attack_type',
                                 options=attack_type,
                                 placeholder='Select Attack Type',  # default value
                                 style={'width': 300, 'borderRadius': '15px', 'position': 'relative'},
                                 multi=True
                                 ),
                    html.Br(),
                    html.H2(children='Select the year', id='year_title'),
                    dcc.RangeSlider(id='year-slider',
                                    min=min(year_list),
                                    max=max(year_list),
                                    value=[min(year_list), max(year_list)],
                                    marks=years,  # Slider values
                                    step=None
                                    ),
                    html.Br()
                ]),
                dcc.Tab(label='Chart Tool', id='chart tool', value='Chart', children=[
                    dcc.Tabs(id='subtabs2', value='WorldChart', children=[
                        dcc.Tab(label='World Chart', id='world_chart', value='WorldChart', children=[]),
                        dcc.Tab(label='India Chart', id='india chart', value='IndiaChart')
                    ]),
                    html.Br(),
                    html.H2(id='chartFilter', children='Chart Filters'),
                    dcc.Dropdown(id='chart',
                                 options=world_chart_options,
                                 placeholder='Select an option',
                                 value='region_txt',
                                 style={'width': 300, 'borderRadius': '15px'}
                                 ),
                    html.Br(),
                    dcc.Input(id='search',
                              placeholder='Search Filter',
                              style={'width': 293, 'borderRadius': '13px', 'height': 26}
                              ),
                    html.Br(),
                    html.Br(),
                    html.H2(children='Select Year Range'),
                    dcc.RangeSlider(id='cyear_slider',
                                    min=min(year_list),
                                    max=max(year_list),
                                    value=[min(year_list), max(year_list)],
                                    marks=years,  # Slider values
                                    step=None
                                    ),
                    html.Br()
                ])
            ])
        ]),
        html.Br(),
        html.Div(id='graph', children='Graph will be shown here')
    ])
    return main_layout


@app.callback(
    Out('graph', 'children'),
    [In('tabs', 'value'),
     In('month', 'value'),
     In('day', 'value'),
     In('region', 'value'),
     In('country', 'value'),
     In('state', 'value'),
     In('city', 'value'),
     In('attack_type', 'value'),
     In('year-slider', 'value'),
     In('cyear_slider', 'value'),
     
     In('chart', 'value'),
     In('search', 'value'),
     In('subtabs2', 'value')
     ]
)

def update_app_ui(tabs, month_value, day_value, region_value, country_value, state_value, city_value, 
                  attack_type_val, year_value, cyear_value, chart_dp_values, search, subtabs2):
    fig = None

    if tabs == 'Map':
        # Define the year range from the slider
        year_start, year_end = year_value if year_value else (1970, 2018)

        # Create the payload for the API request
        payload = {
            "region": region_value if region_value else [],
            "country": country_value if country_value else [],
            "state": state_value if state_value else [],
            "city": city_value if city_value else [],
            "attack_type": attack_type_val if attack_type_val else [],
            "year_start": year_start,
            "year_end": year_end,
            "month": month_value if month_value else [],
            "day": day_value if day_value else []
        }

        # Call the API to fetch the filtered data
        try:
            response = requests.post('http://127.0.0.1:8080/api/filter-data', json=payload)
            response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
            data = response.json()  # Parse JSON response
        except requests.exceptions.RequestException as e:
            return html.Div(f"Error fetching data from API: {e}")

        # Convert the JSON response to a DataFrame
        if not data:
            return html.Div("No data available for the selected filters.")
        new_df = pd.DataFrame(data)

        # Create the map figure
        fig = px.scatter_mapbox(
            new_df,
            lat='latitude',
            lon='longitude',
            hover_data=['region_txt', 'country_txt', 'provstate', 'city', 'attacktype1_txt', 'nkill', 'iyear'],
            zoom=1,
            color='attacktype1_txt',
            height=650
        )

        fig.update_layout(
            mapbox_style='carto-positron',
            mapbox_accesstoken=token,
            autosize=True,
            margin=dict(l=0, r=0, b=25, t=20),
            template='plotly_dark'
        )

    elif tabs == 'Chart':
        year_range_c = range(cyear_value[0], cyear_value[1] + 1) if cyear_value else range(2000, 2022)
        chart_df = df[df['iyear'].isin(year_range_c)]

        if subtabs2 == 'WorldChart':
            pass
        elif subtabs2 == 'IndiaChart':
            chart_df = chart_df[(chart_df['region_txt'] == 'South Asia') & (chart_df['country_txt'] == 'India')]

        if chart_dp_values and chart_df.shape[0]:
            if search:
                chart_df = chart_df.groupby('iyear')[chart_dp_values].value_counts().reset_index(name='count')
                chart_df = chart_df[chart_df[chart_dp_values].str.contains(search, case=False)]
            else:
                chart_df = chart_df.groupby('iyear')[chart_dp_values].value_counts().reset_index(name='count')

        if chart_df.shape[0] == 0:
            chart_df = pd.DataFrame(columns=['iyear', 'count', chart_dp_values])
            chart_df.iloc[0] = [0, 0, 'No Data']

        fig = px.area(chart_df, x='iyear', y='count', color=chart_dp_values, template='plotly_dark')

    return dcc.Graph(figure=fig)
    
@app.callback(
    Out('day', 'options'),
    [In('month', 'value')]
)
def day_options(value):
    date_list = [x for x in range(1, 32)]
    option = []
    if value:
        option = [{"label": m, "value": m} for m in date_list]
    return option


@app.callback(
    [Out('region', 'value'),
     Out('region', 'disabled'),
     Out('country', 'value'),
     Out('country', 'disabled')],
    [In('subtabs', 'value')]
)
def update_r(sub_value):
    region_v = None
    disabled_r = False
    country_v = None
    disabled_c = False
    if sub_value == 'WorldMap':
        pass
    elif sub_value == 'IndiaMap':
        region_v = ['South Asia']
        disabled_r = True
        country_v = ['India']
        disabled_c = True
    return region_v, disabled_r, country_v, disabled_c
    

@app.callback(
    Out('country', 'options'),
    [In('region', 'value')]
)
def country_option(r_value):
    option = []
    if r_value is None:
        raise PreventUpdate
    else:
        for var in r_value:
            if var in countries.keys():
                option.extend(countries[var])
    return [{'label': m, 'value': m} for m in option]


@app.callback(
    Out('state', 'options'),
    [In('country', 'value')]
)
def state_option(c_value):
    option = []
    if c_value is None:
        raise PreventUpdate
    else:
        for var in c_value:
            if var in state.keys():
                option.extend(state[var])
    return [{'label': m, 'value': m} for m in option]


@app.callback(
    Out('city', 'options'),
    [In('state', 'value')]
)
def city_option(s_value):
    option = []
    if s_value is None:
        raise PreventUpdate
    else:
        for var in s_value:
            if var in city.keys():
                option.extend(city[var])
    return [{'label': m, 'value': m} for m in option]


def main():
    # webpage of the
    load_data()
    open_webbrowser()
    
    global app
    app.layout = create_app_ui()
    app.title = "Terrorism Analysis And Insights"
    
    app.run_server(debug=True, host="0.0.0.0", port=8080)
    
    app = None
    df = None


if __name__ == '__main__':
    main()
