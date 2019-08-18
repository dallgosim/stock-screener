# -*- coding: utf-8 -*-
import logging

def init_logger(logger_name='logger'):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%m/%d/%Y %I:%M:%S')
    
    # stream
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # file
    fh = logging.FileHandler(filename='./log/finance.log')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger