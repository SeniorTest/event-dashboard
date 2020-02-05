import json
import random
import pytest
from src import es_handler


@pytest.fixture()
def es_cleared():
    # setup
    es = es_handler.connect_elasticsearch()

    es.indices.delete(index='test_index', ignore=[400, 404])
    yield
    # cleanup after test execution
    es.indices.delete(index='test_index', ignore=[400, 404])



@pytest.fixture
def es_with_events():
    # setup
    es = es_handler.connect_elasticsearch()

    es.indices.delete(index='test_index', ignore=[400, 404])

    files = [
        'happy_path.json',
    ]

    file = files[random.randint(0, len(files) - 1)]
    print('----> using file ' + file)
    kafka_events = json.load(open(file))
    # when
    for kafka_event in kafka_events:
        assert es_handler.store_record(es, 'test_index', kafka_event), 'unable to store event'
    yield
    # teardown
    es.indices.delete(index='test_index', ignore=[400, 404])
