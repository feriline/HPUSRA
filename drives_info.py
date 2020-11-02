import re

import psutil
import subprocess

from report_manager import ReportManager
from write_to_log_file import __init__
drive_name_re = re.compile(r"^Volume\s(.+?)\s")
bitlocker_version_re = re.compile(r"^BitLocker Version:\s+(.+?)$")


def get_bitlocker_drives_list():
    bitlocker_drives = []
    cmd = 'manage-bde -status'
    result = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout.read().decode('utf-8')

    lines = result.split('\n')

    for line in lines:
        line = line.strip()
        drive_name_s = drive_name_re.search(line)
        if drive_name_s is not None:
            last_drive = drive_name_s.group(1)
            continue

        bitlocker_s = bitlocker_version_re.search(line)
        if bitlocker_s is not None:
            bitlocker_version = bitlocker_s.group(1)
            if bitlocker_version != 'None':
                bitlocker_drives.append(last_drive)

    return bitlocker_drives


def get_drives_info(report_manager):
    partitions_dict = report_manager.get_report_dict()['partitions']
    partitions_dict[:] = []
    drives = psutil.disk_partitions()

    bitlocker_drives = get_bitlocker_drives_list()
    for drive in drives:
        if drive.opts != 'cdrom':
            drive_name = drive.device.rstrip(r'\\')
            has_bitlocker = 0
            if drive_name in bitlocker_drives:
                has_bitlocker = 1

            partitions_dict.append({'drive_name': drive_name,
                                    'file_system': drive.fstype,
                                    'bitlocker': has_bitlocker})

    #print(partitions_dict)


if __name__ == "__main__":
    report_manager = ReportManager()
    get_drives_info(report_manager)
