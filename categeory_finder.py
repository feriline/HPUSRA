import json

from fuzzywuzzy import fuzz

SOFTWARE_LIST_FILE = 'conf/software.json'


def load_software_list():
    with open(SOFTWARE_LIST_FILE) as config_file:
        return json.load(config_file)


software_list = load_software_list()

SPECIAL_CAT_FILE = 'conf/special_soft_category.json'
SPECIAL_LIST_FILE = 'conf/special_list.json'


def load_special_list():
    with open(SPECIAL_LIST_FILE) as conf_file:
        return json.load(conf_file)


special_list = load_special_list()


def load_special_cat():
    with open(SPECIAL_CAT_FILE) as conf_file:
        return json.load(conf_file)


special_cat_dict = load_special_cat()



MIN_RATIO = 90

def get_special_category(software_name, top_category):
    for categroy in special_cat_dict[top_category]:
        for special_soft in special_list[categroy]:
            r = fuzz.token_sort_ratio(software_name, special_soft)
            if r >= MIN_RATIO:
                print(software_name + '>>' + special_soft + '>> fuzz ratio :' + str(r))
                return categroy

    return 'unknown'


def get_category(software_name):
    """
    if software_name in software_list:
        return software_list[software_name]['category']
    else:
        return 'unknown'
    """

    """
    max_ratio = MIN_RATIO-1
    match_soft = None

    for soft in software_list:
        r = fuzz.token_sort_ratio(software_name, soft)
        if r >= MIN_RATIO:
            if r > max_ratio:
                max_ratio = r
                match_soft = soft

    if match_soft is not None:
        print(software_name + '>>' + match_soft + '>> fuzz ratio :' + str(max_ratio))
        return software_list[match_soft]['category']

    """
    for soft in software_list:
        r = fuzz.token_sort_ratio(software_name, soft)
        if r >= MIN_RATIO:
            print(software_name + '>>' + soft + '>> fuzz ratio :' + str(r))
            return software_list[soft]['category']


    return 'unknown'
