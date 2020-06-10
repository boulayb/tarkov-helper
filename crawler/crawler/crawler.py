# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from settings import *

import loot
import medical
import price


# format the crawled data to ES bulk format
def format_to_bulk(data):
    bulk_data_list = []
    for item_name, item in data.items():
        bulk_data = {
            '_index': CONST_ES_INDEX,
            '_type': CONST_ES_TYPE,
            '_id': item_name
        }
        bulk_data.update(item)
        bulk_data_list.append(bulk_data)
    return bulk_data_list


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
        bulk_success, bulk_failed = bulk(es, format_to_bulk(data))
        logger.info("Bulk ended with " + str(bulk_success) + " success and " + str(bulk_failed))

    logger.info("Done!")

    # close log handle
    log_hdlr.close()
    logger.removeHandler(log_hdlr)


if __name__ == "__main__":
    main()
