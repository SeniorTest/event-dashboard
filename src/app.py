import base64
import datetime
from datetime import datetime as dt
import glob
import json
import os
import logging

# external modules
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.exceptions import PreventUpdate
import dash_html_components as html
import dash_table
from flask import Flask, request
import pandas as pd

# own modules
import config
import charts
import event_schema_validation
import sequence_diagram
import es_handler

# from waitress import serve

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

print('\n\n\n############################## initialise app \n\n\n')
logging.basicConfig(format='%(asctime)s - [%(levelname)s] %(message)s [%(pathname)s %(funcName)s %(lineno)d]',
                    datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
# config parameters
url_base_path = config.config['url_base_path']
schema_directory = config.config['schema_directory']
index = config.config['index']

# initialise app with some data
kafka_events = json.load(open('initial_event.json'))
events_df = pd.DataFrame(kafka_events)

server = Flask(__name__)


@server.route(url_base_path + 'api/eventSchema', methods=['POST'])
def post_event_schema():
    print('---------------schema posted')
    event_schema = request.get_json(force=True)

    schema_filename = 'event_schema_' + str(datetime.datetime.now().isoformat()).split('.')[0].replace(':',
                                                                                                       '') + '.json'
    with open(schema_directory + '/' + schema_filename, 'w') as schema_file:
        json.dump(event_schema, schema_file)

    return {'message': 'reveived event_schema',
            'event_schema': event_schema}, 200


app = dash.Dash(server=server, url_base_pathname=url_base_path, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.config['suppress_callback_exceptions'] = True

msc = charts.create_sequence_diagram(kafka_events)
number_of_event_names_pie = charts.create_pie_chart(events_df, 'name')
number_of_event_sources_pie = charts.create_pie_chart(events_df, 'source')

with open(max(glob.glob(schema_directory + '/*.json'), key=os.path.getctime)) as schema_file:
    event_schema = json.load(schema_file)

conditional_format, tooltips = event_schema_validation.select_events_which_are_not_valid(events_df, event_schema)

events_df['valid'] = conditional_format
events_df['tooltip_message'] = tooltips
events_df['delta'] = 0
events_df = charts.create_events_table(events_df)

print('\n\n\n############################## initialise app \n\n\n')
logging.info('############################## initialise app ###################')

download_link = html.Div(
    children=[
        html.A(dbc.Button('Download Sequence Diagram'),
               id='download-link',
               download="msc_" + str(datetime.datetime.now().isoformat()).split('.')[0].replace(':', '') + '.png',
               href='',
               target="_blank")])

navbar = dbc.Navbar(
    color="dark",
    dark=True,
    children=[
        dbc.NavbarBrand("Event Monitor", className="ml-2"),
        html.Div(
            style={
                'marginLeft': 50,
                'marginRight': 50
            },
            children=[
                dbc.Tooltip('Min Timestamp',
                            target="min_timestamp_input"
                            ),
                html.Div([
                    dbc.Input(id='min_timestamp_input', type='text'),
                ])
            ]),
        html.Div(
            style={
                'marginLeft': 50,
                'marginRight': 50
            },
            children=[
                dbc.Tooltip('Max Timestamp',
                            target="max_timestamp_input"
                            ),
                html.Div([
                    dbc.Input(id='max_timestamp_input', type='text'),
                ])
            ]),
        html.Div(
            style={
                'marginLeft': 50,
                'marginRight': 50
            },
            children=[
                dbc.Button('Apply filter', id='refresh', color='primary', n_clicks_timestamp=0),
            ]),
        html.Div(
            style={
                'marginLeft': 50,
                'marginRight': 50
            },
            children=[
                dbc.Button('Reset filter', id='clear', color='warning', n_clicks_timestamp=0)
            ]),
        html.Div(
            children=[
                dcc.Loading(
                    id="loading-2",
                    children=[html.Div([html.Div(id="loading-output-2", style={'display': 'none'})])],
                    type="circle",
                ),
            ]
        ),
    ],
    sticky="top",
)

number_of_events_collapse = html.Div(
    [
        dbc.Button(
            "Number of events",
            id="number_of_events_collapse_button",
            className="mb-3",
            color="info",
            block=True
        ),
        dbc.Collapse(
            dbc.Col(
            ),
            id="number_of_events_collapse"
        ),
    ]
)

timeseries_collapse = html.Div(
    [
        dbc.Button(
            "Timeseries of events",
            id="timeseries_collapse_button",
            className="mb-3",
            color="info",
            block=True
        ),
        dbc.Collapse(
            dbc.Col(

            ),
            id="timeseries_collapse",
        ),
    ]
)

timedelta_collapse = html.Div(
    [
        dbc.Button(
            "Time delta",
            id="timedelta_collapse_button",
            className="mb-3",
            color="info",
            block=True
        ),
        dbc.Collapse(
            dbc.Col(),
            id="timedelta_collapse",
        )
    ]
)

sequence_diagram_collapse = html.Div(
    [
        dbc.Button(
            "Sequence Diagram",
            id="sequence_diagram_collapse_button",
            className="mb-3",
            color="info",
            block=True
        ),
        dbc.Collapse(
            dbc.Col(

            ),
            id="sequence_diagram_collapse",
        ),
    ]
)

plantuml_msc_collapse = html.Div(
    [
        dbc.Button(
            "Plantuml Sequence Diagram (wip)",
            id="plantuml_msc_collapse_button",
            className="mb-3",
            color="info",
            block=True
        ),
        dbc.Collapse(
            id="plantuml_msc_collapse",
        ),
    ]
)

if glob.glob('assets/images/*.png'):
    top_card = html.Div(id='msc_png_card', children=[
        html.Img(src='data:image/png;base64,{}'.format(
            base64.b64encode(open(max(glob.glob('assets/images/*.png'), key=os.path.getctime), 'rb').read()).decode(
                'ascii')))
    ])
else:
    top_card = html.Div(id='msc_png_card', children=[
    ])

dbc_body = dbc.Container(fluid=True, children=
[
    dbc.Row([
        dbc.Col(html.Div(
            children=[
                number_of_events_collapse
            ]),
            width=2),
        dbc.Col(html.Div(
            children=[
                timeseries_collapse
            ]),
            width=2),
        dbc.Col(html.Div(
            children=[
                timedelta_collapse
            ]),
            width=2),
        dbc.Col(html.Div(
            children=[
                sequence_diagram_collapse
            ]),
            width=2),
        dbc.Col(html.Div(
            children=[
                plantuml_msc_collapse
            ]),
            width=2),
    ]),
    dbc.Row([
        dbc.Col(html.Div(id='timedelta_details_div',
                         style={"border": "1px lightgrey solid"},
                         children=[

                         ]))
    ]),
    dbc.Row([
        dbc.Col(html.Div(id='number_of_events_details_div',
                         style={"border": "1px lightgrey solid"},
                         children=[

                         ]))
    ]),
    dbc.Row([
        dbc.Col(html.Div(id='timeseries_details_div',
                         style={"border": "1px lightgrey solid"},
                         children=[

                         ]))
    ]),
    dbc.Row([
        dbc.Col(html.Div(id='sequence_diagram_details_div',
                         style={"border": "1px lightgrey solid"},
                         children=[

                         ]))
    ]),
    dbc.Row([
        dbc.Col(html.Div(id='plantuml_msc_details_div',
                         style={"border": "1px lightgrey solid"},
                         children=[

                         ]))
    ]),

    dbc.Row([
        dbc.Col(html.Div(children=[
            html.H2("Table of events", id='table_title'),
            dbc.Tooltip(
                """
            Shows the details of the events.
            Filtering examples:
            to select all events from source adapto-asr add the following command to source column
            eq "adapto-asr"
            operators = [['ge ', '>='],
         ['le ', '<='],
         ['lt ', '<'],
         ['gt ', '>'],
         ['ne ', '!='],
         ['eq ', '='],
         ['contains '],
         ['datestartswith ']]

            """,
                target="table_title"
            )
        ]),
            width=6)
    ]),
    dbc.Row(
        [
            dbc.Col(
                [
                    dash_table.DataTable(
                        id='event-table',
                        columns=[{"name": i, "id": i} for i in events_df.columns if
                                 i not in ["tooltip_message", 'delta']],
                        fixed_rows={'headers': True, 'data': 0},
                        style_cell={'textAlign': 'left',
                                    'whiteSpace': 'normal',
                                    'font_size': '14px',
                                    'font_family': '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans",sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji"',
                                    'padding': '.50rem'
                                    },
                        style_table={'overflowX': 'scroll',
                                     'maxHeight': '1000px',
                                     'border': 'thin lightgrey solid'},
                        style_header={
                            'backgroundColor': 'white',
                            'fontWeight': 'bold'
                        },
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(248, 248, 248)'
                            },
                            {'if': {'column_id': 'valid'},
                             'width': '55px',
                             'maxWidth': '55px',
                             'textAlign': 'center'},
                            {'if': {
                                'column_id': 'valid',
                                'filter_query': '{valid} eq 0'
                            },
                                'backgroundColor': 'grey',
                                'opacity': 0.75,
                                'color': 'white',
                            },
                            {
                                'if': {
                                    'column_id': 'valid',
                                    'filter_query': '{valid} eq -1'
                                },
                                "backgroundColor": "#F08080",
                                "opacity": 0.75,
                                'color': 'white'
                            },
                            {
                                'if': {
                                    'column_id': 'valid',
                                    'filter_query': '{valid} eq 1'
                                },
                                "backgroundColor": "#3D9970",
                                "opacity": 0.75,
                                'color': 'white'
                            }
                        ],
                        data=events_df.to_dict("rows"),
                        tooltip_data=charts.create_tooltips(events_df.tooltip_message.tolist()),
                        filter_action='native',
                        sort_action='native',
                        sort_mode='multi',
                        page_action="native",
                        page_current=0,
                        page_size=25,
                    )
                ]
            ),
        ]
    ),
],
                         className="mt-4",
                         )

app.layout = html.Div(children=[navbar,
                                dbc_body,
                                dcc.Store(id='session_store', storage_type='session'),
                                dcc.Store(id='event_schema_store', storage_type='session'),
                                dcc.Store(id='memory'),
                                dcc.Store(id='last_cleared'),
                                dcc.Store(id='last_msc_generated'),
                                dcc.Interval(
                                    id='interval_event_schema_updating',
                                    interval=30000,
                                    n_intervals=0
                                )
                                ])


def get_events(start_time=None, end_time=None):
    """
    gets events from kafka adapter using group_id as kafka consumer group
    gets events from elasticsearch based on start and end time using group_id as kafka consumer group
    :param end_time:
    :param start_time:
    :return: events dataframe
    """
    # setup
    es = es_handler.connect_elasticsearch()
    logging.info('getting events from elasticsearch from index ' + index)
    logging.debug(es)

    tmp_df = pd.DataFrame(es_handler.get_all(es, index))
    print(tmp_df.head(2))

    if not tmp_df.empty:
        if start_time and end_time:
            print('using min max from parameters')
            print(start_time)
            print(end_time)
            min_timestamp = start_time
            max_timestamp = end_time
        else:
            logging.info('using min max from dataframe')
            min_timestamp = min(tmp_df['timestamp'])
            max_timestamp = max(tmp_df['timestamp'])
    else:
        logging.info('using hardcoded min max')
        min_timestamp = "2019-10-01T02:36:53.510Z"
        max_timestamp = "2019-10-20T02:36:58.510Z"

    search_object = {"query": {
        "range": {"timestamp": {"gte": min_timestamp, "lte": max_timestamp}}
    }}
    print(search_object)
    events = es_handler.search(es_object=es, index_name=index, search=search_object)
    df = pd.DataFrame(events)

    return df


def refresh_session_store(session_data, event_schema, start_time=None, end_time=None):
    logging.info('updating session_store')
    new_events = get_events(start_time, end_time)

    if not new_events.empty:
        # add schema validation information
        conditional_format, tooltips = event_schema_validation.select_events_which_are_not_valid(new_events,
                                                                                                 event_schema)
        new_events['valid'] = conditional_format
        new_events['tooltip_message'] = tooltips

        events_df = pd.DataFrame(new_events)
        events_df['delta'] = (
                pd.to_datetime(events_df['timestamp']) - pd.to_datetime(events_df['timestamp']).shift()).fillna(0)
        events_df['delta'] = events_df['delta'].apply(str)
        events = events_df.to_dict(orient='row')

    else:
        logging.info('_no_new events')
        raise PreventUpdate

    return json.dumps(events)


def clear_session_store():
    logging.info('clearing session store ')
    return get_events(start_time=None, end_time=None).to_dict(orient='row')


@app.callback(dash.dependencies.Output('event_schema_store', 'data'),
              [dash.dependencies.Input('interval_event_schema_updating', 'n_intervals')])
def update_event_schema(n_intervals):
    logging.info('updating_event_schema')
    with open(max(glob.glob(schema_directory + '/*.json'), key=os.path.getctime)) as schema_file:
        event_schema = json.load(schema_file)

    logging.info(event_schema)

    return event_schema


@app.callback(
    dash.dependencies.Output('memory', "data"),
    [dash.dependencies.Input('event-table', "derived_virtual_data"),
     dash.dependencies.Input('event-table', "derived_virtual_selected_rows")])
def update_session_memory(rows, derived_virtual_selected_rows):
    # When the table is first rendered, `derived_virtual_data` and
    # `derived_virtual_selected_rows` will be `None`. This is due to an
    # idiosyncracy in Dash (unsupplied properties are always None and Dash
    # calls the dependent callbacks when the component is first rendered).
    # So, if `rows` is `None`, then the component was just rendered
    # and its value will be the same as the component's dataframe.
    # Instead of setting `None` in here, you could also set
    # `derived_virtual_data=df.to_rows('dict')` when you initialize
    # the component.
    logging.info('applying filter on table')
    logging.debug(rows)
    logging.debug(derived_virtual_selected_rows)

    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    if not rows:
        dff = pd.DataFrame(
            columns=['timestamp', 'name', 'source', 'correlationId', 'payload', 'id', 'causationId'])
    else:
        dff = pd.DataFrame(rows)
        dff['delta'] = (
                pd.to_datetime(dff['timestamp']) - pd.to_datetime(dff['timestamp']).shift()).fillna(0)
        dff['delta'] = dff['delta'].apply(str)

    logging.debug(dff)
    return dff.to_json(orient='records')


@app.callback([dash.dependencies.Output('session_store', 'data'),
               dash.dependencies.Output("loading-output-2", "children"),
               dash.dependencies.Output('last_cleared', 'data')],
              [dash.dependencies.Input('refresh', 'n_clicks_timestamp'),
               dash.dependencies.Input('clear', 'n_clicks_timestamp')],
              [dash.dependencies.State('session_store', 'data'),
               dash.dependencies.State('last_cleared', 'data'),
               dash.dependencies.State('event_schema_store', 'data'),
               dash.dependencies.State('min_timestamp_input', 'value'),
               dash.dependencies.State('max_timestamp_input', 'value')])
def update_session_store(refresh, clear, session_data, last_cleared, event_schema, start_date, end_date):
    logging.info('refreshing data from source ' + ' ' + str(start_date) + ' ' + str(end_date))

    if not refresh:
        refresh = 0
    if not clear:
        clear = 0
    if not last_cleared:
        last_cleared = 0

    if int(clear) > int(last_cleared):
        refreshed_data = refresh_session_store(session_data, event_schema)

    else:
        refreshed_data = refresh_session_store(session_data, event_schema, start_date, end_date)

        if refreshed_data == session_data:
            logging.info('_no_update on data')
            raise PreventUpdate
        else:
            logging.info('_update')

    return refreshed_data, refresh, clear


@app.callback(
    dash.dependencies.Output('number_of_event_names', 'figure'),
    [dash.dependencies.Input('memory', 'data')])
def update_pie_chart_by_name(session_data):
    return charts.create_pie_chart(pd.read_json(session_data), 'name')


@app.callback(
    dash.dependencies.Output('number_of_event_sources', 'figure'),
    [dash.dependencies.Input('memory', 'data')])
def update_pie_chart_by_source(session_data):
    return charts.create_pie_chart(pd.read_json(session_data), 'source')


@app.callback(
    dash.dependencies.Output('time_delta', 'figure'),
    [dash.dependencies.Input('memory', 'data')])
def update_timedelta_chart(session_data):
    return charts.create_timedelta_graph(pd.read_json(session_data))


@app.callback(
    [dash.dependencies.Output('event-table', 'data'),
     dash.dependencies.Output('event-table', 'tooltip_data')],
    [dash.dependencies.Input('session_store', 'data'),
     dash.dependencies.Input('event-table', "filter_query")])
def update_table(session_data, filter_query):
    if session_data != '[]' and session_data:
        tooltips_df = pd.DataFrame(json.loads(session_data))

        table_data = charts.create_events_table(pd.DataFrame(json.loads(session_data)))
        tooltips = charts.create_tooltips(tooltips_df.tooltip_message.tolist())

        return table_data[table_data.columns.tolist()[:-1]].to_dict('rows'), tooltips
    else:
        return [], []


@app.callback(
    [dash.dependencies.Output('event-timeseries', 'figure'),
     dash.dependencies.Output('sequence_diagram', 'figure'),
     dash.dependencies.Output("loading_indicator_ts", "children")],
    [dash.dependencies.Input('memory', 'data')])
def update_charts(session_data):
    df = pd.read_json(session_data)

    try:
        df['timestamp'] = df['timestamp'].apply(str)
    except:
        logging.info('no timestamp in dataframe')
    kafka_events = df.to_dict(orient='records')

    return charts.create_event_timeseries(kafka_events), charts.create_sequence_diagram(
        kafka_events), 0


@app.callback(
    [dash.dependencies.Output('msc_png_card', 'children'),
     dash.dependencies.Output('last_msc_generated', 'data'),
     dash.dependencies.Output('download-link', 'href')],
    [dash.dependencies.Input('generate_sequence_diagram', 'n_clicks'),
     dash.dependencies.Input('memory', 'data')],
    [dash.dependencies.State('memory', 'data'),
     dash.dependencies.State('last_msc_generated', 'data'),
     dash.dependencies.State('event_schema_store', 'data')]
)
def update_image(n_clicks, updated_session_data, session_data, last_msc_generated, event_schema):
    if last_msc_generated is None:
        last_msc_generated = 0

    if n_clicks is None:
        n_clicks = 0

    if updated_session_data == '[]':
        logging.info('going to reset png')
        return [], n_clicks, ''

    elif n_clicks > last_msc_generated:
        df = pd.read_json(session_data)
        filename = sequence_diagram.create_sequence_diagram(df, event_schema)

        return [
            html.Img(src='data:image/png;base64,{}'.format(
                base64.b64encode(open(filename, 'rb').read()).decode(
                    'ascii'))), n_clicks, filename
        ]
    else:
        return [], n_clicks, ''


@app.callback(
    [dash.dependencies.Output("timedelta_collapse", "is_open"),
     dash.dependencies.Output('timedelta_details_div', 'children'),
     dash.dependencies.Output('timedelta_collapse_button', 'color')],
    [dash.dependencies.Input("timedelta_collapse_button", "n_clicks")],
    [dash.dependencies.State("timedelta_collapse", "is_open"),
     dash.dependencies.State("memory", "data")])
def toggle_timedelta_collapse(n, is_open, session_data):
    if is_open is None:
        return False, None, "dark"

    elif is_open:
        return False, None, "dark"

    else:
        fig = charts.create_timedelta_graph(pd.read_json(session_data))

        chart = dbc.Row([
            dbc.Col(html.Div(
                style={
                    'width': '100%',
                },
                children=[
                    html.H2("Time delta in milliseconds (logarithmic scale)"),
                    dcc.Graph(
                        id='time_delta',
                        figure=fig
                    )
                ]),
                width=12
            )
        ]),

        return True, chart, "light"


@app.callback(
    [dash.dependencies.Output("number_of_events_collapse", "is_open"),
     dash.dependencies.Output("number_of_events_details_div", "children"),
     dash.dependencies.Output('number_of_events_collapse_button', 'color')],
    [dash.dependencies.Input("number_of_events_collapse_button", "n_clicks")],
    [dash.dependencies.State("number_of_events_collapse", "is_open")])
def toggle_number_of_events_collapse(n, is_open):
    if is_open is None:
        return False, None, "dark"

    elif is_open:
        return False, None, "dark"

    else:
        chart = dbc.Row([
            dbc.Col(html.Div(
                children=[
                    html.H2("Number of events by source"),
                    dcc.Graph(id='number_of_event_sources', figure=number_of_event_sources_pie)
                ]),
                width=6
            ),
            dbc.Col(html.Div(
                children=[
                    html.H2("Number of events by name"),
                    dcc.Graph(id='number_of_event_names', figure=number_of_event_names_pie)
                ]),
                width=6
            )
        ]),

        return True, chart, "light"


@app.callback(
    [dash.dependencies.Output("sequence_diagram_collapse", "is_open"),
     dash.dependencies.Output("sequence_diagram_details_div", "children"),
     dash.dependencies.Output('sequence_diagram_collapse_button', 'color')],
    [dash.dependencies.Input("sequence_diagram_collapse_button", "n_clicks")],
    [dash.dependencies.State("sequence_diagram_collapse", "is_open"),
     dash.dependencies.State('memory', 'data')])
def toggle_sequence_diagram_collapse(n, is_open, session_data):
    if is_open is None:
        return False, None, "dark"

    elif is_open:
        return False, None, "dark"

    else:
        df = pd.read_json(session_data)

        try:
            df['timestamp'] = df['timestamp'].apply(str)
        except:
            logging.info('no timestamp in dataframe')

        kafka_events = df.to_dict(orient='records')

        msc = charts.create_sequence_diagram(kafka_events)

        chart = dbc.Row([
            dbc.Col(html.Div(
                style={
                    'width': '100%',
                },
                children=[
                    dcc.Graph(id='sequence_diagram', figure=msc)
                ]),
                width=12
            )
        ]),

        return True, chart, "light"


@app.callback(
    [dash.dependencies.Output("plantuml_msc_collapse", "is_open"),
     dash.dependencies.Output("plantuml_msc_details_div", "children"),
     dash.dependencies.Output('plantuml_msc_collapse_button', 'color')],
    [dash.dependencies.Input("plantuml_msc_collapse_button", "n_clicks")],
    [dash.dependencies.State("plantuml_msc_collapse", "is_open"),
     dash.dependencies.State('memory', 'data')])
def toggle_plantuml_msc_collapse(n_clicks, is_open, session_data):
    logging.info('toggle_plantuml_msc_collapse clicked for ' + str(n_clicks))

    result_values = False, None, "dark"

    if is_open is not None and not is_open:
        events_df = pd.read_json(session_data)

        try:
            events_df['timestamp'] = events_df['timestamp'].apply(str)
        except:
            logging.info('no timestamp in dataframe')

        chart = dbc.Row([
            dbc.Col(html.Div(
                style={
                    'width': '100%',
                },
                children=[
                    html.Div(
                        style={
                            'marginUp': 50,
                            'marginDown': 50,
                            'marginLeft': 50,
                            'marginRight': 50
                        },
                        children=[
                            dbc.Row([dbc.Col(
                                dbc.Button(
                                    'Generate Sequence Diagram',
                                    id='generate_sequence_diagram',
                                    className="mb-3",
                                    color="info"
                                ),
                                width=2
                            ),

                                dbc.Col(
                                    download_link,
                                    width=2
                                )])
                        ]),
                    top_card,
                ]),
                width=12
            )
        ]),

        result_values = True, chart, "light"

    return result_values


@app.callback(
    [dash.dependencies.Output("timeseries_collapse", "is_open"),
     dash.dependencies.Output("timeseries_details_div", "children"),
     dash.dependencies.Output('timeseries_collapse_button', 'color')],
    [dash.dependencies.Input("timeseries_collapse_button", "n_clicks")],
    [dash.dependencies.State("timeseries_collapse", "is_open"),
     dash.dependencies.State('memory', 'data')])
def toggle_timeseries_collapse(n_clicks, is_open, session_data):
    logging.info('toogle_timeseries_collapse clicked for ' + str(n_clicks))

    result_values = False, None, "dark"

    if is_open is not None and not is_open:

        events_df = pd.read_json(session_data)

        try:
            events_df['timestamp'] = events_df['timestamp'].apply(str)
        except:
            logging.info('no timestamp in dataframe')

        list_of_events = events_df.to_dict(orient='records')

        timeseries_figure = charts.create_event_timeseries(list_of_events)

        chart = dbc.Row([
            dbc.Col(html.Div(
                style={
                    'width': '100%',
                },
                children=[
                    dcc.Graph(id='event-timeseries', figure=timeseries_figure)
                ]),
                width=12
            )
        ]),

        result_values = True, chart, "light"

    return result_values


@app.callback(
    [dash.dependencies.Output('min_timestamp_input', 'value'),
     dash.dependencies.Output('max_timestamp_input', 'value')],
    [dash.dependencies.Input('memory', 'data')])
def update_start_end_date(session_data):
    print('---------------->')
    events_df = pd.read_json(session_data)

    if not events_df.empty:
        min_timestamp = min(events_df['timestamp'])
        max_timestamp = max(events_df['timestamp'])
    else:
        min_timestamp = ""
        max_timestamp = ""

    print('returning ', min_timestamp)
    return min_timestamp, max_timestamp

    string_prefix = 'You have selected: '
    if start_date is not None:
        start_date = dt.strptime(start_date, '%Y-%m-%d')
        start_date_string = start_date.strftime('%B %d, %Y')
        string_prefix = string_prefix + 'Start Date: ' + start_date_string + ' | '
    if end_date is not None:
        end_date = dt.strptime(end_date, '%Y-%m-%d')
        end_date_string = end_date.strftime('%B %d, %Y')
        string_prefix = string_prefix + 'End Date: ' + end_date_string
    if len(string_prefix) == len('You have selected: '):
        return 'Select a date to see it displayed here'
    else:
        return string_prefix


if __name__ == '__main__':
    # serve(app.server, host='0.0.0.0', port=18550)
    # serve(app.server, host='127.0.0.1', port=18550)
    # app.run_server(host='0.0.0.0', port=18550)
    app.run_server(debug=True, host='127.0.0.1', port=18550)
