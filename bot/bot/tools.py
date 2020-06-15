# -*- coding: utf-8 -*-

from datetime import datetime

from settings import *


# delta in days between today and a late date
def days_since(late_date):
    if late_date != '':
        try:
            days_since = datetime.today() - late_date
            if days_since.days <= 0:
                hours_since = int(days_since.total_seconds() / 3600)
                if hours_since <= 0:
                    return 'this hour'
                else:
                    return str(hours_since) + ' hours ago'
            elif days_since.days == 1:
                return 'yesterday'
            else:
                return str(days_since.days) + ' days ago'
        except Exception as e:
            logger.info("Warning: Days since failed for date: " + str(late_date) + " - Reason: " + e)

    return ''


# 'YYYYMMDDHHmmss' to proper date
# fuck this format and fuck you for using it 
def convert_date_loot_goblin(date):
    try:
        year = int(date[0:4])
        date_without_year = date[4:]
        split = [int(date_without_year[i:i+2]) for i in range(0, len(date_without_year), 2)] # split line every two characters
        proper_date = datetime(year, split[0], split[1], split[2], split[3], split[4])
    except Exception as e:
        logger.info("Warning: Date conversion failed for date: " + str(date) + " - Reason: " + e)
        return ''

    return proper_date


def convert_date_tarkov_market(date_str):
    try:
        proper_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    except Exception as e:
        logger.info("Warning: Date conversion failed for date: " + str(date_str) + " - Reason: " + e)
        return ''

    return proper_date


# build an embed string from a list of strings
def build_string(string_list, item_url, prefix='', see_more=True):

    rest_str = None
    embed_str = prefix + ('\n' + prefix).join(string_list)   # one string per line

    if len(embed_str) > 1024:   # one field can only contain a maximum of 1024 characters
        if see_more is True:
            see_more_str = "\n- See the remainings [here](" + item_url + ")"
            last_line = embed_str[:1024-len(see_more_str)].rfind('\n')
            rest_str = embed_str[last_line:]
            embed_str = embed_str[:last_line]
            embed_str += see_more_str
        else:
            last_line = embed_str[:1024].rfind('\n')
            rest_str = embed_str[last_line:]
            embed_str = embed_str[:last_line]

    result = {"embed_str": embed_str, "rest_str": rest_str}

    return result
