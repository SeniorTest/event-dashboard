import random
import uuid
from datetime import datetime
from src import es_handler

index = 'test_index_3'
possible_sources = ['Service1', 'Service2', 'Service3', 'Service4']
possible_names = ['EventName1', 'EventName2', 'EventName3', 'EventName4']
possible_correlation_ids = [
    'c506484c-e5d6-4067-b38f-5eb52b6f68ce', 'fe2f5fd2-a721-4903-bced-b27cd27af039',
    '339c7de6-cf0d-40c2-ab5b-9548283ce13e', '2fd46da5-66e2-423c-9435-91b220000ed9',
    '6d442b9f-3804-46e9-befc-ba8b0c4bd5ec', 'f635b8ce-dbeb-46e3-a4ff-440960944cb3',
    str(uuid.uuid4())]


def test_add_event():
    # given
    es = es_handler.connect_elasticsearch('127.0.0.1')
    assert es

    test_event = {
        "id": str(uuid.uuid4()),
        "source": random.choice(possible_sources),
        "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
        "name": random.choice(possible_names),
        "correlationId": random.choice(possible_correlation_ids),
        "causationId": str(uuid.uuid4()),
        "nestedObject": {
            "nestedProperty1": str(uuid.uuid4()),
            "nestedProperty2": "565b709b-f2d2-4148-a358-fa812899e346"
        }
    }
    # when, then
    assert es_handler.store_record(es, index, test_event), 'unable to store event'
