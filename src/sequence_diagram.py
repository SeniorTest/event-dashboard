import json
import glob
import os
import time
from subprocess import call


def create_sequence_diagram(events_df, event_schema_map):
    output = """
    @startuml

    skinparam ParticipantFontSize 18
    skinparam DatabaseFontSize 18
    skinparam ArrowFontSize 18

    participant Kafka

    """

    print([event_schema['target'] for event_schema in event_schema_map if 'target' in event_schema])

    unique_participants = set([event_schema['target'] for event_schema in event_schema_map if
                               'target' in event_schema] + events_df.source.unique().tolist())

    print(unique_participants)

    # create participant section
    for participant in unique_participants:

        if participant in events_df['source'].tolist():

            output += 'participant "' + participant + '"\n'

    print(output)

    # if event name is in event_schemap_map create an arrow from event source to event_schema_map.target
    for index, row in events_df.iterrows():
        if any(row['name'] in event_schema['name'] for event_schema in event_schema_map):
            event_targets = [event_schema for event_schema in event_schema_map if row['name'] == event_schema['name']]
            event_target_names = [event_schema['target'] for event_schema in event_schema_map if row['name'] == event_schema['name']]

            print('---')
            print(event_targets)
            print(event_target_names)

            for event_target in list(set(event_target_names)):
                output += create_arrow(event_target, row)

        elif 'AdaptoMetricsCalculated' == row['name']:
            continue
        else:
            output += create_arrow('Kafka', row)

    print('\n--------------')

    output += '\n@enduml'

    filename = 'msc_' + str(time.time()) + '.txt'

    with open(os.path.join('assets/images/', filename), 'a') as file:
        file.write('assets/images/' + output)

    print(os.path.join('assets/images/', filename))

    call(['java', '-DPLANTUML_LIMIT_SIZE=8192', '-jar', 'plantuml.jar', os.path.join('assets/images/', filename)])

    list_of_files = glob.glob('assets/images/msc_*.png')
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


def create_arrow(destination, row):
    event_arrow = '\n"' + row['source'] + '" -> "' + destination +'": ' + row[
        'name'] + ' \\n\\\n'

    if isinstance(row['payload'], str):
        json_acceptable_string = row['payload'].replace("'", "\"")
        event_payload = json.loads(json_acceptable_string)
    elif isinstance(row['metrics'], str):
        json_acceptable_string = row['metrics'].replace("'", "\"")
        event_payload = json.loads(json_acceptable_string)
    else:
        event_payload = row['payload']

    for payload_key, payload_value in event_payload.items():
        print(payload_key)
        print(payload_value)
        event_arrow += '\\t' + payload_key + ': ' + str(payload_value) + ' \\n\\\n'

    print(event_arrow)
    return event_arrow
