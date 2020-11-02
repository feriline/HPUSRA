import copy
import platform
import re
from time import strftime, gmtime

import subprocess

from psutil import sensors_battery

from report_manager import ReportManager

def is_folder_shared():
    cmd = 'net share'
    result = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    lines = result.strip().split('\r\n')
    shared_list = lines[3:len(lines)-1]
    for line in shared_list:
        share_name = re.split('\s+', line)[0]
        if share_name.endswith('$'):
            return 1

    return 0

def get_accounts():
    accounts = []
    cmd = 'net users'
    result = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    lines = result.strip().split('\r\n')
    account_list = lines[3:len(lines)-1]
    for line in account_list:
        accounts_in_line = re.split('\s+', line)
        for account_in_line in accounts_in_line:
            account = account_in_line.strip()
            if account != '':
                accounts.append(account)
    return accounts


def get_active_account():
    accounts = get_accounts()
    active_accounts = []

    for account in accounts:
        cmd = 'net user '+account
        result = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
        lines = result.strip().split('\r\n')
        active = re.split('\s+', lines[5])[2]
        if account == 'Administrator' or account == 'Guest':
            isActive = 'enabled' if active == 'Yes' else 'disabled'
            active_accounts.append(account+':'+isActive)
        if active == 'Yes':
            active_accounts.append(account)

    return active_accounts


def generate_system_settings(report_manager):
    system_settings = report_manager.get_report_dict()['system_setting']
    system_settings.clear()

    computer_type = 'PC'
    if sensors_battery() is not None:
        computer_type = 'Laptop'
    system_settings['computer_type'] = computer_type
    system_settings['os_name'] = platform.system()+' '+platform.release()
    system_settings['os_version'] = platform.version()
    system_settings['user_accounts'] = get_active_account()
    system_settings['shared_folders'] = is_folder_shared()
    system_settings['time_zone'] = strftime("%z", gmtime())
    #system_settings['windows_update'] = 0

    #print(system_settings)




if __name__ == "__main__":
    report_manager = ReportManager()
    generate_system_settings(report_manager)
    #print(is_folder_shared())