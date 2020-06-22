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

    for name, item in items.items():
        logger.info("Taking screenshot from " + item['url'])
        try:
            # open page via webdriver
            driver = webdriver.Remote("http://webdriver:4444/wd/hub", DesiredCapabilities.FIREFOX)
            driver.get(item['url'])

            item['trade'] = getter.get_item_trade(item['url'].replace(CONST_BASE_URL, ''), driver)

            driver.close()
        except Exception as e:
            logger.info("Warning: Failed crawling trades for item url: " + item['url'].replace(CONST_BASE_URL, '') +  " - reason: " + str(e))
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
    items[name]['notes'] = getter.get_item_notes(item_soup, item_url)
    items[name]['quests'] = getter.get_item_quests(item_soup, item_url)
    items[name]['type'] = getter.get_item_type(item_details_table, item_url)
    items[name]['time'] = getter.get_item_time(item_details_table, item_url)
    items[name]['weight'] = getter.get_item_weight(item_details_table, item_url)
    items[name]['locations'] = getter.get_item_locations(item_soup, item_url)
    items[name]['penalties'] = getter.get_item_penalties(item_details_table, item_url)
    items[name]['lock_location'] = getter.generic_get_category(item_soup, item_url, "Lock_Locations")
    items[name]['behind_lock'] = getter.generic_get_category(item_soup, item_url, "Behind_the_Lock")
    items[name]['hideouts'] = getter.generic_get_category(item_soup, item_url, "Hideout")
    items[name]['dealer'] = getter.generic_get_infos(item_details_table, item_url, "Sold by")
    items[name]['description'] = getter.generic_get_category(item_soup, item_url, "Description")
    items[name]['exp'] = getter.generic_get_infos(item_details_table, item_url, "Loot experience")
    items[name]['inventory'] = getter.generic_get_infos(item_details_table, item_url, "Inventory")
    items[name]['material'] = getter.generic_get_infos(item_details_table, item_url, "Material")
    items[name]['class'] = getter.generic_get_infos(item_details_table, item_url, "Armor class")
    items[name]['zone'] = getter.generic_get_infos(item_details_table, item_url, "Armor zones")
    items[name]['segment'] = getter.generic_get_infos(item_details_table, item_url, "Armor segments")
    items[name]['durability'] = getter.generic_get_infos(item_details_table, item_url, "Durability")
    items[name]['ricochet'] = getter.generic_get_infos(item_details_table, item_url, "Ricochet chance")
    items[name]['size'] = getter.generic_get_infos(item_details_table, item_url, "Grid size")
    items[name]['total_size'] = tools.calculate_total_size(items[name]['size'])
    effects = getter.get_item_effect(item_details_table, item_url)
    items[name]['effect'] = effects['effect']
    items[name]['buff'] = effects['buff']
    items[name]['debuff'] = effects['debuff']

    # clean beautifulsoup parser and close webdriver page
    item_soup.decompose()

    return items


# crawl links to item from table
def crawl_table(items, loot_table, tab=False):

    for loot_item in loot_table[1:]: # each row of the table is a loot item, except first one (titles)
        link = None
        try:
            loot_infos = loot_item.find_all(['th', 'td'])   # 0=icon, 1=name+link, 2=type, etc...
            loot_name = loot_infos[1].find("a")
            if loot_name is not None:
                link = loot_name['href']
                name = loot_name.getText()
                items = crawl_item(items, name, link)
        except Exception as e:
            if link:
                logger.info("Warning: Failed crawling item for url: " + link + " - reason: " + str(e))
            else:
                logger.info("Warning: Failed crawling loot table - reason: " + str(e))
            pass

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
            table = page_soup.find(id=table_id).parent.find_next('table', {'class': 'wikitable'})
            table_div = table.find_parent('div')
            if table_div and "tabbertab" in table_div['class']:
                all_divs = [elem for elem in table_div.find_parent('div') if getattr(elem, 'name', None) == 'div']
                for div in all_divs:
                    table = div.find_next('table', {'class': 'wikitable'})
                    items = crawl_table(items, table.find_all("tr"), tab=True)
            else:
                items = crawl_table(items, table.find_all("tr"))

        # clean beautifulsoup parser
        page_soup.decompose()
    except Exception as e:
        logger.info("Warning: Failed crawling url: " + url + " - reason: " + str(e))
        pass

    return items
