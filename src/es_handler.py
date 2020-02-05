# external imports
from elasticsearch import Elasticsearch

# internal imports
import config


def connect_elasticsearch():
    _es = None
    _es = Elasticsearch([{'host': config.config['elasticsearch_url'], 'port': config.config['elasticsearch_port']}])
    if _es.ping():
        return _es
    else:
        return None


def create_index(es_object, index_name='events'):
    created = False
    # index settings
    settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            'mappings': {
                'examplecase': {
                    'properties': {
                        'address': {'index': 'not_analyzed', 'type': 'string'},
                        'date_of_birth': {'index': 'not_analyzed', 'format': 'dateOptionalTime', 'type': 'date'},
                        'some_PK': {'index': 'not_analyzed', 'type': 'string'},
                        'fave_colour': {'index': 'analyzed', 'type': 'string'},
                        'email_domain': {'index': 'not_analyzed', 'type': 'string'},
                    }}}
        }
    }
    try:
        if not es_object.indices.exists(index_name):
            # Ignore 400 means to ignore "Index Already Exist" error.
            # tmp = es_object.indices.create(index=index_name, ignore=400, body=settings)
            tmp = es_object.indices.create(index=index_name, ignore=400)
            print(tmp)
            print('Created Index')
        created = True
    except Exception as ex:
        print(str(ex))
    finally:
        return created


def store_record(elastic_object, index_name, record):
    try:
        print('creating record')
        outcome = elastic_object.index(index=index_name, doc_type='event', body=record)
        print(outcome)
        if outcome['result'] == 'created':
            return True

    except Exception as ex:
        print('Error in indexing data')
        print(str(ex))

    return False


def search(es_object, index_name, search):
    result = es_object.search(index=index_name, body=search, scroll='1m', size=1000)
    raw_events = [raw_event['_source'] for raw_event in result['hits']['hits']]
    return raw_events


def get_all(es_object, index_name):
    search_object = {'query': {'match_all': {}}}
    return search(es_object, index_name, search_object)
