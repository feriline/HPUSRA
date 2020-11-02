import re
import subprocess
from xml.etree.ElementTree import XML
import json

import datetime

from report_manager import ReportManager
from write_to_log_file import write_to_log_file, __init__

DEFAULT_DELTA_TIME = 24*60*60*1000    # milliseconds
EVENT_CONFIG_FILE = 'conf/event_log.json'
EVENT_LIST_FILE = 'conf/events.json'

def load_events_list():
    with open(EVENT_LIST_FILE) as conf_file:
        return json.load(conf_file)


events_list = load_events_list()


def is_in_events_list(event_type, event_source, event_id):
    for event in events_list:
        if event['type'] == event_type and event['source'] == event_source \
            and str(event['id']) == event_id :
            return True
    return False

def get_events(log_type, levels, which_time=None):
    level = ''
    if levels['critical_level']:
        level = 'Level=1 '
    if levels['error_level']:
        if level == '':
            level = 'Level=2 '
        else:
            level += ' or Level=2 '
    if levels['warning_level']:
        if level == '':
            level = 'Level=3'
        else:
            level += ' or Level=3 '

    if level == '':
        return ''
    elif which_time is not None:
        cmd = 'wevtutil qe ' + log_type + ' "/q:*[System[(' \
              + level + ') and TimeCreated[@SystemTime>\'' + \
              str(which_time) + '\']]]" /f:RenderedXML    /e:root'
    else:
        cmd = 'wevtutil qe ' + log_type + ' "/q:*[System[(' \
              + level + ') and TimeCreated[timediff(@SystemTime) <= '+\
              str(DEFAULT_DELTA_TIME)+']]]" /f:RenderedXML    /e:root'

    response = subprocess.run(cmd, stdout=subprocess.PIPE, encoding="437").stdout
    #response = subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode('utf-8')
    return response


# log : [SL] <TimeCreated>  <Type> <Level>  <EventID>  <Source>
def transform_xml_to_text(xml_input, events_statistics):
    event_levels = {
        "1": "Critical",
        "2": "Error",
        "3": "Warning",
        "4": "Information"
    }
    p = re.compile("xmlns='[^']*'")
    xml_input = p.sub('', xml_input)
    root = XML(xml_input)
    for event_element in root.iterfind('Event'):
        time_created = event_element.find('System/TimeCreated').get('SystemTime')
        msg = '\t'+time_created
        type = event_element.findtext('System/Channel')
        msg += '\t'+type
        level = event_element.findtext('System/Level')
        msg += '\t'+event_levels[level]
        event_id = event_element.findtext('System/EventID')
        msg += '\t'+event_id
        # descp = event_element.findtext('RenderingInfo/Message')
        # msg += '\tEventDescription='+descp.split('\n',1)[0]
        provider = event_element.find('System/Provider').get('Name')
        # task_category = event_element.findtext('RenderingInfo/Task')
        # if task_category == '':
        #    msg += '\tTaskCategory=None'
        # else:
        #    msg += '\tTaskCategory='+task_category
        msg += '\t'+provider
        # keywords = event_element.iterfind('RenderingInfo/Keywords/Keyword')
        # msg += '\tKeywords='
        # num_keys = 0
        # for keyword in keywords:
        #    if num_keys > 0:
        #        msg += ',' + keyword.text
        #    else:
        #        msg += keyword.text
        #    num_keys += 1
        # if num_keys == 0:
        #   msg += 'None'
        write_to_log_file("[SL]"+msg)
        # result += '\n'
        if level == '1' or\
                is_in_events_list(type, provider, event_id):
            level_name = event_levels[level]
            if level_name not in events_statistics[type]:
                events_statistics[type][level_name] = []
            events_statistics[type][level_name].append({'id': event_id, 'source': provider,
                                                   'time': time_created})

# the file name used for storing last time of log
TIME_FILE = 'time'


def event_log(report_manager):
    events_statistics = report_manager.get_report_dict()['system_events']
    current_time = datetime.datetime.now()
    try:
        with open(TIME_FILE, 'r') as f:
            start_time = f.read()
    except IOError:
        start_time = None
    with open(TIME_FILE, 'w') as f:
        f.write(str(current_time).replace(' ', 'T')+'Z')
    with open(EVENT_CONFIG_FILE) as json_data_file:
        properties = json.load(json_data_file)
        security_levels = properties['security']
        system_levels = properties['system']
        application_levels = properties['application']
    xml_event_list = get_events('Security', security_levels, start_time)
    if xml_event_list != '':
        transform_xml_to_text(xml_event_list, events_statistics)
    xml_event_list = get_events('System', system_levels, start_time)
    if xml_event_list != '':
        transform_xml_to_text(xml_event_list, events_statistics)
    xml_event_list = get_events('Application', application_levels, start_time,)
    if xml_event_list != '':
        transform_xml_to_text(xml_event_list, events_statistics)


if __name__ == "__main__":
    __init__()
    report_manager = ReportManager()
    event_log(report_manager)
