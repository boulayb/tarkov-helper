# -*- coding: utf-8 -*-

from settings import *


# search item in ES by name and return a list of found items
def search_item(item, res_size=CONST_ES_RESULT_SIZE, scroll_time='0s', advanced=False):
    logger.info("Searching for item: '" + item + "' with params size: '" + str(res_size) + "' scroll: '" + scroll_time + "' advanced: '" + str(advanced) + "'")

    items = []
    total = 0

    # https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html
    try:
        if advanced is True:
            search = es.search(body={"query": {"query_string": {"default_field": "name", "query": item}}}, index=CONST_ES_INDEX, size=res_size, scroll=scroll_time)                  # for an advanced search, let the user build the query string
        elif ' ' in item:
            search = es.search(body={"query": {"query_string": {"default_field": "name", "query": "\"" + item + "\""}}}, index=CONST_ES_INDEX, size=res_size, scroll=scroll_time)    # for a full sentence, search with double quotes
        else:
            search = es.search(body={"query": {"query_string": {"default_field": "name", "query": "*" + item + "*"}}}, index=CONST_ES_INDEX, size=res_size, scroll=scroll_time)      # for a single word, search with wildcards

        total = search['hits']['total']
        if total > 0:
            for hit in search['hits']['hits']:
                items.append(hit['_source'])
    except Exception as e:
        logger.info("Warning: Elasticsearch failed to search query: " + item)
        search = {}
        items = [e]
        total = -1  # error code

    if '_scroll_id' in search:
        result = {'total': total, 'items': items, 'scroll_id': search['_scroll_id']}
    else:
        result = {'total': total, 'items': items}

    logger.info("Found " + str(total) + " items, returning " + str(len(items)))
    return result


# scroll scroll_id in ES and return a list of found items
def scroll_item(scroll_id, scroll_time='0s'):
    logger.info("Scrolling with scroll id: '" + scroll_id + "' and scroll time: '" + scroll_time + "'")

    items = []
    total = 0

    try:
        search = es.scroll(scroll_id=scroll_id, scroll=scroll_time)

        total = search['hits']['total']
        if total > 0:
            for hit in search['hits']['hits']:
                items.append(hit['_source'])
    except:
        logger.info("Warning: Elasticsearch failed to scroll query: " + scroll_id)

    if '_scroll_id' in search:
        result = {'total': total, 'items': items, 'scroll_id': search['_scroll_id']}
    else:
        result = {'total': total, 'items': items}

    logger.info("Scrolled " + str(total) + " items, returning " + str(len(items)))
    return result
