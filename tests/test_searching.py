import time
from src import es_handler


def test_search_by_date_range(es_with_events):
    # given
    es = es_handler.connect_elasticsearch()
    assert es
    # sleep is required, otherwise the query result is empty
    time.sleep(1)
    # when
    search_object = {"query": {
        "range": {"timestamp": {"gte": "2019-01-01T02:36:53.510Z", "lt": "2019-01-01T02:36:58.510Z"}}
    }}
    #     "bool": {
    #         "must": {
    #             "range": {"timestamp": {"gte": "2019-01-01T02:36:53.510Z", "lte": "2019-01-01T02:36:58.510Z"}}
    #         },
    #
    #         # "must": {
    #         #     "query_string": {
    #         #         "query": "timestamp",
    #         #         "default_operator": "AND"
    #         #     }
    #         # }
    #
    #     }
    # }}
    all_events = es_handler.search(es_object=es, index_name="test_index", search=search_object)
    # then
    print('-----')
    print(all_events)

    for event in all_events:
        print()
        print(event)
    assert all_events
    assert 5 == len(all_events)
