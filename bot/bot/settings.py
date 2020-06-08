# -*- coding: utf-8 -*-

from elasticsearch import Elasticsearch

import discord
import logging

CONST_ES_RESULT_SIZE = 3
CONST_ES_INDEX = "tarkov-helper"

CONST_MEDICAL_IMAGE = "https://gamepedia.cursecdn.com/escapefromtarkov_gamepedia/0/0b/Visual_guide_to_Healing_items_by_-u-MadWookieX.png"
CONST_INJECTOR_IMAGE = "https://gamepedia.cursecdn.com/escapefromtarkov_gamepedia/6/68/Injectors_Visual_Guide_by_-u-MadWookieX.png"


def init():

    global log_hdlr
    global logger
    global es
    global client

    client = discord.Client()

    es = Elasticsearch(hosts=[{"host":'elasticsearch'}])

    # logs init
    logging.basicConfig(level=logging.INFO, filemode='w')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt='%(asctime)s :: %(levelname)s :: %(message)s')
    log_hdlr = logging.FileHandler("./logs_bot.txt")
    log_hdlr.setFormatter(formatter)
    logger.addHandler(log_hdlr)


init()
