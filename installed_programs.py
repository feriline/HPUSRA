import datetime
import json
import re

import copy

import pythoncom

from categeory_finder import get_category, get_special_category
from report_manager import ReportManager
from write_to_log_file import __init__, write_to_log_file

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import traceback
import wmi
from winreg import (HKEY_LOCAL_MACHINE, KEY_ALL_ACCESS,
                    OpenKey, QueryValueEx)

INSTALLED_SOFT = 'conf/installed_soft.json'
HKLM = 0x80000002

SPECIAL_CAT_FILE = 'conf/special_soft_category.json'


def load_special_cat():
    with open(SPECIAL_CAT_FILE) as conf_file:
        return json.load(conf_file)


special_cat_dict = load_special_cat()


def get_special_files():
    installed_soft_list = load_installed_soft()


    special_soft_list = {}

    for top_category in special_cat_dict:
        special_soft_list[top_category] = []

    for soft in installed_soft_list:
        file_category = installed_soft_list[soft]
        if file_category in special_cat_dict:
            special_soft_list[file_category].append(soft)

    return special_soft_list


def special_software(report_manager):
    special_files = get_special_files()

    special_soft_main = report_manager.get_report_dict()['special_software']
    special_soft_main.clear()


    for top_category in special_cat_dict:
        for category in special_cat_dict[top_category]:
            special_soft_main[category] = 0


    for top_category in special_files:
        for soft_name in special_files[top_category]:
            category = get_special_category(soft_name, top_category)
            if category != 'unknown':
                special_soft_main[category] = special_soft_main[category] +1


def load_installed_soft():
    with open(INSTALLED_SOFT) as config_file:
        return json.load(config_file)


def get_current_installed_soft():
    # This code is necessary for calling com object
    pythoncom.CoInitialize()

    current_installed_soft = []
    # r = wmi.Registry()
    r = wmi.WMI(namespace='DEFAULT').StdRegProv
    result, names = r.EnumKey(hDefKey=HKLM,#HKEY_LOCAL_MACHINE
                              sSubKeyName=r"Software\Microsoft\Windows\CurrentVersion\Uninstall")

    keyPath = r"Software\Microsoft\Windows\CurrentVersion\Uninstall"

    for subkey in names:
        key = None
        try:
            path = keyPath + "\\" + subkey
            key = OpenKey(HKEY_LOCAL_MACHINE, path, 0, KEY_ALL_ACCESS)
            try:
                temp = QueryValueEx(key, 'DisplayName')
                software_name = str(temp[0])
                current_installed_soft.append(software_name)

            except:
                #software_name = 'unknown'
                #print('unknown')
                i = 1


        except:
            fp = StringIO.StringIO()
            traceback.print_exc(file=fp)
            errorMessage = fp.getvalue()
            error = 'Error for ' + key + '. Message follows:\n' + errorMessage
            # errorLog.write(error)
            # errorLog.write("\n\n")

    remove_char = '-!@#$.0123456789()\t'
    remove_phrase = {'version', 'Version', 'Update', 'update', '  ', '(x64)', '(x86)', 'x64',
                     'x86', '(64-bit)', '(32-bit)', '(SP1)', '(SP2)', '(SP3)', '(SP4)', 'ENU',
                     '(amd64)', 'HOTKEY', 'None', 'MUI', 'OSM', 'English', 'Deutsch',
                     'español', 'Français'}
    remove_lines = {'update', 'Update', 'Hotfix', 'hotfix'}


    clean_installed_soft = []
    for soft_name in current_installed_soft:
        for phrase in remove_phrase:
            soft_name = soft_name.replace(phrase, "")
        for char in remove_char:
            soft_name = soft_name.replace(char, "")
        if not any(phrase in soft_name for phrase in remove_lines):
            soft_name = soft_name.strip()
            if soft_name not in clean_installed_soft:
                clean_installed_soft.append(soft_name)
    return clean_installed_soft

# log : [IP] <TimeStamp>  <DisplayName> <RegKey>
def installed_programs(report_manager):
    initial_installed_soft = load_installed_soft()
    current_installed_soft = get_current_installed_soft()
    initial_soft_names = initial_installed_soft.keys()
    deleted_soft_list = [x for x in initial_soft_names if x not in current_installed_soft]
    print('------ Deleted Soft -------')
    print(deleted_soft_list)
    new_soft_list = [x for x in current_installed_soft if x not in initial_soft_names]

    print('------ New Soft -------')
    with open('Logs/installed_soft.log', 'w') as soft_file:
        for new_soft in new_soft_list:
            soft_file.write(new_soft+'\n')

    installed_soft_main = report_manager.get_report_dict()['installed_software']

    special_soft_main = report_manager.get_report_dict()['special_software']
    if not special_soft_main:
        for top_category in special_cat_dict:
            for category in special_cat_dict[top_category]:
                special_soft_main[category] = 0

    for del_soft in deleted_soft_list:
        soft_category = initial_installed_soft[del_soft]
        if soft_category in installed_soft_main:
            installed_soft_main[soft_category] = installed_soft_main[soft_category] -1
            if installed_soft_main[soft_category] == 0:
                del installed_soft_main[soft_category]
        if soft_category in special_cat_dict:
            category = get_special_category(del_soft, soft_category)
            if category != 'unknown':
                special_soft_main[category] = special_soft_main[category] - 1


        del initial_installed_soft[del_soft]


    softFile = open('Logs/softLog.log', 'w')
    # errorLog = open('errors.log', 'w')

    for software_name in new_soft_list:
        current_time = datetime.datetime.now()
        write_to_log_file('[IP]\t' + str(current_time) + '\t' + software_name)
        # m = re.search('(.+?)\s*\d.*', software_name)

        # if m:
        #    software_name = m.group(1)

        category = get_category(software_name)
        softFile.write('software: ' + software_name + '\tcategory: ' + category + '\n')
        if category not in installed_soft_main:
            installed_soft_main[category] = 1
        else:
            installed_soft_main[category] = installed_soft_main[category] + 1

        initial_installed_soft[software_name] = category
        if category in special_cat_dict:
            sub_cat = get_special_category(software_name, category)
            if sub_cat != 'unknown':
                special_soft_main[sub_cat] = special_soft_main[sub_cat] + 1

    softFile.close()
    # errorLog.close()
    #report_manager.get_report_dict()['installed_software'] = copy.deepcopy(installed_soft)
    with open(INSTALLED_SOFT, 'w') as outfile:
        json.dump(initial_installed_soft, outfile, default=str, indent=4)


if __name__ == "__main__":

    __init__()
    report_manager = ReportManager()
    start = datetime.datetime.now()
    installed_programs(report_manager)
    stop = datetime.datetime.now()
    print("Total Time is :"+str(stop - start))

    """"
    report_manager = ReportManager()
    special_software(report_manager)
    """