import logging
from uuid import getnode as get_mac

import os
import socket

import datetime
import requests
import time

from write_to_log_file import __init__, write_to_log_file


def getLocationInfo():
    """
    https://ipdata.co/
    {
        "ip": "37.255.23.128",
        "city": "Isfahan",
        "region": "Isfahan",
        "region_code": "04",
        "country_name": "Iran",
        "country_code": "IR",
        "continent_name": "Asia",
        "continent_code": "AS",
        "latitude": 32.6572,
        "longitude": 51.6776,
        "asn": "AS58085",
        "organisation": "Esfahan Telecommunication Company (P.J.S.)",
        "postal": "",
        "currency": "IRR",
        "currency_symbol": "﷼",
        "calling_code": "98",
        "flag": "https://ipdata.co/flags/ir.png",
        "emoji_flag": "🇮🇷",
        "time_zone": "Asia/Tehran",
        "is_eu": false,
        "suspicious_factors": {
            "is_tor": false
        }
    }
    """
    """
    url = 'https://api.ipdata.co'
    response = requests.get(url).json()
    return response
    """
    """
{'ip': '37.255.23.128', 
'country_code': 'IR', 
'country_name': 'Iran', 
'region_code': '04',
'region_name': 'Isfahan', 
'city': 'Isfahan',
'zip_code': '',
'time_zone': 'Asia/Tehran', 
'latitude': 32.6572,
'longitude': 51.6776, 
'metro_code': 0}
"""

    """
    url = "http://freegeoip.net/json"
    response = requests.get(url).json()
    return response
    """
    """
{'ip': '37.255.23.128',
 'city': 'Isfahan', 
 'region': 'Isfahan',
 'country': 'IR', 
 'loc': '32.6572,51.6776',
  'org': 'AS58085 Esfahan Telecommunication Company (P.J.S.)'}
"""

    url = "https://ipinfo.io"
    response = requests.get(url).json()
    return response


# log : [LF] <TimeStamp>  <ComputerName> <IP>  <MacAddress>  <AccountName>  <CountryName>  <CityName>
def location_finder():
    computer_name= os.environ['COMPUTERNAME']
    account_name = os.getlogin()
    macAddr = get_mac()
    ip_addr = 'UNKNOWN'
    country_name = 'UNKNOWN'
    city_name = 'UNKNOWN'
    try:
        location_info = getLocationInfo()
        ip_addr = location_info['ip']
        country_name = location_info['country']
        city_name = location_info['city']
        if city_name == '':
            city_name = 'UNKNOWN'
    except Exception:
        # print('could not connect to server')
        None

    current_time = datetime.datetime.now()
    write_to_log_file('[LF]\t'+str(current_time) + '\t' + computer_name + '\t' + ip_addr + '\t' + str(macAddr) + '\t' + account_name +
                 '\t' + country_name + '\t' + city_name)


if __name__ == "__main__":
    __init__()
    location_finder()
