# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException

import requests
import itertools

from settings import *

import getter


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

    # open page via webdriver
    driver.get(CONST_BASE_URL + item_url)
    try:
        driver.find_element_by_xpath("//*[text()='ACCEPT']").click() # click the page cookie popup so it doesn't hide the screenshots
    except NoSuchElementException:
        pass

    # get the item details table
    item_details_table = item_soup.find(id='va-infobox0-content') # should be unique

    item_data['url'] = CONST_BASE_URL + item_url
    item_data['name'] = getter.get_item_name(item_soup, item_url)
    item_data['icon'] = getter.get_item_icon(item_soup, item_url)
    item_data['description'] = getter.get_item_description(item_soup, item_url)
    item_data['type'] = getter.get_item_type(item_details_table, item_url)
    item_data['size'] = getter.get_item_size(item_details_table, item_url)
    item_data['weight'] = getter.get_item_weight(item_details_table, item_url)
    item_data['exp'] = getter.get_item_exp(item_details_table, item_url)
    item_data['locations'] = getter.get_item_locations(item_soup, item_url)
    item_data['notes'] = getter.get_item_notes(item_soup, item_url)
    item_data['quests'] = getter.get_item_quests(item_soup, item_url)
    item_data['hideouts'] = getter.get_item_hideouts(item_soup, item_url)
    item_data['trades'] = getter.get_item_trades(item_url)

    # clean beautifulsoup parser
    item_soup.decompose()

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
    
    # clean beautifulsoup parser
    loot_soup.decompose()

    return loot_data
