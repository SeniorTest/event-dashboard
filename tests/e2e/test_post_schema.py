# external modules
import json
import requests


def test_post_schema():
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    event_schema = [{'name': 'EventName1',
                     'target': 'Service2',  # from pact broker
                     'schema': {'$schema': 'http://json-schema.org/schema#', 'type': 'object',
                                'properties': {'id': {'type': 'string'}, 'name': {'type': 'string'},
                                               'payload': {'type': 'object',
                                                           'properties': {
                                                               'nestedProperty1': {
                                                                   'type': 'string'},
                                                               'nestedProperty2': {
                                                                   'type': 'string'}},
                                                           'required': [
                                                               'nestedProperty1',
                                                               'nestedProperty2'
                                                           ]}},
                                'required': ['id', 'name', 'payload']}},
                    {'name': 'EventName2',
                     'target': 'Service1',  # from pact broker
                     'schema': {'$schema': 'http://json-schema.org/schema#', 'type': 'object',
                                'properties': {'id': {'type': 'string'}, 'name': {'type': 'string'},
                                               'payload': {'type': 'object',
                                                           'properties': {
                                                               'nestedProperty1': {
                                                                   'type': 'string'},
                                                               'nestedProperty2': {
                                                                   'type': 'string'}},
                                                           'required': [
                                                               'nestedProperty1',
                                                               'nestedProperty2',
                                                               'nestedProperty3'
                                                           ]}},
                                'required': ['id', 'name', 'payload']}},
                    {'name': 'EventName3',
                     'target': 'Service1',  # from pact broker
                     'schema': {'$schema': 'http://json-schema.org/schema#', 'type': 'object',
                                'properties': {'id': {'type': 'string'}, 'name': {'type': 'string'},
                                               'payload': {'type': 'object',
                                                           'properties': {
                                                               'nestedProperty1': {
                                                                   'type': 'string'},
                                                               'nestedProperty2': {
                                                                   'type': 'string'}},
                                                           'required': [
                                                               'nestedProperty1',
                                                               'nestedProperty2'
                                                           ]}},
                                'required': ['id', 'name', 'payload']}}
                    ]

    r = requests.post('http://127.0.0.1:18550/kebab/api/eventSchema',
                      data=json.dumps(event_schema), headers=headers)
    assert r.status_code == 200
