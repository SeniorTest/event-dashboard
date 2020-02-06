import random
import uuid
from datetime import datetime
from src import es_handler


index = 'test_index_3'
possible_sources = ['Service1', 'Service2', 'Service3', 'Service4']
possible_names = ['EventName1', 'EventName2', 'EventName3', 'EventName4']


def test_add_event():
    # given
    es = es_handler.connect_elasticsearch()
    assert es

    test_event = {
        "id": str(uuid.uuid4()),
        "source": random.choice(possible_sources),
        "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
        "name": random.choice(possible_names),
        "correlationId": str(uuid.uuid4()),
        "causationId": str(uuid.uuid4()),
        "payload": {
            "nestedProperty1": str(uuid.uuid4()),
            "nestedProperty2": "565b709b-f2d2-4148-a358-fa812899e346"
        }
    }

    assert es_handler.store_record(es, index, test_event), 'unable to store event'
