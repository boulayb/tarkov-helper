# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from bs4 import BeautifulSoup
from argparse import ArgumentParser
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

import json
import logging
import requests
import itertools

import loot

CONST_BASE_URL = "https://escapefromtarkov.gamepedia.com"
CONST_LOOT_GOBLIN = "https://eft-loot.com/page-data/index/page-data.json"

# init selenium webdriver
driver = webdriver.Remote("http://webdriver:4444/wd/hub", DesiredCapabilities.FIREFOX)

# logs init
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(fmt='%(asctime)s :: %(levelname)s :: %(message)s')
hdlr = logging.FileHandler("./logs_crawler.txt")
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)


# retrieve prices from loot goblin for each item
def crawl_prices(data):

    # get the prices json
    logger.info("Getting JSON from " + CONST_LOOT_GOBLIN)
    r = requests.get(CONST_LOOT_GOBLIN)
    r.raise_for_status()
    goblin_json = json.loads(r.text)
    items_list = goblin_json['result']['data']['allDataJson']['nodes']

    logger.info("Getting prices from goblin list")
    for item in items_list:
        item_name = item['name']
        item_price = item['price_avg']
        item_price_slot = item['price_per_slot']
        item_price_date = item['timestamp']

        if item_name in data['loot']:
            data['loot'][item_name]['price'] = item_price
            data['loot'][item_name]['price_slot'] = item_price_slot
            data['loot'][item_name]['price_date'] = item_price_date
        else:
            logger.info("Warning: Price not added, no object found for item " + item_name)
    
    return data


# format the crawled data to Elasticsearch bulk format 
# {'index': {'_index': 'tarkov', '_type': 'loot', '_id': item_name}}
# {'name': item_name, 'description': item_description, etc...}
def to_es_bulk_format(data):
    bulk = []

    for category_type, category in data.items():
        for obj_type, obj in category.items():
            index = {'index': {'_index': 'tarkov', '_type': category_type, '_id': obj_type}}
            document = obj
            bulk.append(index)
            bulk.append(document)
    
    return bulk


if __name__ == "__main__":
  
    ### TODO: add arguments parsing

    # result dict
    logger.info("Crawling")
    data = {}
    data['loot'] = loot.crawl_loot()

    # item prices from loot goblin
    data = crawl_prices(data)

    # format to es bulk format
    logger.info("Formating to bulk format")
    bulk_data = to_es_bulk_format(data)

    # send to elasticsearch
    logger.info("Sending to elasticsearch")
    es = Elasticsearch(hosts=[{"host":'elasticsearch'}])
    es.bulk(index='tarkov', body=bulk_data)

    logger.info("Done!")

    # close selenium webdriver
    driver.close()

    # close log handle
    hdlr.close()
    logger.removeHandler(hdlr)
