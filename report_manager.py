import json
import datetime
from threading import Thread
import time
from constants import wlan, vpn, ethernet, DATE_FORMAT

REPORT_FILE_NAME = 'Logs/analyticalData.json'
SAVE_TIME_INTERVAL = 60  #seconds


class ReportManager:
    def __init__(self):
        with open(REPORT_FILE_NAME) as json_data_file:
            self.__report_dict = json.load(json_data_file)

        self.chnage_str_to_datetime()

        self.synch_report_dict()

        thread = Thread(target=self.save_dict)
        thread.start()

    def save_dict(self):
        while True:
            time.sleep(SAVE_TIME_INTERVAL)
            print('saving report to file ---> ')
            current_time = datetime.datetime.now()
            self.__report_dict.update({"last_time": current_time})
            with open(REPORT_FILE_NAME, 'w') as outfile:
                json.dump(self.__report_dict, outfile, default=str, indent=4)

    def get_report_dict(self):
        return self.__report_dict

    def synch_report_dict(self):
        if 'last_time' in self.__report_dict:
            last_saving_time = self.__report_dict['last_time']
            current_time = datetime.datetime.now()
            time_diff = current_time - last_saving_time

            nic_dict = self.__report_dict['nic']
            wlan_dict = nic_dict[wlan]
            ethernet_dict = nic_dict[ethernet]
            vpn_dict = nic_dict[vpn]

            for nic_name in wlan_dict:
                nic = wlan_dict[nic_name]
                if nic['stop'] is None:
                    nic['start'] += time_diff
                else:
                    nic['start'] = current_time
                    nic['stop'] = None

            for nic_name in ethernet_dict:
                nic = ethernet_dict[nic_name]
                if nic['stop'] is None:
                    nic['start'] += time_diff
                else:
                    nic['start'] = current_time
                    nic['stop'] = None

            for nic_name in vpn_dict:
                nic = vpn_dict[nic_name]
                if nic['stop'] is None:
                    nic['start'] += time_diff
                else:
                    nic['start'] = current_time
                    nic['stop'] = None

    @staticmethod
    def str_to_datetime(content):
        return datetime.datetime.strptime(content, DATE_FORMAT)

    def chnage_str_to_datetime(self):
        if 'last_time' in self.__report_dict:
            self.__report_dict['last_time'] =\
                self.str_to_datetime(self.__report_dict['last_time'])

        nic_dict = self.__report_dict['nic']
        wlan_dict = nic_dict[wlan]
        ethernet_dict = nic_dict[ethernet]
        vpn_dict = nic_dict[vpn]

        for nic_name in wlan_dict:
            nic = wlan_dict[nic_name]
            nic['start'] = self.str_to_datetime(nic['start'])
            if nic['stop'] is not None:
                nic['stop'] = self.str_to_datetime(nic['stop'])

        for nic_name in ethernet_dict:
            nic = ethernet_dict[nic_name]
            nic['start'] = self.str_to_datetime(nic['start'])
            if nic['stop'] is not None:
                nic['stop'] = self.str_to_datetime(nic['stop'])

        for nic_name in vpn_dict:
            nic = vpn_dict[nic_name]
            nic['start'] = self.str_to_datetime(nic['start'])
            if nic['stop'] is not None:
                nic['stop'] = self.str_to_datetime(nic['stop'])

    @staticmethod
    def reset():
        report_dict = {
            "nic": {
                "wireless": {},
                "ethernet": {},
                "vpn": {}
            },
            "partitions": [],
            "file_statistics": {},
            "installed_software": {},
            "special_software": {},
            "spent_time": {},
            "system_setting": {},
            "system_events": {"Security":{},"System":{},"Application":{}}
        }

        with open(REPORT_FILE_NAME, 'w') as outfile:
            json.dump(report_dict, outfile, default=str, indent=4)



