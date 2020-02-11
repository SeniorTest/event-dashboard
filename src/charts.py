import plotly.graph_objs as go
import math
import pandas as pd

color_palette = ['#586BA4',
                 '#324376',
                 '#F5DD90',
                 '#F68E5F',
                 '#F76C5E']


def create_timedelta_graph(events_df):
    if events_df.empty:
        x_values = list()
        y_values = list()
        ticktext = list()
    else:
        events_df['delta_2'] = (
            pd.to_datetime(events_df['timestamp']) - pd.to_datetime(events_df['timestamp']).shift()).fillna(0)
        events_df['delta_2'] = events_df['delta_2'].astype('timedelta64[ms]')
        x_values = events_df.index.tolist()
        y_values = events_df.delta_2.tolist()
        ticktext = events_df.name.tolist()

    figure = {
        'data': [
            {'x': x_values, 'y': y_values, 'type': 'bar',
             'name': 'time delta in ms',
             'marker': {'color': color_palette[1]}},

        ],
        'layout': {
            'yaxis': dict(
                type='log',
                autorange=True,
                automargin=True,
                title=''
            ),
            'xaxis': dict(
                tickvals=x_values,
                ticktext=ticktext,
                automargin=True
            ),
            'height': 600,
        }
    }
    return figure


def create_pie_chart(events_df, grouped_by):
    sorted_bar_color_list = list()
    if not events_df.empty:
        number_of_events = events_df[grouped_by].value_counts().to_frame()

        for event in list(number_of_events.index):
            print('+++++')
            print(event)
            print(list(number_of_events.index))
            print(list(number_of_events.index).index(event))
            sorted_bar_color_list.append(color_palette[list(number_of_events.index).index(event) % len(color_palette) - 1])


        x_axis = list(number_of_events.index)
        y_axis = number_of_events[grouped_by].values

    else:
        x_axis = []
        y_axis = []

    number_of_events_figure = {
        'data': [{'labels': x_axis,
                  'values': y_axis,
                  'type': 'pie',
                  'marker': {'colors': sorted_bar_color_list},
                  }],
        'layout': {
            'legend': {'x': 1.05, 'y': 1.0}
        }
    }
    return number_of_events_figure


def add_representation_value(events_df):
    sorted_df = events_df.sort_values(by='source')

    named_groups = sorted_df.groupby('name', sort=False).groups.keys()

    offset_list = list()
    offset = 0

    for name_group in named_groups:
        event_source = list(events_df.loc[events_df['name'] == name_group].source)[0]

        if event_source not in offset_list:
            offset_list.append(event_source)
            offset += 1

        events_df.loc[events_df['name'] == name_group, 'repr_value'] = list(named_groups).index(name_group) + offset

    return events_df


def create_sequence_diagram(kafka_events):
    data = list()
    events_df = pd.DataFrame(kafka_events)
    if not kafka_events:
        fig = create_sequence_diagram_figure(data, events_df)
        return fig
    else:
        events_df = add_representation_value(events_df)
        print('#####')
        correlation_groups = events_df.groupby('correlationId').groups.keys()

        for correlation_group in correlation_groups:
            group_index_list = list(events_df.groupby('correlationId').groups[correlation_group])

            trace_name = events_df.loc[group_index_list]['name'].tolist()[0] + '_' + \
                         events_df.loc[group_index_list]['timestamp'].tolist()[0]

            trace_color = color_palette[group_index_list[0] % len(color_palette) - 1]

            print('creating trace for ' + trace_name + ' and color ' + trace_color)

            y_list, x_list = (list(t) for t in zip(*sorted(zip(events_df.loc[group_index_list].index.tolist(),
                                                               events_df.loc[group_index_list][
                                                                   'repr_value'].tolist()))))

            trace_high = go.Scatter(
                y=y_list,
                x=x_list,
                name=trace_name,
                line=dict(width=6, color=trace_color),
                marker=dict(
                    size=10,
                    color=trace_color,
                    line=dict(
                        width=2,
                        color='rgb(0, 0, 0)'
                    )
                ),
                opacity=0.8)
            data.append(trace_high)

        fig = create_sequence_diagram_figure(data, events_df)
        return fig


def create_sequence_diagram_figure(data, events_df):
    df = events_df

    grid_with = 2

    if 'name' in df:
        grid_with = (200 - len(df.source.tolist()) * 3) * math.log10(len(df.source.tolist()))

    if df.empty:
        tick_values = [10]
        tick_texts = ['no events']
    else:
        print()
        tick_values = df.repr_value.tolist()
        print('--------------------')
        tick_texts = [s + '.' + n for s, n in list(zip(df.source.tolist(), df.name.tolist()))]

    layout = dict(
        xaxis=dict(zeroline=False,
                   side='top',
                   showline=True,
                   tickmode='array',
                   tickvals=tick_values,
                   ticktext=tick_texts,
                   tickangle=10,
                   ticklen=4,
                   mirror=True,
                   showgrid=True,
                   gridcolor='#bdbdbd',
                   gridwidth=grid_with,
                   zerolinecolor='#969696',
                   zerolinewidth=4,
                   linecolor='#636363',
                   linewidth=6,
                   automargin='true'
                   ),
        yaxis=dict(
            automargin=True,
            autorange='reversed',
            type='scale'),
        margin=dict(l=250, r=100),
        height=1200,
    )
    fig = dict(data=data, layout=layout)
    return fig


def create_event_timeseries(kafka_events):
    data = list()
    print('\n\n\n############################## timeseries \n\n\n')

    if not kafka_events:
        fig = creature_figure(data, pd.DataFrame())
        return fig
    else:
        events_df = pd.DataFrame(kafka_events)
        events_df = add_representation_value(events_df)
        events_df.loc[events_df['name'] == events_df['repr_value'], 'repr_value'] = -1

        correlation_groups = events_df.groupby('correlationId').groups.keys()

        for correlation_group in correlation_groups:
            group_index_list = list(events_df.groupby('correlationId').groups[correlation_group])

            event_color_map = dict()

            trace_name = events_df.loc[group_index_list]['name'].tolist()[0]
            trace_color = color_palette[group_index_list[0] % len(color_palette) - 1]

            trace_high = go.Scatter(
                x=events_df.loc[group_index_list]['timestamp'].tolist(),
                y=events_df.loc[group_index_list]['repr_value'].tolist(),
                name=trace_name,
                line=dict(width=4, color=trace_color),
                marker=dict(
                    size=12,
                    color=list(event_color_map.values()),
                    line=dict(
                        width=2,
                        color='rgb(0, 0, 0)'
                    )
                ),
                opacity=0.8)
            data.append(trace_high)
            # print(trace_high)
        fig = creature_figure(data, events_df)
        return fig


def creature_figure(data, events_df):
    if events_df.empty:
        # create column names to avoid null pointer in events_df
        events_df['name'] = None
        events_df['repr_value'] = None

    layout = dict(
        title='Events Time Series',
        xaxis=dict(
            rangeselector=dict(
                id='hello',
                buttons=list([
                    dict(count=1,
                         label='10s',
                         step='second',
                         stepmode='backward'),
                    dict(count=1,
                         label='1m',
                         step='minute',
                         stepmode='backward'),
                    dict(count=10,
                         label='10m',
                         step='minute',
                         stepmode='backward'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(height=200),
            type='date'
        ),
        yaxis=dict(tickvals=events_df.repr_value.tolist(),
                   ticktext=events_df['name'].tolist()),
        margin=dict(l=250, r=100),
        height=800,
    )
    fig = dict(data=data, layout=layout)
    return fig


def create_events_table(events_df):
    table_df = events_df
    # make sure valid is always the first column
    sorted_columns = ['valid']
    additional_columns = list(set(list(table_df.columns)) - set(sorted_columns))
    table_columns = list(table_df.columns)
    table_columns.remove(sorted_columns[0])
    sorted_columns.extend(table_columns)
    # tmp = list(set(sorted_columns))
    # check if one of the columns contains a dictionary
    list_of_dicts = table_df.to_dict(orient='records')
    # only checking for the first row
    for column, value in list_of_dicts[0].items():
        if isinstance(value, dict):
            # value is a dictionary and  needs to parsed to string in order to display it in the table
            table_df[column] = table_df[column].apply(str)

    # apply sortation to dataframe
    table_df = table_df[sorted_columns]
    return table_df


def create_tooltips(validation_messages):

    tooltips = []

    for validation_message in validation_messages:
        tooltips.append(
            {'valid': validation_message}
        )

    return tooltips
