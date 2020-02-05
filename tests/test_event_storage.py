import json
import random
import time
from src import es_handler


def test_storing_events(es_cleared):
    # given
    es = es_handler.connect_elasticsearch()
    assert es

    files = [
        'events.json',
    ]

    file = files[random.randint(0, len(files) - 1)]
    print('----> using file ' + file)
    kafka_events = json.load(open(file))
    print(kafka_events)
    # when
    for kafka_event in kafka_events:
        assert es_handler.store_record(es, 'test_index', kafka_event), 'unable to store event'
    # then
    time.sleep(1)
    all_events = es_handler.get_all(es, 'test_index')
    assert len(kafka_events) == len(all_events)


def test_initial_events():
    # given
    es = es_handler.connect_elasticsearch()
    assert es

    files = [
        'events.json',
    ]

    file = files[random.randint(0, len(files) - 1)]
    print('----> using file ' + file)
    kafka_events = json.load(open(file))
    print(kafka_events)
    # when
    for kafka_event in kafka_events:
        assert es_handler.store_record(es, 'test_index', kafka_event), 'unable to store event'
