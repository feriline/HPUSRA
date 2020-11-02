import json
from threading import Thread

import pythoncom
import schedule
import time

import logging

from drives_info import get_drives_info
from installed_programs import installed_programs
from report_manager import ReportManager
from system_settings import generate_system_settings
from write_to_log_file import __init__
from event_log import event_log
from network_connection import network_connection
from file_system import file_system, file_statistics
from location_finder import location_finder
from running_processes import monitor_working_program_thread

# dependency : conf/main_controller.json
CONFIG_FILE = 'conf/main_controller.json'


def sensor_schedule():
    # schedule log disabling
    logging.getLogger('schedule').setLevel(logging.CRITICAL + 10)

    def run_threaded(job_func):
        job_thread = Thread(target=job_func, args={report_manager})
        job_thread.start()

    with open(CONFIG_FILE) as config_file:
        properties = json.load(config_file)
        sensors = properties["sensors"]
        time_intervals = properties["time_intervals"]

    if sensors["event_log"]:
        run_threaded(event_log)
        schedule.every(time_intervals["event_log"]).hours.do(run_threaded, event_log)

    if sensors["installed_programs"]:
        run_threaded(installed_programs)
        schedule.every(time_intervals["installed_software"]).hours.do(run_threaded, installed_programs)

    if sensors["drives_info"]:
        run_threaded(get_drives_info)
        schedule.every(time_intervals["drives_info"]).hours.do(run_threaded, get_drives_info)

    while True:
        schedule.run_pending()
        time.sleep(1)


def run():
    __init__()
    global report_manager
    report_manager = ReportManager()
    with open(CONFIG_FILE) as config_file:
        properties = json.load(config_file)
        sensors = properties["sensors"]

    if sensors["file_statistics"]:
        Thread(target=file_statistics, args={report_manager}).start()


    if sensors["location_finder"]:
        Thread(target=location_finder).start()

    if sensors["file_system"]:
        Thread(target=file_system).start()

    if sensors["network_connection"]:
        Thread(target=network_connection, args={report_manager}).start()

    if sensors["running_processes"]:
        Thread(target=monitor_working_program_thread, args={report_manager}).start()

    if sensors["installed_programs"] or sensors["event_log"]\
            or sensors["drives_info"]:
        Thread(target=sensor_schedule).start()

    if sensors["system_setting"]:
        Thread(target=generate_system_settings, args={report_manager}).start()


if __name__ == "__main__":
    run()
