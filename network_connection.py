import json
import re
import socket

import datetime
import psutil
import time

import subprocess

from constants import wlan, vpn, ethernet
from report_manager import ReportManager
from write_to_log_file import __init__, write_to_log_file
# dependency  conf/network.json
CONFIG_FILE = 'conf/network.json'

af_map = {
    socket.AF_INET: 'IPv4',
    socket.AF_INET6: 'IPv6',
    psutil.AF_LINK: 'MAC',
}


def bytes2human(n):
    """
     bytes2human(10000)
    '9.8 K'
     bytes2human(100001221)
    '95.4 M'
    """
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.2f%s' % (value, s)
    return '%.2fB' % (n)


interface_name_re = re.compile(r"^Name\s*:\s*(?P<name>.+)$")

regexps = [
    re.compile(r"^Physical address\s*:\s*(?P<physical_addr>.+)$"),
    re.compile(r"^State\s*:\s*(?P<state>.+)$"),
    re.compile(r"^SSID\s*:\s*(?P<ssid>.+)$"),
    re.compile(r"^Authentication\s*:\s*(?P<auth_protocol>.+)$"),
    re.compile(r"^Profile\s*:\s*(?P<profile>.+)$")
]


def get_wlan_info():
    cmd = 'netsh wlan show interfaces'
    result = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    interfaces = []
    lines = result.split('\n')
    for line in lines:
        line = line.strip()
        interface_name = interface_name_re.search(line)
        if interface_name is not None:
            interfaces.append(interface_name.groupdict())
            interfaces[-1].update({'type': wlan})
            continue
        for expression in regexps:
            result = expression.search(line)
            if result is not None:
                interfaces[-1].update(result.groupdict())
                break
    return interfaces


def load_virtual_net_vendors():
    with open(CONFIG_FILE) as config_file:
        properties = json.load(config_file)
        return properties["virtaul_net_vendors"]


virtual_net_vendors = load_virtual_net_vendors()


def get_nic_info():
    nic_list= get_wlan_info()
    nic_stat= psutil.net_if_stats()
    nic_addresses = psutil.net_if_addrs()

    for nic_name in nic_stat:
        if nic_name.startswith('Loopback'):
            continue

        is_virtual_net=False
        for addr in nic_addresses[nic_name]:
            if addr.family == psutil.AF_LINK:
                if addr.address[:8] in virtual_net_vendors:
                    is_virtual_net = True
                    break
        if is_virtual_net:
            continue

        found = False
        for nic in nic_list:
            if nic_name == nic['name']:
                found = True
                break
        if not found:
            con_type = ethernet
            if 'vpn' in nic_name.lower() or 'tunnel' in nic_name.lower():
                con_type = vpn
            nic_list.append({'name': nic_name, 'type':con_type})

    return nic_list


# log : [NC] <TimeStamp>  <InterfaceName> <Status> <IP>  <SSID> <Authentication_Type>
def network_connection(report_manager):
    time_interval = 10 # seconds

    nic_dict = report_manager.get_report_dict()['nic']
    wlan_dict = nic_dict[wlan]
    ethernet_dict = nic_dict[ethernet]
    vpn_dict = nic_dict[vpn]

    before_stats = psutil.net_if_stats()
    nic_addresses = psutil.net_if_addrs()
    nic_list = get_nic_info()
    for nic in nic_list:
        nic_name = nic['name']
        current_time = datetime.datetime.now()
        if before_stats[nic_name].isup:


            if nic['type'] == wlan:
                curr_dict = wlan_dict
                last_ssid = nic['ssid']
            elif nic['type'] == ethernet:
                curr_dict = ethernet_dict
            else:
                curr_dict = vpn_dict

            if nic['type'] == wlan:
                name = nic['ssid']
            else:
                name = nic_name

            if name not in curr_dict:
                curr_dict[name] = {"duration": 0,
                                            "start": current_time,
                                            "stop": None}

            msg = str(current_time)+'\t'+nic['type']+'\t'+ nic_name+'\tconnected'
            for addr in nic_addresses[nic_name]:
                if addr.family == socket.AF_INET:
                    msg += '\t'+addr.address
                    break
            if nic['type'] == wlan:
                msg += '\t'+nic['ssid']+'\t'+nic['auth_protocol']

            print(nic_dict)
            write_to_log_file('[NC]\t' + msg)

    while True:
        time.sleep(time_interval)
        nic_list = get_nic_info()
        after_stats = psutil.net_if_stats()
        nic_addresses = psutil.net_if_addrs()
        for nic in nic_list:
            nic_name = nic['name']
            if nic_name not in before_stats or\
                    after_stats[nic_name].isup != before_stats[nic_name].isup:
                is_up = after_stats[nic_name].isup
                current_time = datetime.datetime.now()

                if nic['type'] == wlan:
                    curr_dict = wlan_dict
                elif nic['type'] == ethernet:
                    curr_dict = ethernet_dict
                else:
                    curr_dict = vpn_dict

                if not is_up and nic_name in before_stats:
                    if nic['type'] == wlan:
                        #diff_time = current_time - curr_dict[last_ssid]["start"]
                        curr_dict[last_ssid]["duration"] += time_interval
                        curr_dict[last_ssid]["stop"] = current_time
                    else:
                        #diff_time = current_time - curr_dict[nic_name]["start"]
                        curr_dict[nic_name]["duration"] += time_interval
                        curr_dict[nic_name]["stop"] = current_time
                elif is_up:
                    if nic['type'] == wlan:
                        name = nic['ssid']
                        last_ssid = name
                    else:
                        name = nic_name

                    if name not in curr_dict:
                        curr_dict[name] = {"duration": 0,
                                                    "start": current_time,
                                                    "stop": None}
                    else:
                        curr_dict[name]["start"] = current_time
                        curr_dict[name]["stop"] = None

                msg = str(current_time)+'\t'+nic['type']+'\t'+nic_name+'\t'+('connected' if is_up else 'disconnected')
                if is_up:
                    for addr in nic_addresses[nic_name]:
                        if addr.family == socket.AF_INET:
                            msg += '\t' + addr.address
                            break
                    if nic['type'] == wlan:
                        msg += '\t' + nic['ssid'] + '\t' + nic['auth_protocol']

                print(nic_dict)

                write_to_log_file('[NC]\t'+msg)

            else:
                is_up = after_stats[nic_name].isup
                if is_up:
                    current_time = datetime.datetime.now()
                    if nic['type'] == wlan:
                        curr_dict = wlan_dict
                    elif nic['type'] == ethernet:
                        curr_dict = ethernet_dict
                    else:
                        curr_dict = vpn_dict

                    if nic['type'] == wlan:
                        if nic['ssid'] != last_ssid:
                            print(last_ssid+'---->'+nic['ssid'])
                            msg = str(current_time) + '\t' + nic['type'] + '\t' + last_ssid + '\tdisconnected'
                            write_to_log_file('[NC]\t' + msg)
                            msg = str(current_time) + '\t' + nic['type'] + '\t' + nic['ssid'] + '\tconnected'
                            write_to_log_file('[NC]\t' + msg)
                            #diff_time = current_time - curr_dict[last_ssid]["start"]
                            curr_dict[last_ssid]["duration"] += time_interval
                            curr_dict[last_ssid]["stop"] = current_time

                            name = nic['ssid']
                            if name not in curr_dict:
                                curr_dict[name] = {"duration": 0,
                                                   "start": current_time,
                                                   "stop": None}
                            else:
                                curr_dict[name]["start"] = current_time
                                curr_dict[name]["stop"] = None

                            last_ssid = name
                            print(curr_dict)

                        else:
                            curr_dict[last_ssid]["duration"] += time_interval
                    else:
                        curr_dict[nic_name]["duration"] += time_interval

        #print(nic_dict)
        before_stats = after_stats


if __name__ == '__main__':
    __init__()
    report_manager = ReportManager()
    network_connection(report_manager)




