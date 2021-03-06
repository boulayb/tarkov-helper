# -*- coding: utf-8 -*-

from elasticsearch import Elasticsearch
from argparse import ArgumentParser

import logging

CONST_SELENIUM_DELAY = 1
CONST_ES_RESULT_SIZE = 3
CONST_ES_ITEM_INDEX = "tarkov-items"
CONST_ES_IMAGE_INDEX = "tarkov-images"
CONST_SCREENSHOTS_FOLDER = "crawler/screenshots"

CONST_SERVER_URL = "http://vps-31da28b6.vps.ovh.net/"
CONST_BASE_URL = "https://escapefromtarkov.gamepedia.com"
CONST_LOOT_GOBLIN = "https://eft-loot.com/page-data/index/page-data.json"
CONST_TARKOV_MARKET = "https://tarkov-market.com/"
CONST_TARKOV_MARKET_ITEMS = "https://tarkov-market.com/api/items?lang=en&search=&tag=&sort=&sort_direction=&skip=&limit=-1"

CONST_EFFECT_LIST = ['Bloodloss', 'Fresh Wound', 'Restores HP', 'Pain', 'On Painkillers', 'Contusion', 'Fracture']

CONST_LOOT_PAGE = "/Loot"
CONST_MEDICAL_PAGE = "/Medical"
CONST_PROVISION_PAGE = "/Provisions"
CONST_CONTAINER_PAGE = "/Containers"
CONST_EYEWEAR_PAGE = "/Eyewear"
CONST_ARMBAND_PAGE = "/Armbands"
CONST_POUCH_PAGE = "/Secure_containers"
CONST_HEADWEAR_PAGE = "/Headwear"
CONST_FACEWEAR_PAGE = "/Face_cover"
CONST_HEADSET_PAGE = "/Headsets"
CONST_HEADGEAR_PAGE = "/Gear_components"
CONST_BACKPACK_PAGE = "/Backpacks"
CONST_CHESTRIG_PAGE = "/Chest_rigs"
CONST_ARMOR_PAGE = "/Armor_vests"
CONST_KEYS_PAGE = "/Keys_%26_Intel"


def init():

    global log_hdlr
    global logger
    global use_elasticsearch
    global crawl_prices
    global crawl_loot
    global crawl_images
    global take_screenshots
    global reset_index
    global es

    # parse arguments
    parser = ArgumentParser('tarkov-helper_crawler')
    parser.add_argument('-es', '--elasticsearch', dest='use_elasticsearch', action='store_true', help='Push results into Elasticsearch.')
    parser.add_argument('-l', '--loot', dest='crawl_loot', action='store_true', help='Crawl items on the wiki.')
    parser.add_argument('-p', '--prices', dest='crawl_prices', action='store_true', help='Crawl prices from Tarkov-Market / Loot Goblin.')
    parser.add_argument('-s', '--screenshots', dest='take_screenshots', action='store_true', help='Use Selenium webdriver to take screenshots.')
    parser.add_argument('-i', '--images', dest='crawl_images', action='store_true', help='Crawl images (map, cheat sheet...) on the wiki.')
    parser.add_argument('-r', '--reset', dest='reset_index', action='store_true', help='Destroy and recreate the ES index.')
    parser.set_defaults(use_elasticsearch=False)
    parser.set_defaults(crawl_prices=False)
    parser.set_defaults(crawl_loot=False)
    parser.set_defaults(crawl_images=False)
    parser.set_defaults(take_screenshots=False)
    parser.set_defaults(reset_index=False)
    args = parser.parse_args()

    use_elasticsearch = args.use_elasticsearch
    crawl_prices = args.crawl_prices
    crawl_loot = args.crawl_loot
    crawl_images = args.crawl_images
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

    es = Elasticsearch(hosts=[{"host":'elasticsearch'}])


init()
