import json
import jsonschema
from jsonschema import validate
import pandas as pd
import logging


def apply_validate_events_against_schema(events_df, event_schema_map):
    """
    function to validate an event against a schema
    first checks if event is valid against chema, then if its payload has a schema and is valid
    row based
    :param events_df:
    :return: pd.series(<-1||0 || 1>, <validation message>)
    """
    logging.error('apply validating event')
    events_df.dropna(inplace=True)
    event_as_json = events_df.to_json()

    print(event_schema_map)

    if not event_schema_map:
        return pd.Series([0, 'no payload schema available'])

    try:
        if any(events_df['name'] in event_schema['name'] for event_schema in event_schema_map):
            print('found schema for ' + events_df['name'])
            event_schemas = [event_schema['schema'] for event_schema in event_schema_map if events_df['name'] == event_schema['name']]

            for event_schema in event_schemas:
                validate(json.loads(event_as_json), event_schema)

        else:
            print('no schema exists for event ' + events_df['name'])
            return pd.Series([0, 'no payload schema available'])

    except jsonschema.exceptions.ValidationError as ve:
        print("Record #{}: ERROR\n".format(events_df['name']))
        print(ve)
        return pd.Series([-1, ve.message])

    return pd.Series([1, 'valid'])


def select_events_which_are_not_valid(events_df, event_schema):
    """
    :param events_df:
    :return: list of integers representing if valid and list of descriptions
    """
    result = events_df.apply(apply_validate_events_against_schema, event_schema_map=event_schema, axis=1)

    if not result.empty:
        return result[0].tolist(), result[1].tolist()
    else:
        return [], []
