# -*- coding: utf-8 -*-


# find the substring between substr1(included) and substr2(excluded)
def find_substring(string, substr1=None, substr2=None, exclude=False):
    if substr1 is not None and exclude:
        idx1 = string.find(substr1)
        cutstr = string[idx1+len(substr1):]
    elif substr1 is not None:
        idx1 = string.find(substr1)
        cutstr = string[idx1:]
    else:
        idx1 = 0
        cutstr = string[idx1:]

    if substr2 is not None:
        idx2 = cutstr.find(substr2)
        res = cutstr[:idx2]
    else:
        res = cutstr

    return res


# calculate the total size of an item
def calculate_total_size(size):
    if size and 'x' in size:
        size_split = size.split('x')
        total_size = int(size_split[0]) * int(size_split[1])
    else:
        total_size = 1  # default size
    return total_size
