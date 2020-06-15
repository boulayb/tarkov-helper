# -*- coding: utf-8 -*-

from settings import *


# search index in ES and return a list of found items
def search_item(index, res_size=CONST_ES_RESULT_SIZE, scroll_time='0s'):
    logger.info("Searching for all item in index: '" + str(CONST_ES_RESULT_SIZE) + "' with params size: '" + str(res_size) + "' scroll: '" + scroll_time + "'")

    items = []
    total = 0

    try:
        search = es.search(body={"query": {"match_all": {}}}, index=index, size=res_size, scroll=scroll_time)    # get all documents

        total = search['hits']['total']
        if total > 0:
            for hit in search['hits']['hits']:
                items.append(hit['_source'])
    except Exception as e:
        logger.info("Warning: Elasticsearch failed to search index: " + CONST_ES_RESULT_SIZE)
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
