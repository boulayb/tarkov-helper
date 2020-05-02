# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from argparse import ArgumentParser
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

import json
import requests
import logging
import itertools

CONST_BASE_URL = "https://escapefromtarkov.gamepedia.com"
CONST_LOOT_GOBLIN = "https://eft-loot.com/page-data/index/page-data.json"
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

    # get the item details table
    item_details_table = item_soup.find(id='va-infobox0-content') # should be unique

    # get the item icon
    try:
        item_icon = item_soup.find('td', {'class': 'va-infobox-icon'}).find('img')['src']
        if item_icon is not None and item_icon != "" and item_icon != "\n":
            logger.info("Icon found")
            icon = item_icon
        else:
            raise Exception
    except:
        logger.info("Warning: Icon not found for loot item " + item_url)
        icon = ""

    # get the item weight
    try:
        item_weight = item_details_table.find(text="Weight").parent.parent.find('td', {'class': 'va-infobox-content'}).getText()
        if item_weight is not None and item_weight != "" and item_weight != "\n":
            logger.info("Weight found")
            weight = item_weight
        else:
            raise Exception
    except:
        logger.info("Warning: Weight not found for loot item " + item_url)
        weight = "Not found"

    # get the item size
    try:
        item_size = item_details_table.find(text="Grid size").parent.parent.find('td', {'class': 'va-infobox-content'}).getText()
        if item_size is not None and item_size != "" and item_size != "\n":
            logger.info("Size found")
            size = item_size
        else:
            raise Exception
    except:
        logger.info("Warning: Size not found for loot item " + item_url)
        size = "Not found"

    # get the item exp
    try:
        item_exp = item_details_table.find(text="Loot experience").parent.parent.find('td', {'class': 'va-infobox-content'}).getText()
        if item_exp is not None and item_exp != "" and item_exp != "\n":
            logger.info("Exp found")
            exp = item_exp
        else:
            raise Exception
    except:
        logger.info("Warning: Exp not found for loot item " + item_url)
        exp = "Not found"

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
        name = "No name found"

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
        description = "No description found"

    item_data['name'] = name
    item_data['icon'] = icon
    item_data['weight'] = weight
    item_data['size'] = size
    item_data['exp'] = exp
    item_data['description'] = description
    item_data['url'] = CONST_BASE_URL + item_url

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


### TODO: add arguments parsing

# result dict
logger.info("Crawling")
data = {}
data['loot'] = crawl_loot()

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

# close log handle
hdlr.close()
logger.removeHandler(hdlr)
