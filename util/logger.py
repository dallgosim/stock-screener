# -*- coding: utf-8 -*-
import os
import datetime
import logging

LOG_PATH = 'log'
APP_LOGGER = init_logger()

def init_logger(logger_name='logger'):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%m/%d/%Y %I:%M:%S')
    
    # stream
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # dir
    try:
        os.makedirs(LOG_PATH)
    except FileExistsError:
        # directory already exists
        pass

    # file
    log_date = datetime.date.today().strftime('%Y%m%d')
    file_name = f'./{LOG_PATH}/{log_date}.log'
    if not os.path.exists(file_name):
        with open(file_name, 'w') as f:
            f.write('')

    fh = logging.FileHandler(filename=file_name)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger