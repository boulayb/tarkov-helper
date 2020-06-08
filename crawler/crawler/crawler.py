# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from settings import *

import loot
import medical
import price


# format the crawled data to Elasticsearch bulk format 
# {'index': {'_index': 'tarkov', '_type': 'loot', '_id': item_name}}
# {'name': item_name, 'description': item_description, etc...}
def to_es_bulk_format(data):
    bulk = []

    for obj_name, obj in data.items():
        index = {'index': {'_index': CONST_ES_INDEX, '_type': CONST_ES_TYPE, '_id': obj_name}}
        document = obj
        bulk.append(index)
        bulk.append(document)
    
    return bulk


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
        # format to es bulk format
        logger.info("Formating to bulk format")
        bulk_data = to_es_bulk_format(data)

        # send to elasticsearch
        logger.info("Sending to elasticsearch")
        es = Elasticsearch(hosts=[{"host":'elasticsearch'}])
        if es.indices.exists(index=CONST_ES_INDEX) is False:
            es.indices.create(index=CONST_ES_INDEX)
        es.bulk(index=CONST_ES_INDEX, body=bulk_data)

    logger.info("Done!")

    # close log handle
    log_hdlr.close()
    logger.removeHandler(log_hdlr)


if __name__ == "__main__":
    main()
