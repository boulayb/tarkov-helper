# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from settings import *

import loot
import medical
import provision
import price


# format the crawled data to ES bulk format
def format_to_bulk(data, index):
    bulk_data_list = []
    for item_name, item in data.items():
        bulk_data = {
            '_index': index,
            '_type': index,
            '_id': item_name
        }
        bulk_data.update(item)
        bulk_data_list.append(bulk_data)
    return bulk_data_list


# send data to elasticsearch in index
def send_to_es(es, data, index):
    if reset_index is True and es.indices.exists(index=index):
        es.indices.delete(index=index)
        es.indices.create(index=index)
    elif es.indices.exists(index=index) is False:
        es.indices.create(index=index)
    bulk_success, bulk_failed = bulk(es, format_to_bulk(data, index))
    logger.info("Bulk ended with " + str(bulk_success) + " success and " + str(bulk_failed))


def main():

    items = None
    images = None

    # crawl items from the wiki
    if crawl_loot is True:
        logger.info("Crawling items")

        items = {}
        items.update(loot.crawl_category())
        items.update(medical.crawl_category())
        items.update(provision.crawl_category())

        # item prices from tarkov market
        ### TODO: separate price crawl from loot crawl and cron it every one or two hours
        if crawl_prices is True:
            logger.info("Crawling prices")
            items = price.crawl_prices_tarkov_market(items)

    # crawl images from the wiki
    # if crawl_images is True:
    #     logger.info("Crawling images")

    #     images = {}
    #     images.update(medical.crawl_images())

    # send data to elasticsearch
    if use_elasticsearch is True:
        logger.info("Sending to elasticsearch")

        es = Elasticsearch(hosts=[{"host":'elasticsearch'}])
        if items:
            send_to_es(es, items, CONST_ES_ITEM_INDEX)
        if images:
            send_to_es(es, images, CONST_ES_IMAGE_INDEX)

    logger.info("Done!")

    # close log handle
    log_hdlr.close()
    logger.removeHandler(log_hdlr)


if __name__ == "__main__":
    main()
