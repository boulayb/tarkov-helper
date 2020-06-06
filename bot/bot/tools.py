# -*- coding: utf-8 -*-

from datetime import datetime


# delta in days between today and a late date
def days_since(late_date):
    days_since = datetime.today() - late_date
    if days_since.days <= 0:
        return 'today'
    elif days_since.days == 1:
        return 'yesterday'
    else:
        return str(days_since.days) + ' days ago'


# 'YYYYMMDDHHmmss' to proper date
# fuck this format and fuck you for using it 
def convert_date(date):
    year = int(date[0:4])
    date_without_year = date[4:]
    split = [int(date_without_year[i:i+2]) for i in range(0, len(date_without_year), 2)] # split line every two characters
    proper_date = datetime(year, split[0], split[1], split[2], split[3], split[4])

    return proper_date


# build an embed string from a list of strings
def build_string(string_list, item_url, see_more=True):

    rest_str = None
    embed_str = '- ' + '\n- '.join(string_list)   # one string per line

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
