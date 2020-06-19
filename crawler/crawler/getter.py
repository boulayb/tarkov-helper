# -*- coding: utf-8 -*-

from PIL import Image
from io import BytesIO
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from settings import *

import image_tools
import tools


# get the item icon
def get_item_icon(item_soup, item_url):
    try:
        item_icon = item_soup.find('td', {'class': 'va-infobox-icon'}).find('img')['src']
        if item_icon is not None and item_icon != "" and item_icon != "\n":
            icon = item_icon
        else:
            raise Exception
    except:
        logger.info("Warning: Icon not found for item " + item_url)
        icon = None

    return icon


# get the item name
def get_item_name(item_soup, item_url):
    try:
        item_name = item_soup.find(id='firstHeading').getText()
        if item_name is not None and item_name != "" and item_name != "\n":
            name = item_name
        else:
            raise Exception
    except:
        logger.info("Warning: Name not found for item " + item_url)
        name = None

    return name


# get the item type
def get_item_type(item_details_table, item_url):
    item_type = generic_get_infos(item_details_table, item_url, "Type")
    if item_type and 'http' in item_type:
        item_type = item_type[item_type.find('[')+1:item_type.find(']')]    # do not return a link but only the name
    return item_type


# get the item weight
def get_item_weight(item_details_table, item_url):
    res = generic_get_infos(item_details_table, item_url, "Weight")
    if res and 'kg' in res:
        res = float(res.split('kg')[0])
    return res


# get the item use time
def get_item_time(item_details_table, item_url):
    res = generic_get_infos(item_details_table, item_url, "Use time")
    if res is None:
        res = generic_get_infos(item_details_table, item_url, "Use Time")
    if res and 's' in res:
        res = int(res.split('s')[0])
    return res


# get the item effects
def get_item_effect(item_details_table, item_url):
    try:
        effect_node = item_details_table.find(text="Effect")
        if effect_node is None:
            effect_node = item_details_table.find(text="Usage")   # sometimes Effect is named Usage
        effect_node = effect_node.parent.parent.find('td', {'class': 'va-infobox-content'})
        res = generic_get_recursive(effect_node, item_url)

        if res is not None:
            res_list = [i for i in res.split('\n') if i]   # remove empty strings
            res = {'effect': None, 'buff': None, 'debuff': None}
            if len(res_list) > 0:
                res_string = '\n'.join(res_list)
                if 'Buffs:' in res_string and 'Debuffs:' in res_string:
                    res['effect'] = tools.find_substring(res_string, substr2="Buffs:").rstrip().lstrip()
                    res['buff'] = tools.find_substring(res_string, "Buffs:", "Debuffs:", exclude=True).rstrip().lstrip()
                    res['debuff'] = tools.find_substring(res_string, "Debuffs:", exclude=True).rstrip().lstrip()
                elif 'Buffs:' in res_string:
                    res['effect'] = tools.find_substring(res_string, substr2="Buffs:").rstrip().lstrip()
                    res['buff'] = tools.find_substring(res_string, "Buffs:", exclude=True).rstrip().lstrip()
                elif 'Debuffs:' in res_string:
                    res['effect'] = tools.find_substring(res_string, substr2="Buffs:").rstrip().lstrip()
                    res['debuff'] = tools.find_substring(res_string, "Debuffs:", exclude=True).rstrip().lstrip()
                else:
                    res['effect'] = res_string.rstrip().lstrip()
        else:
            res = {'effect': None, 'buff': None, 'debuff': None}

    except Exception as e:
        if "has no attribute 'parent'" not in str(e):   # do not display error if it is because the item is not present on the page
            logger.info("Warning: Effect not found for item " + item_url + " - reason: " + str(e))
        res = {'effect': None, 'buff': None, 'debuff': None}

    return res


# get the item penalties and blocks
def get_item_penalties(item_soup, item_url):
    penalties = generic_get_infos(item_soup, item_url, 'Penalties')

    block_headset = generic_get_infos(item_soup, item_url, 'Blocks Headset')
    if block_headset and penalties:
        penalties += '\nBlock Headset: ' + block_headset
    elif block_headset:
        penalties = 'Block Headset: ' + block_headset

    block_eyewear = generic_get_infos(item_soup, item_url, 'Blocks Eyewear')
    if block_eyewear and penalties:
        penalties += '\nBlock Eyewear: ' + block_eyewear
    elif block_eyewear:
        penalties = 'Block Eyewear: ' + block_eyewear

    block_face = generic_get_infos(item_soup, item_url, 'Blocks Face cover')
    if block_face and penalties:
        penalties += '\nBlock Face cover: ' + block_face
    elif block_face:
        penalties = 'Block Face cover:' + block_face

    block_headwear = generic_get_infos(item_soup, item_url, 'Blocks Headwear')
    if block_headwear and penalties:
        penalties += '\nBlock Headwear: ' + block_headwear
    elif block_headwear:
        penalties = 'Block Headwear:' + block_headwear

    block_armor = generic_get_infos(item_soup, item_url, 'Blocks Armor')
    if block_armor and penalties:
        penalties += '\nBlocks Armor: ' + block_armor
    elif block_armor:
        penalties = 'Blocks Armor:' + block_armor

    return penalties


# get the item quests needs
def get_item_quests(item_soup, item_url):
    quests = generic_get_category(item_soup, item_url, "Quests")
    rewards = generic_get_category(item_soup, item_url, "Quest rewards")
    if quests and rewards:
        return quests + rewards
    elif quests:
        return quests
    else:
        return rewards


# get the item notes
def get_item_notes(item_soup, item_url):
    notes = generic_get_category(item_soup, item_url, "Notes")
    info = generic_get_category(item_soup, item_url, "Info")
    if notes and info:
        return notes + info
    elif notes:
        return notes
    else:
        return info


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
                    children_res = ''
                    contents = children.contents
                    for info in contents:
                        if isinstance(info, str) is False and info.name == 'a':
                            if info.has_attr('title') and info['title'] in CONST_EFFECT_LIST:
                                children_res += "'" + info['title'] + "'"
                            elif info.has_attr('href') and info['href']:
                                children_res += '[' + info.getText() + '](' + CONST_BASE_URL + info['href'] + ')'
                            else:
                                children_res += info.getText()
                        elif isinstance(info, str) is False and info.name == 'br':
                            children_res += '\n'
                        elif isinstance(info, str) is False:
                            children_res += info.getText()
                        else:
                            children_res += info
                    infos.append(children_res)

            elif current_node.name == 'li' and images_found is False:
                images_found = True

            elif current_node.name == 'p':
                current_node_res = ''
                contents = current_node.contents
                for info in contents:
                    if isinstance(info, str) is False and info.name == 'a':
                        if info.has_attr('title') and info['title'] in CONST_EFFECT_LIST:
                            current_node_res += "'" + info['title'] + "'"
                        elif info.has_attr('href') and info['href']:
                            current_node_res += '[' + info.getText() + '](' + CONST_BASE_URL + info['href'] + ')'
                        else:
                            current_node_res += info.getText()
                    elif isinstance(info, str) is False and info.name == 'br':
                        current_node_res += '\n'
                    elif isinstance(info, str) is False:
                        current_node_res += info.getText()
                    else:
                        current_node_res += info
                infos.append(current_node_res)

            current_node = current_node.find_next_sibling()

        if images_found is True:
            infos.append('Check [wiki page](' + CONST_BASE_URL + item_url + '#' + category_id + ') for image')
    except Exception as e:
        if "has no attribute 'parent'" not in str(e):   # do not display error if it is because the item is not present on the page
            logger.info("Warning: " + category_id + " not found for item " + item_url + " - reason: " + str(e))
        infos = None

    return infos if infos and len(infos) > 0 else None


def generic_get_recursive(node, item_url):
    try:
        res = ''
        contents = node.contents
        for info in contents:
            if isinstance(info, str) is False and info.name == 'a':
                if info.has_attr('title') and info['title'] in CONST_EFFECT_LIST:
                    res += " '" + info['title'] + "' "
                elif info.has_attr('href') and info['href']:
                    res += '[' + info.getText() + '](' + CONST_BASE_URL + info['href'] + ')'
                else:
                    res += info.getText()
            elif isinstance(info, str) is False and info.name == 'br':
                res += '\n'
            elif isinstance(info, str) is False and (info.name == 'ul' or info.name == 'li' or info.name == 'p'):
                recursion = generic_get_recursive(info, item_url)
                if recursion is not None:
                    res += recursion
            elif isinstance(info, str) is False:
                res += info.getText()
            else:
                if 'Generic loot item' not in info and 'Quest item' not in info:
                    res += info
    except Exception as e:
        if "has no attribute 'parent'" not in str(e):   # do not display error if it is because the item is not present on the page
            logger.info("Warning: recursive node " + str(node) + " not parsed for item " + item_url + " - reason: " + str(e))
        res = None

    return res


# generic getter to get all text from the info table of an item
def generic_get_infos(item_details_table, item_url, info_id):
    try:
        item_info = item_details_table.find(text=info_id).parent.parent.find('td', {'class': 'va-infobox-content'})
        if item_info is not None and item_info != "" and item_info != "\n":
            current_node_res = ''
            contents = item_info.contents
            for info in contents:
                if isinstance(info, str) is False and info.name == 'a':
                    if info.has_attr('title') and info['title'] in CONST_EFFECT_LIST:
                        current_node_res += " '" + info['title'] + "' "
                    elif info.has_attr('href') and info['href']:
                        current_node_res += '[' + info.getText() + '](' + CONST_BASE_URL + info['href'] + ')'
                    else:
                        current_node_res += info.getText()
                elif isinstance(info, str) is False and info.name == 'br':
                    current_node_res += '\n'
                elif isinstance(info, str) is False:
                    current_node_res += info.getText()
                else:
                    current_node_res += info
        else:
            raise Exception
    except Exception as e:
        if "has no attribute 'parent'" not in str(e):   # do not display error if it is because the item is not present on the page
            logger.info("Warning: " + info_id + " not found for item " + item_url + " - reason: " + str(e))
        current_node_res = None

    return current_node_res if current_node_res != '' else None


# take screenshot of the trade & craft sections, concat them and upload to imgur, save link for ES
def get_item_trade(item_url, driver):
    try:
        popup = WebDriverWait(driver, CONST_SELENIUM_DELAY).until(EC.presence_of_element_located((By.XPATH, "//*[text()='ACCEPT']")))   # wait x seconds for page to load
        popup.click()   # click the page cookie popup so it doesn't hide the screenshots
    except Exception as e:
        if 'Unable to locate element' not in str(e):
            logger.info("Warning: Selenium couldn't parse the page for item " + item_url + " - reason: " + str(e))
        trades = None
        return trades

    # screenshot the crafting section
    try:
        crafting_title = driver.find_element_by_id("Crafting")
        crafting_table = crafting_title.find_element_by_xpath("../following-sibling::table[@class='wikitable']")
        crafting_screen = crafting_table.screenshot_as_png
        crafting_screen = Image.open(BytesIO(crafting_screen))  # uses PIL library to open image in memory
    except Exception as e:
        if 'Unable to locate element' not in str(e):
            logger.info("Warning: Crafting not found for item " + item_url + " - reason: " + str(e))
        crafting_screen = None

    # screenshot the trading section
    try:
        trading_title = driver.find_element_by_id("Trading")
        trading_table = trading_title.find_element_by_xpath("../following-sibling::table[@class='wikitable']")
        trading_screen = trading_table.screenshot_as_png
        trading_screen = Image.open(BytesIO(trading_screen))    # uses PIL library to open image in memory
    except Exception as e:
        if 'Unable to locate element' not in str(e):
            logger.info("Warning: Trading not found for item " + item_url + " - reason: " + str(e))
        trading_screen = None

    # save the screenshot
    screenshot_location = CONST_SCREENSHOTS_FOLDER + str(item_url) + '.png'
    if crafting_screen is not None and trading_screen is not None:
        image_tools.get_concat_v_resize(crafting_screen, trading_screen, resize_big_image=False).save(screenshot_location)  # concat the screenshots
    elif crafting_screen is not None:
        crafting_screen.save(screenshot_location)
    elif trading_screen is not None:
        trading_screen.save(screenshot_location)
    else:
        trades = None
        return trades

    trades = CONST_SERVER_URL + str(item_url) + '.png'
    return trades
