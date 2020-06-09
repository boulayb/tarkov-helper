# -*- coding: utf-8 -*-

from argparse import ArgumentParser

import logging

CONST_SELENIUM_DELAY = 1
CONST_ES_INDEX = "tarkov-helper"
CONST_ES_TYPE = "tarkov"
CONST_SCREENSHOTS_FOLDER = "crawler/screenshots"

CONST_SERVER_URL = "http://vps-31da28b6.vps.ovh.net/"
CONST_BASE_URL = "https://escapefromtarkov.gamepedia.com"
CONST_LOOT_GOBLIN = "https://eft-loot.com/page-data/index/page-data.json"
CONST_TARKOV_MARKET = "https://tarkov-market.com/"
CONST_TARKOV_MARKET_ITEMS = "https://tarkov-market.com/api/items?lang=en&search=&tag=&sort=&sort_direction=&skip=&limit=-1"

CONST_LOOT_PAGE = "/Loot"
CONST_MEDICAL_PAGE = "/Medical"


def init():

    global log_hdlr
    global logger
    global use_elasticsearch
    global crawl_prices
    global take_screenshots
    global reset_index

    # parse arguments
    parser = ArgumentParser('tarkov-helper_crawler')
    parser.add_argument('-es', '--elasticsearch', dest='use_elasticsearch', action='store_true', help='Push results into Elasticsearch.')
    parser.add_argument('-p', '--prices', dest='crawl_prices', action='store_true', help='Crawl prices from Tarkov-Market / Loot Goblin.')
    parser.add_argument('-s', '--screenshots', dest='take_screenshots', action='store_true', help='Use Selenium webdriver to take screenshots.')
    parser.add_argument('-r', '--reset', dest='reset_index', action='store_true', help='Destroy and recreate the ES index.')
    parser.set_defaults(use_elasticsearch=False)
    parser.set_defaults(crawl_prices=False)
    parser.set_defaults(take_screenshots=False)
    parser.set_defaults(reset_index=False)
    args = parser.parse_args()

    use_elasticsearch = args.use_elasticsearch
    crawl_prices = args.crawl_prices
    take_screenshots = args.take_screenshots
    reset_index = args.reset_index

    # logs init
    logging.basicConfig(level=logging.INFO, filemode='w')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt='%(asctime)s :: %(levelname)s :: %(message)s')
    log_hdlr = logging.FileHandler("./logs_crawler.txt")
    log_hdlr.setFormatter(formatter)
    logger.addHandler(log_hdlr)


init()
