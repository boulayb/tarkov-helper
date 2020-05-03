# -*- coding: utf-8 -*-

from crawler import logger


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


# get the item type
def get_item_type(item_details_table, item_url):
    try:
        item_type = item_details_table.find(text="Type").parent.parent.find('td', {'class': 'va-infobox-content'}).getText()
        if item_type is not None and item_type != "" and item_type != "\n":
            logger.info("Type found")
            type_ = item_type
        else:
            raise Exception
    except:
        logger.info("Warning: Type not found for item " + item_url)
        type_ = ""

    return type_


# get the item weight
def get_item_weight(item_details_table, item_url):
    try:
        item_weight = item_details_table.find(text="Weight").parent.parent.find('td', {'class': 'va-infobox-content'}).getText()
        if item_weight is not None and item_weight != "" and item_weight != "\n":
            logger.info("Weight found")
            weight = item_weight
        else:
            raise Exception
    except:
        logger.info("Warning: Weight not found for item " + item_url)
        weight = "Not found"

    return weight


# get the item size
def get_item_size(item_details_table, item_url):
    try:
        item_size = item_details_table.find(text="Grid size").parent.parent.find('td', {'class': 'va-infobox-content'}).getText()
        if item_size is not None and item_size != "" and item_size != "\n":
            logger.info("Size found")
            size = item_size
        else:
            raise Exception
    except:
        logger.info("Warning: Size not found for item " + item_url)
        size = "Not found"

    return size


# get the item exp
def get_item_exp(item_details_table, item_url):
    try:
        item_exp = item_details_table.find(text="Loot experience").parent.parent.find('td', {'class': 'va-infobox-content'}).getText()
        if item_exp is not None and item_exp != "" and item_exp != "\n":
            logger.info("Exp found")
            exp = item_exp
        else:
            raise Exception
    except:
        logger.info("Warning: Exp not found for item " + item_url)
        exp = "Not found"

    return exp


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


# get the item description
def get_item_description(item_soup, item_url):
    try:
        item_description = item_soup.find(id="Description").parent.findNext('p').getText()
        if item_description is not None and item_description != "" and item_description != "\n":
            logger.info("Description found")
            description = item_description
        else:
            raise Exception
    except:
        logger.info("Warning: Description not found for item " + item_url)
        description = "No description found"
    
    return description
