import json
import os
import re
import string
import time
import datetime

import copy
from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler
from watchdog.events import DirCreatedEvent
from watchdog.events import DirDeletedEvent
from watchdog.events import DirModifiedEvent
from watchdog.events import DirMovedEvent

from report_manager import ReportManager
from write_to_log_file import __init__, write_to_log_file
# dependency : conf/file_system.json
# dependency : conf/file_extensions.json
FILE_SYS_CONFIG_FILE= 'conf/file_system.json'
EXTENSIONS_CONFIG_FILE = 'conf/file_extensions.json'

# log : [SL] <TimeStamp>  <ComputerName> <AccountName>  <FilePath>  <File/Folder>  <Event>
def file_action_log(action):
    current_time = datetime.datetime.now()
    msg = str(current_time) + '\t' + computer_name + \
          '\t' + account_name + '\t' + action
    write_to_log_file('[FS]\t' + msg)


class MyHandler(RegexMatchingEventHandler):

    def on_created(self, event):
        type1 = 'file'
        if type(event) is DirCreatedEvent:
            type1 = 'folder'
        action = event.src_path+'\t'+type1+'\tcreated'
        file_action_log(action)

    def on_deleted(self, event):
        type1 = 'file'
        if type(event) is DirDeletedEvent:
            type1 = 'folder'
        action = event.src_path+'\t'+type1+'\tdeleted'
        file_action_log(action)

    # Called when a file or a directory is moved or renamed.
    def on_moved(self, event):
        type1 = 'file'
        if type(event) is DirMovedEvent:
            type1 = 'folder'
        action = event.src_path+'\t'+type1+'\tmoved'+event.dest_path
        file_action_log(action)

    # Called when a file or directory is modified.
    def on_modified(self, event):
        type1 = 'file'
        if type(event) is DirModifiedEvent:
            type1 = 'folder'
        action = event.src_path+'\t'+type1+' modified'
        file_action_log(action)


def get_drives():
    return ['%s:\\' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]

def load_patterns():
    with open(FILE_SYS_CONFIG_FILE) as config_file:
        properties = json.load(config_file)
        ignore_directories = properties['ignore_directory']
        include_pattern = properties['include'].replace('\\', '\\\\').\
                                                replace(';', '|')
        exclude_pattern = properties['exclude'].replace('\\', '\\\\').\
                                                replace(';', '|')
        exclude_extension_categories = properties['exclude_extension_categories'].split(';')

    with open(EXTENSIONS_CONFIG_FILE) as extensions_file:
        extension = "("
        extensions_list = json.load(extensions_file)
        for category in extensions_list:
            if category['category'] not in exclude_extension_categories:
                for extension_item in category['extensions']:
                    extension += extension_item+"|"

        extension = extension.rstrip("|")+")"
    log_file_pattern = '.*log$'
    if exclude_pattern == '':
        ignore_pattern = [log_file_pattern]
    else:
        ignore_pattern = [r'('+log_file_pattern+'|.*('+exclude_pattern+').*)']
    include_pattern = [r'.*('+include_pattern+').*\\.'+extension+'$']

    return {"include_pattern":include_pattern,
            "ignore_pattern": ignore_pattern,
            "ignore_directories": ignore_directories,
            "categories": extensions_list}


def file_system():
    #file_statistics_dict = report_manager.get_report_dict()['fileStatistics']

    global computer_name
    computer_name = os.environ['COMPUTERNAME']
    global account_name
    account_name = os.getlogin()

    pattern_dict = load_patterns()
    include_pattern = pattern_dict["include_pattern"]
    ignore_pattern = pattern_dict["ignore_pattern"]
    ignore_directories = pattern_dict["ignore_directories"]

    observer = Observer()

    for path in get_drives():
        event_handler = MyHandler(regexes=include_pattern,ignore_regexes=ignore_pattern, ignore_directories=ignore_directories)
        observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


def get_file_statistics(root_path, include_paths, exclude_paths):
    for path, subdirs, files in os.walk(root_path):
        for exclude_dir in exclude_paths:
            exclude_pat = re.compile(exclude_dir,re.IGNORECASE)
            for dir in subdirs:
                subdir_path = os.path.join(path, dir)
                if exclude_pat.match(subdir_path):
                    subdirs.remove(dir)
        fsnodes = []
        fsnodes.extend(files)
        for name in fsnodes:
            for include_path in include_paths:
                include_pat = re.compile(include_path, re.IGNORECASE)
                file_path = os.path.join(path, name)
                if include_pat.match(file_path):
                    yield file_path
                    break

def get_category(categories, file_extension):
    for category in categories:
        for extension  in category['extensions']:
            if extension == file_extension:
                return category['category']
    return 'UNKNOWN'


def file_statistics(report_manager):
    file_stat_main = report_manager.get_report_dict()['file_statistics']
    file_stat_main.clear()

    file_stat = {}
    pattern_dict = load_patterns()
    categories = pattern_dict["categories"]
    include_pattern = pattern_dict["include_pattern"]
    ignore_pattern = pattern_dict["ignore_pattern"]

    for path in get_drives():
        for file_path in get_file_statistics(root_path=path, include_paths=include_pattern,
                                             exclude_paths=ignore_pattern):
            file_name, extension = os.path.splitext(file_path)
            category = get_category(categories, extension.lstrip('.').lower())
            if category not in file_stat:
                file_stat.update({category: 1})
            else:
                file_stat[category]=file_stat[category]+1


    report_manager.get_report_dict()['file_statistics'] = copy.deepcopy(file_stat)


if __name__ == "__main__":
    __init__()
    report_manager = ReportManager()
    file_statistics(report_manager)






