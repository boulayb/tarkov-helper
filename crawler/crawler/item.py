# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import requests

from settings import *

import getter
import tools


# screenshot the trade & craft category
def crawl_trade(items):

    try:
        for name, item in items.items():
            logger.info("Taking screenshot from " + item['url'])

            # open page via webdriver
            driver = webdriver.Remote("http://webdriver:4444/wd/hub", DesiredCapabilities.FIREFOX)
            driver.get(item['url'])

            item['trade'] = getter.get_item_trade(item['url'].replace(CONST_BASE_URL, ''), driver)

            driver.close()
    except Exception as e:
        logger.info("Warning: Failed crawling trades, reason: " + str(e))
        pass

    return items


# crawl a single item page to retrieve infos
def crawl_item(items, name, item_url):

    if name not in items:
        items[name] = {}
    items[name]['trade'] = None if 'trade' not in items[name] else items[name]['trade']
    items[name]['price_day'] = None if 'price_day' not in items[name] else items[name]['price_day']
    items[name]['price_week'] = None if 'price_week' not in items[name] else items[name]['price_week']
    items[name]['price_slot_day'] = None if 'price_slot_day' not in items[name] else items[name]['price_slot_day']
    items[name]['price_slot_week'] = None if 'price_slot_week' not in items[name] else items[name]['price_slot_week']
    items[name]['price_change_day'] = None if 'price_change_day' not in items[name] else items[name]['price_change_day']
    items[name]['price_change_week'] = None if 'price_change_week' not in items[name] else items[name]['price_change_week']
    items[name]['resell_name'] = None if 'resell_name' not in items[name] else items[name]['resell_name']
    items[name]['resell_price'] = None if 'resell_price' not in items[name] else items[name]['resell_price']
    items[name]['price_date'] = None if 'price_date' not in items[name] else items[name]['price_date']
    items[name]['worth_resell'] = False if 'worth_resell' not in items[name] else items[name]['worth_resell']

    # get the item loot page
    logger.info("Getting HTML from " + CONST_BASE_URL + item_url)
    r = requests.get(CONST_BASE_URL + item_url)
    r.raise_for_status()

    # init beautifulsoup parser
    item_html = r.text
    item_soup = BeautifulSoup(item_html, 'html.parser')

    # get the item details table
    item_details_table = item_soup.find(id='va-infobox0-content') # should be unique

    items[name]['url'] = CONST_BASE_URL + item_url
    items[name]['name'] = getter.get_item_name(item_soup, item_url)
    items[name]['icon'] = getter.get_item_icon(item_soup, item_url)
    items[name]['description'] = getter.get_item_description(item_soup, item_url)
    items[name]['type'] = getter.get_item_type(item_details_table, item_url)
    items[name]['size'] = getter.get_item_size(item_details_table, item_url)
    items[name]['total_size'] = tools.calculate_total_size(items[name]['size'])
    items[name]['weight'] = getter.get_item_weight(item_details_table, item_url)
    items[name]['exp'] = getter.get_item_exp(item_details_table, item_url)
    items[name]['time'] = getter.get_item_time(item_details_table, item_url)
    items[name]['merchant'] = getter.get_item_merchant(item_details_table, item_url)
    items[name]['locations'] = getter.get_item_locations(item_soup, item_url)
    items[name]['notes'] = getter.get_item_notes(item_soup, item_url)
    items[name]['quests'] = getter.get_item_quests(item_soup, item_url)
    items[name]['hideouts'] = getter.get_item_hideouts(item_soup, item_url)
    effects = getter.get_item_effect(item_details_table, item_url)
    items[name]['effect'] = effects['effect']
    items[name]['buff'] = effects['buff']
    items[name]['debuff'] = effects['debuff']

    # clean beautifulsoup parser and close webdriver page
    item_soup.decompose()

    return items


# crawl links to item from table
def crawl_table(items, loot_table):

    for loot_item in loot_table[1:]: # each row of the table is a loot item, except first one (titles)
        loot_infos = loot_item.find_all("th")   # 0=icon, 1=name+link, 2=type, etc...
        loot_name = loot_infos[1].find("a")
        if loot_name is not None:
            link = loot_name['href']
            name = loot_name.getText()
            items = crawl_item(items, name, link)

    return items


# crawl all links to item from the main loot page to get their infos
def crawl_category(items, url, ids_list):

    try:
        # get the wiki page
        logger.info("Getting HTML from " + CONST_BASE_URL + url)
        r = requests.get(CONST_BASE_URL + url)
        r.raise_for_status()

        # init beautifulsoup parser
        page_html = r.text
        page_soup = BeautifulSoup(page_html, 'html.parser')

        # get the loot table
        for table_id in ids_list:
            table = page_soup.find(id=table_id).parent.find_next('table', {'class': 'wikitable'}).find_all("tr")
            items = crawl_table(items, table)

        # clean beautifulsoup parser
        page_soup.decompose()
    except Exception as e:
        logger.info("Warning: Failed crawling url: " + url + " - reason: " + str(e))
        pass

    return items
