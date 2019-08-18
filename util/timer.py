# -*- coding: utf-8 -*-
import time
import datetime
import random

def random_sleep(min_delay=0.1):
    time.sleep(max(min_delay, random.randrange(1, 9)/10))

def get_now(time_format='%Y-%m-%d %H:%M:%S'):
    return datetime.datetime.now().strftime(time_format)

def str2date(str_date, date_format='%Y-%m-%d'):
    return datetime.datetime.strptime(str_date, date_format)

