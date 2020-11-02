import logging
import os
import datetime


def __init__():
    log = logging.getLogger()  # root logger
    for handler in log.handlers[:]:  # remove all old handlers
        log.removeHandler(handler)
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        filename=os.path.dirname(os.path.abspath(__file__)) + '\\Logs\\report-' + str(
            datetime.datetime.now().strftime('%Y-%m-%d')
        ) + '.log',
        datefmt='[%d/%b/%Y %H:%M:%S]'
    )
    if os.path.exists(os.path.dirname(os.path.abspath(__file__)) + '\\Logs\\report-' + str(
            (datetime.datetime.now() - datetime.timedelta(days=60)).strftime('%Y-%m-%d')) + '.log'):
        os.remove(os.path.dirname(os.path.abspath(__file__)) + '\\Logs\\report-' + str(
            (datetime.datetime.now() - datetime.timedelta(days=60)).strftime('%Y-%m-%d')) + '.log')


def write_to_log_file(the_message):
    #aes_object = AES.new('the key')
    logging.info(
        #aes_object.encrypt(the_message.decode('utf-8').rstrip())
        the_message
    )
    return
