# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup

import requests
import itertools

from crawler import CONST_BASE_URL, logger

CONST_LOOT_PAGE = "/Loot"


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

    # get the item type
    try:
        item_type = item_details_table.find(text="Type").parent.parent.find('td', {'class': 'va-infobox-content'}).getText()
        if item_type is not None and item_type != "" and item_type != "\n":
            logger.info("Type found")
            type_ = item_type
        else:
            raise Exception
    except:
        logger.info("Warning: Type not found for loot item " + item_url)
        type_ = ""

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

    item_data['type'] = type_
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
