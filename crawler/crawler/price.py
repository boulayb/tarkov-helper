# -*- coding: utf-8 -*-

import re
import json
import requests
import itertools

from settings import *

import tools


# retrieve prices from tarkov-market for each item
def crawl_prices_tarkov_market(data):
    logger.info("Getting JSON from " + CONST_TARKOV_MARKET)

    # escape the 401 first, no SimpleCookie because for some reason the 'Set-Cookie' is all fucked up
    r = requests.get(CONST_TARKOV_MARKET)   
    r.raise_for_status()
    cookies = r.headers['Set-Cookie']
    cfduid = tools.find_substring(cookies, "__cfduid=", ";")
    uid = tools.find_substring(cookies, " uid=", ";")
    token = tools.find_substring(cookies, "token=", ";")
    cookie_string = cfduid + '; ' + uid + '; ' + token
    fake_header = {"Cookie": cookie_string}

    # get the prices json
    r = requests.get(CONST_TARKOV_MARKET_ITEMS, headers=fake_header)
    r.raise_for_status()
    market_json = json.loads(r.text)
    items_list = market_json['items']

    for item in items_list:
        item_name = re.sub(' \([0-9]+\/[0-9]+\)', '', item['enName']) if 'enName' in item else None     #remove the (xx/xx) from the names
        item_price_day = int(item['avgDayPrice']) if 'avgDayPrice' in item else None
        item_price_week = int(item['avgWeekPrice']) if 'avgWeekPrice' in item else None
        item_price_slot_day = int(item['avgDayPricePerSlot']) if 'avgDayPricePerSlot' in item else None
        item_price_slot_week = int(item['avgWeekPricePerSlot']) if 'avgWeekPricePerSlot' in item else None
        item_price_change_day = int(item['change24']) if 'change24' in item else None
        item_price_change_week = int(item['change7d']) if 'change7d' in item else None
        item_trader_price = int(item['traderPrice']) if 'traderPrice' in item else None
        item_trader_name = item['traderName'] if 'traderName' in item else None
        item_price_date = item['priceUpdated'] if 'priceUpdated' in item else None
        item_is_worth_resell = True if (item_price_day and item_trader_price) and (item_price_day <= item_trader_price) else False

        if item_name in data:
            data[item_name]['price_day'] = item_price_day
            data[item_name]['price_week'] = item_price_week
            data[item_name]['price_slot_day'] = item_price_slot_day
            data[item_name]['price_slot_week'] = item_price_slot_week
            data[item_name]['price_change_day'] = item_price_change_day
            data[item_name]['price_change_week'] = item_price_change_week
            data[item_name]['resell_name'] = item_trader_name
            data[item_name]['resell_price'] = item_trader_price
            data[item_name]['price_date'] = item_price_date
            data[item_name]['worth_resell'] = item_is_worth_resell
    
    return data    


# retrieve prices from loot goblin for each item
def crawl_prices_loot_goblin(data):

    # get the prices json
    logger.info("Getting JSON from " + CONST_LOOT_GOBLIN)
    r = requests.get(CONST_LOOT_GOBLIN)
    r.raise_for_status()
    goblin_json = json.loads(r.text)
    items_list = goblin_json['result']['data']['allDataJson']['nodes']

    for item in items_list:
        item_name = item['name']
        item_price = item['price_avg']
        item_price_slot = item['price_per_slot']
        item_price_date = item['timestamp']

        if item_name in data:
            data[item_name]['price'] = item_price
            data[item_name]['price_slot'] = item_price_slot
            data[item_name]['price_date'] = item_price_date
    
    return data
