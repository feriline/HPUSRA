#!/usr/bin/env python
import datetime
import json
import os
import re

import time


import utility
from categeory_finder import get_category
from report_manager import ReportManager
from write_to_log_file import __init__, write_to_log_file

TIME_INETRVAL = 10 #seconds


# log : [RP] <TimeStamp>  <ApplicationName> <StartTime>  <Interval>
def monitor_working_program_thread(report_manager):
    spent_time = report_manager.get_report_dict()['spent_time']
    previous_active_window_name = utility.get_active_window_name()
    previous_time = datetime.datetime.now()
    while True:
        # print(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        current_active_window_name = utility.get_active_window_name()
        if current_active_window_name != previous_active_window_name:
            current_time = datetime.datetime.now()
            display = previous_active_window_name
            time_diff = (current_time - previous_time).seconds

            software_name = display

            last_index = display.rfind('- ')
            if last_index != -1:
                software_name = display[last_index+2:].strip()

            category = get_category(software_name)
            print(display+' ----'+software_name+'====='+category)
            if category not in spent_time:
                spent_time[category] = time_diff
            else:
                spent_time[category] = spent_time[category] + time_diff
            write_to_log_file(
                "[RP]\t"+str(current_time)+'\t' +
                previous_active_window_name + "\t" + str(previous_time) + '\t' + str(
                    time_diff))

            previous_time = current_time
            previous_active_window_name = current_active_window_name
        # process_list = psutil.process_iter()
        # for any_process in process_list:
        #     try:
        #         # print(                any_process.name())
        #         print(
        #             any_process.name() + '; ' + any_process.username() + '; ' + any_process.status() + '; ' + str(
        #                 any_process.pid))
        #         # if any_process.
        #     except psutil.AccessDenied:
        #         continue
        #         # print('Access to the process list is denied.')

        time.sleep(TIME_INETRVAL)  # seconds


# Thread(target=monitor_working_program_thread).start()

if __name__ == "__main__":
    __init__()
    report_manager = ReportManager()
    monitor_working_program_thread(report_manager)
