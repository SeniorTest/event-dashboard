# internal imports
import uuid
import time

# external imports
import requests

# own imports
from src import es_handler

uri = 'http://localhost:9200'


def test_raw_es_connection_availability():
    response = requests.get(uri)
    print(response.content)
    assert response.status_code == 200, 'unable to connect to elasticsearch'


def test_es_connection_availability():
    es = es_handler.connect_elasticsearch()
    print(es)
    assert es is not None, 'unable to connect to elasticsearch using imported module'


def test_create_index():
    # given
    es = es_handler.connect_elasticsearch()
    assert es
    # when
    assert es_handler.create_index(es)
    # then
    response = requests.get(uri + '/events/_mappings')
    print(response.text)
    assert response.text


def test_put_event():
    # given
    unique_event_name = str(uuid.uuid4())
    test_event = {
        'name': unique_event_name,
        'id': 123,
        'payload': {
            'orderId': 'abc123',
            'arrayTypePayload': [
                1, 2, 3
            ]
        }
    }

    es = es_handler.connect_elasticsearch()
    assert es

    # when
    assert es_handler.store_record(es, 'test_event', test_event)
    time.sleep(1)
    # then
    search_object = {'query': {'match' : {'name': unique_event_name}}}
    response = es_handler.search(es_object=es, index_name="test_event", search=search_object)
    assert response, 'no events found'
    assert len(response) == 1, 'too many events found'
    assert response[0] == test_event, 'event does not match expected event'


def test_get_all():
    # given
    es = es_handler.connect_elasticsearch()
    assert es
    # when
    all_events = es_handler.get_all(es, 'events')
    # then
    assert all_events


def test_search():
    # given
    es = es_handler.connect_elasticsearch()
    assert es
    # when
    search_object = {'query': {'match': {'name': 'bla_1'}}}
    all_events = es_handler.search(es_object=es, index_name="events", search=search_object)
    # then
    print('-----')
    for event in all_events:
        print(event)
    assert all_events