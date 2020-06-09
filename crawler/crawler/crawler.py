# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from settings import *

import loot
import medical
import price


def test_bulk_2(data):
    bulk_data = []
    for obj_name, obj in data.items():
        obj.update({
            '_index': CONST_ES_INDEX,
            '_type': CONST_ES_TYPE,
            '_id': obj_name
        })
        bulk_data.append(obj)
    return bulk_data

def test_bulk(data):
    for doc in data:
        yield {
            "_index": CONST_ES_INDEX,
            "_type": CONST_ES_TYPE,
            "doc": doc
        }


# format the crawled data to Elasticsearch bulk format and send it by batch to prevent oversized bulk
def send_bulk_by_batch(es, data, batch_size):
    i = 0
    bulk_data = []
    for obj_name, obj in data.items():
        index = {'index': {'_index': CONST_ES_INDEX, '_type': CONST_ES_TYPE, '_id': obj_name}}
        document = obj
        bulk_data.append(index)
        bulk_data.append(document)
        i += 1
        if i == batch_size:
            es.bulk(index=CONST_ES_INDEX, body=bulk_data)
            i = 0
            bulk_data = []
    if len(bulk_data) > 0:
        es.bulk(index=CONST_ES_INDEX, body=bulk_data)


def main():

    # result dict
    logger.info("Crawling")
    data = {}
    data.update(loot.crawl_category())
    data.update(medical.crawl_category())

    if crawl_prices is True:
        # item prices from tarkov market
        data = price.crawl_prices_tarkov_market(data)

    if use_elasticsearch is True:
        # send to elasticsearch
        logger.info("Sending to elasticsearch")
        es = Elasticsearch(hosts=[{"host":'elasticsearch'}])
        if reset_index is True and es.indices.exists(index=CONST_ES_INDEX):
            es.indices.delete(index=CONST_ES_INDEX)
            es.indices.create(index=CONST_ES_INDEX)
        elif es.indices.exists(index=CONST_ES_INDEX) is False:
            es.indices.create(index=CONST_ES_INDEX)
        print(bulk(es, test_bulk_2(data)))
        # send_bulk_by_batch(es, data, 100)

    logger.info("Done!")

    # close log handle
    log_hdlr.close()
    logger.removeHandler(log_hdlr)


if __name__ == "__main__":
    main()
