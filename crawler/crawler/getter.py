# -*- coding: utf-8 -*-

from PIL import Image
from io import BytesIO
from selenium.common.exceptions import NoSuchElementException

from settings import *

import image_tools


# get the item icon
def get_item_icon(item_soup, item_url):
    try:
        item_icon = item_soup.find('td', {'class': 'va-infobox-icon'}).find('img')['src']
        if item_icon is not None and item_icon != "" and item_icon != "\n":
            logger.info("Icon found")
            icon = item_icon
        else:
            raise Exception
    except:
        logger.info("Warning: Icon not found for item " + item_url)
        icon = ""

    return icon


# get the item name
def get_item_name(item_soup, item_url):
    try:
        item_name = item_soup.find(id='firstHeading').getText()
        if item_name is not None and item_name != "" and item_name != "\n":
            logger.info("Name found")
            name = item_name
        else:
            raise Exception
    except:
        logger.info("Warning: Name not found for item " + item_url)
        name = "No name found"

    return name


# get the item type
def get_item_type(item_details_table, item_url):
    return generic_get_infos(item_details_table, item_url, "Type")


# get the item weight
def get_item_weight(item_details_table, item_url):
    return generic_get_infos(item_details_table, item_url, "Weight")


# get the item size
def get_item_size(item_details_table, item_url):
    return generic_get_infos(item_details_table, item_url, "Grid size")


# get the item exp
def get_item_exp(item_details_table, item_url):
    return generic_get_infos(item_details_table, item_url, "Loot experience")


# get the item description
def get_item_description(item_soup, item_url):
    return generic_get_category(item_soup, item_url, "Description")


# get the item locations
def get_item_locations(item_soup, item_url):
    return generic_get_category(item_soup, item_url, "Location")


# get the item hideout needs
def get_item_hideouts(item_soup, item_url):
    return generic_get_category(item_soup, item_url, "Hideout")


# get the item quests needs
def get_item_quests(item_soup, item_url):
    return generic_get_category(item_soup, item_url, "Quests")


# get the item notes
def get_item_notes(item_soup, item_url):
    return generic_get_category(item_soup, item_url, "Notes")


# generic getter to get all text and links from a category of an item
def generic_get_category(item_soup, item_url, category_id):
    infos = []
    try:
        images_found = False

        current_node = item_soup.find(id=category_id).parent.find_next_sibling()
        while current_node.name == 'ul' or current_node.name == 'h3' or current_node.name == 'li' or current_node.name == 'p':  # ul == list of infos, h3 == title/map of infos, li == images of infos, p == single info

            if current_node.name == 'ul':
                # search for links in infos, if there is we keep them to display them
                for children in current_node.findChildren(recursive=False):
                    info = children.getText()
                    links = children.find_all('a')
                    links_dict = {link.getText():link['href'] for link in links}
                    for text, link in links_dict.items():
                        info = info.replace(text, '[' + text + '](' + CONST_BASE_URL + link + ')')
                    infos.append(info)

            elif current_node.name == 'li' and images_found is False:
                images_found = True

            elif current_node.name == 'p':
                info = current_node.getText()
                links = current_node.find_all('a')
                links_dict = {link.getText():link['href'] for link in links}
                for text, link in links_dict.items():
                    info = info.replace(text, '[' + text + '](' + CONST_BASE_URL + link + ')')
                infos.append(info)

            current_node = current_node.find_next_sibling()

        if images_found is True:
            infos.append('Check [wiki page](' + CONST_BASE_URL + item_url + '#' + category_id + ') for image')
    except:
        logger.info("Warning: " + category_id + " not found for item " + item_url)

    return infos


# generic getter to get all text from the info table of an item
def generic_get_infos(item_details_table, item_url, info_id):
    try:
        item_info = item_details_table.find(text=info_id).parent.parent.find('td', {'class': 'va-infobox-content'}).getText()
        if item_info is not None and item_info != "" and item_info != "\n":
            info = item_info
        else:
            raise Exception
    except:
        logger.info("Warning: " + info_id + " not found for item " + item_url)
        info = "Not found"

    return info


# take screenshot of the trade & craft sections, concat them and upload to imgur, save link for ES
def get_item_trades(item_url):

    # screenshot the crafting section
    try:
        crafting_title = driver.find_element_by_id("Crafting")
        crafting_table = crafting_title.find_element_by_xpath("../following-sibling::table[@class='wikitable']")
        crafting_screen = crafting_table.screenshot_as_png
        crafting_screen = Image.open(BytesIO(crafting_screen)) # uses PIL library to open image in memory
    except:
        logger.info("Warning: Crafting not found for item " + item_url)
        crafting_screen = None

    # screenshot the trading section
    try:
        trading_title = driver.find_element_by_id("Trading")
        trading_table = trading_title.find_element_by_xpath("../following-sibling::table[@class='wikitable']")
        trading_screen = trading_table.screenshot_as_png
        trading_screen = Image.open(BytesIO(trading_screen)) # uses PIL library to open image in memory
    except:
        logger.info("Warning: Trading not found for item " + item_url)
        trading_screen = None

    # save the screenshot
    screenshot_location = CONST_SCREENSHOTS_FOLDER + str(item_url) + '.png'
    if crafting_screen is not None and trading_screen is not None:
        image_tools.get_concat_v_resize(crafting_screen, trading_screen, resize_big_image=False).save(screenshot_location) # concat the screenshots
    elif crafting_screen is not None:
        crafting_screen.save(screenshot_location)
    elif trading_screen is not None:
        trading_screen.save(screenshot_location)
    else:
        trades = ''
        return trades

    trades = CONST_SERVER_URL + str(item_url) + '.png'
    return trades
