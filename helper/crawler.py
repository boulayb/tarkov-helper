# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from argparse import ArgumentParser
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

import requests
import logging
import itertools

CONST_BASE_URL = "https://escapefromtarkov.gamepedia.com"
CONST_LOOT_PAGE = "/Loot"

# logs init
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(fmt='%(asctime)s :: %(levelname)s :: %(message)s')
hdlr = logging.FileHandler("./logs_crawler.txt")
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)


# crawl a single item page to retrieve infos
def crawl_loot_item(item_url):
    item_data = {}

    # get the item loot page
    logger.info("Getting HTML from " + CONST_BASE_URL + item_url)
    r = requests.get(CONST_BASE_URL + item_url)
    r.raise_for_status()

    # init beautifulsoup parser
    logger.info("Init Beautifulsoup")
    item_html = r.text
    item_soup = BeautifulSoup(item_html, 'html.parser')

    # get the item name
    try:
        item_name = item_soup.find(id='firstHeading').getText()
        if item_name is not None and item_name != "" and item_name != "\n":
            logger.info("Name found")
            name = item_name
        else:
            raise Exception
    except:
        logger.info("Warning: Name not found for loot item " + item_url)
        name = "No name found."

    # get the item description
    try:
        item_description = item_soup.find(id="Description").parent.findNext('p').getText()
        if item_description is not None and item_description != "" and item_description != "\n":
            logger.info("Description found")
            description = item_description
        else:
            raise Exception
    except:
        logger.info("Warning: Description not found for loot item " + item_url)
        description = "No description found."

    item_data['name'] = name
    item_data['description'] = description

    return item_data


# crawl each loot page from the main loot page table to get their infos
def crawl_loot():
    loot_data = {}

    # get the wiki loot page
    logger.info("Getting HTML from " + CONST_BASE_URL + CONST_LOOT_PAGE)
    r = requests.get(CONST_BASE_URL + CONST_LOOT_PAGE)
    r.raise_for_status()

    # init beautifulsoup parser
    logger.info("Init Beautifulsoup")
    loot_html = r.text
    loot_soup = BeautifulSoup(loot_html, 'html.parser')

    # get the loot table
    loot_table = loot_soup.find('table', {'class': 'wikitable'}).find_all("tr")
    logger.info("Getting loot table infos")
    for loot_item in itertools.islice(loot_table, 1, None): # each row of the table is a loot item, except first one (titles)
        loot_infos = loot_item.find_all("th")   # 0=icon, 1=name+link, 2=type, 3=notes
        loot_name = loot_infos[1].find("a")
        if loot_name is not None:
            link = loot_name['href']
            name = loot_name.getText()
            loot_data[name] = crawl_loot_item(link)

    return loot_data


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


### TODO: add arguments parsing

# result dict
logger.info("Crawling")
data = {}
data['loot'] = crawl_loot()

# format to es bulk format
logger.info("Formating to bulk format")
bulk_data = to_es_bulk_format(data)

# send to elasticsearch
logger.info("Sending to elasticsearch")
es = Elasticsearch(hosts=[{"host":'elasticsearch'}])
es.bulk(index='tarkov', body=bulk_data)

logger.info("Done!")

# close log handle
hdlr.close()
logger.removeHandler(hdlr)
