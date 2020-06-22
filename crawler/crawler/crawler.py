# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from elasticsearch.helpers import bulk

from settings import *

import item
import price
import search


# format the crawled data to ES bulk format
def format_to_bulk(data, index):
    bulk_data_list = []
    for item_name, item in data.items():
        bulk_data = {
            '_index': index,
            '_type': index,
            '_id': item_name
        }
        bulk_data.update(item)
        bulk_data_list.append(bulk_data)
    return bulk_data_list


# send data to elasticsearch in index
def send_to_es(es, data, index):
    if es.indices.exists(index=index) is False:
        es.indices.create(index=index)
    bulk_success, bulk_failed = bulk(es, format_to_bulk(data, index))
    logger.info("Bulk ended with " + str(bulk_success) + " success and " + str(bulk_failed))


# get all items from index as a list
def get_items_from_index(index):
    items = {}
    result = search.search_item(index, res_size=50, scroll_time='10s')
    if result['total'] != -1:
        while len(result['items']) > 0:
            for item in result['items']:
                new_item = {item['name']: item}
                items.update(new_item)
            result = search.scroll_item(result['scroll_id'], scroll_time='10s')
    return items


def main():

    # remove existing index if asked for
    if reset_index is True and es.indices.exists(index=CONST_ES_ITEM_INDEX):
        es.indices.delete(index=CONST_ES_ITEM_INDEX)
        es.indices.create(index=CONST_ES_ITEM_INDEX)

    # get the existing items from index to update them
    items = get_items_from_index(CONST_ES_ITEM_INDEX)

    # crawl items from the wiki
    if crawl_loot is True:
        logger.info("Crawling items")
        items = item.crawl_category(items, CONST_LOOT_PAGE, ['List_of_loot'])
        items = item.crawl_category(items, CONST_MEDICAL_PAGE, ['List_of_medical_supplies', 'List_of_Stimulators'])
        items = item.crawl_category(items, CONST_PROVISION_PAGE, ['List'])
        items = item.crawl_category(items, CONST_CONTAINER_PAGE, ['List'])
        items = item.crawl_category(items, CONST_EYEWEAR_PAGE, ['List'])
        items = item.crawl_category(items, CONST_ARMBAND_PAGE, ['List'])
        items = item.crawl_category(items, CONST_POUCH_PAGE, ['List'])
        items = item.crawl_category(items, CONST_HEADWEAR_PAGE, ['Mount', 'Armored', 'Vanity'])
        items = item.crawl_category(items, CONST_FACEWEAR_PAGE, ['Armored', 'Vanity'])
        items = item.crawl_category(items, CONST_HEADSET_PAGE, ['List'])
        items = item.crawl_category(items, CONST_HEADGEAR_PAGE, ['Night_vision_devices', 'Thermal_vision_devices', 'Visors', 'Additional_armor', 'Mounts', 'Vanity'])
        items = item.crawl_category(items, CONST_BACKPACK_PAGE, ['List'])
        items = item.crawl_category(items, CONST_ARMOR_PAGE, ['List'])
        items = item.crawl_category(items, CONST_CHESTRIG_PAGE, ['Armored', 'Unarmored'])
        items = item.crawl_category(items, CONST_KEYS_PAGE, ['Keys_&_Keycards'])

    # screenshots of trade and craft
    if take_screenshots is True:
        logger.info("Taking screenshots")
        items = item.crawl_trade(items)

    # item prices from tarkov market
    if crawl_prices is True:
        logger.info("Crawling prices")
        items = price.crawl_prices_tarkov_market(items)

    # crawl images from the wiki
    # if crawl_images is True:
    #     logger.info("Crawling images")
    #     images = {}
    #     images.update(medical.crawl_images())

    # send data to elasticsearch
    if use_elasticsearch is True:
        logger.info("Sending to elasticsearch")
        send_to_es(es, items, CONST_ES_ITEM_INDEX)
        # if images:
        #     send_to_es(es, images, CONST_ES_IMAGE_INDEX)

    logger.info("Done!")

    # close log handle
    log_hdlr.close()
    logger.removeHandler(log_hdlr)


if __name__ == "__main__":
    main()
