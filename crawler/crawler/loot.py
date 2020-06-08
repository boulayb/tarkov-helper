# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import requests
import itertools

from settings import *

import getter
import tools


# crawl a single item page to retrieve infos
def crawl_loot_item(item_url):
    item_data = {}  ### TODO: set default values for all data that will go in there (loot and prices)

    # get the item loot page
    logger.info("Getting HTML from " + CONST_BASE_URL + item_url)
    r = requests.get(CONST_BASE_URL + item_url)
    r.raise_for_status()

    # init beautifulsoup parser
    item_html = r.text
    item_soup = BeautifulSoup(item_html, 'html.parser')

    # open page via webdriver
    if take_screenshots is True:
        driver = webdriver.Remote("http://webdriver:4444/wd/hub", DesiredCapabilities.FIREFOX)
        driver.get(CONST_BASE_URL + item_url)

    # get the item details table
    item_details_table = item_soup.find(id='va-infobox0-content') # should be unique

    item_data['url'] = CONST_BASE_URL + item_url
    item_data['name'] = getter.get_item_name(item_soup, item_url)
    item_data['icon'] = getter.get_item_icon(item_soup, item_url)
    item_data['description'] = getter.get_item_description(item_soup, item_url)
    item_data['type'] = getter.get_item_type(item_details_table, item_url)
    item_data['size'] = getter.get_item_size(item_details_table, item_url)
    item_data['total_size'] = tools.calculate_total_size(item_data['size'])
    item_data['weight'] = getter.get_item_weight(item_details_table, item_url)
    item_data['exp'] = getter.get_item_exp(item_details_table, item_url)
    item_data['locations'] = getter.get_item_locations(item_soup, item_url)
    item_data['notes'] = getter.get_item_notes(item_soup, item_url)
    item_data['quests'] = getter.get_item_quests(item_soup, item_url)
    item_data['hideouts'] = getter.get_item_hideouts(item_soup, item_url)
    if take_screenshots is True:
        item_data['trades'] = getter.get_item_trades(item_url, driver)

    # clean beautifulsoup parser and close webdriver page
    item_soup.decompose()
    if take_screenshots is True:
        driver.close()

    return item_data


# crawl each loot page from the main loot page table to get their infos
def crawl_loot():
    loot_data = {}

    # get the wiki loot page
    logger.info("Getting HTML from " + CONST_BASE_URL + CONST_LOOT_PAGE)
    r = requests.get(CONST_BASE_URL + CONST_LOOT_PAGE)
    r.raise_for_status()

    # init beautifulsoup parser
    loot_html = r.text
    loot_soup = BeautifulSoup(loot_html, 'html.parser')

    # get the loot table
    loot_table = loot_soup.find('table', {'class': 'wikitable'}).find_all("tr")
    for loot_item in itertools.islice(loot_table, 1, None): # each row of the table is a loot item, except first one (titles)
        loot_infos = loot_item.find_all("th")   # 0=icon, 1=name+link, 2=type, 3=notes
        loot_name = loot_infos[1].find("a")
        if loot_name is not None:
            link = loot_name['href']
            name = loot_name.getText()
            loot_data[name] = crawl_loot_item(link)
    
    # clean beautifulsoup parser
    loot_soup.decompose()

    return loot_data
