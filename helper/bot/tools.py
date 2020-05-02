# -*- coding: utf-8 -*-

from datetime import datetime


# 'YYYYMMDDHHmmss' to proper date
# fuck this format and fuck you for using it 
def convert_date(date):

    year = int(date[0:4])
    date_without_year = date[4:]
    split = [int(date_without_year[i:i+2]) for i in range(0, len(date_without_year), 2)] # split line every two characters
    proper_date = datetime(year, split[0], split[1], split[2], split[3], split[4])

    return proper_date

