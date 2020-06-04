# -*- coding: utf-8 -*-

# from selenium import webdriver
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import logging

CONST_ES_INDEX = "tarkov-helper"
CONST_SCREENSHOTS_FOLDER = "crawler/screenshots"
CONST_SERVER_URL = "http://vps-31da28b6.vps.ovh.net/"
CONST_BASE_URL = "https://escapefromtarkov.gamepedia.com"
CONST_LOOT_GOBLIN = "https://eft-loot.com/page-data/index/page-data.json"

CONST_LOOT_PAGE = "/Loot"


def init():

    global log_hdlr
    global logger
    # global driver

    # logs init
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt='%(asctime)s :: %(levelname)s :: %(message)s')
    log_hdlr = logging.FileHandler("./logs_crawler.txt")
    log_hdlr.setFormatter(formatter)
    logger.addHandler(log_hdlr)

    # # init selenium webdriver
    # driver = webdriver.Remote("http://webdriver:4444/wd/hub", DesiredCapabilities.FIREFOX)


init()
