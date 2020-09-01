import logging
import datetime

# setup logging
logtime = datetime.datetime.now()
logging.basicConfig(filename='logs/' + str(logtime.year) + str(logtime.month) + str(logtime.day) + '.log',
                    level=logging.DEBUG, format='%(asctime)s %(message)s')
logging.debug('App started')


def log_status(mes):
    """The function records log and prints message to the console"""
    print(mes)
    logging.debug(mes)
