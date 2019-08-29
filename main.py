# -*- coding: utf-8 -*-
import os
import datetime
import argparse
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

from util import const
from scheduler import scheduler
from route import web


# scheduler
weekday = 'mon-fri'
sched = BackgroundScheduler({'apscheduler.timezone': 'Asia/Seoul'})
sched.add_job(scheduler.run_screener, 'cron', day=weekday, hour='9')
sched.add_job(scheduler.crawl_daily_price, 'cron', day=weekday, hour='23')
sched.start()

# web server
app = Flask(__name__)
app.add_url_rule('/metric_studio', view_func=web.hello_world, methods=['GET'])


def arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', dest='MYSQL_USER', type=str,
                        help='MariaDB user', required=True)
    parser.add_argument('-p', dest='MYSQL_PASSWD', type=str,
                        help='MariaDB password', required=True)
    parser.add_argument('--model', dest='MODEL_NAME', type=str,
                        help='Name of model for prediction',
                        default='metricstudio_xgb_20190816_kospi.pkl')
    args = parser.parse_args()

    const.MODEL_NAME = args.MODEL_NAME
    const.MYSQL_USER = args.MYSQL_USER
    const.MYSQL_PASSWD = args.MYSQL_PASSWD
    return args


if __name__ == '__main__':
    args = arg_parse()

    if not os.path.exists('output.pkl'):
        scheduler.run_screener()

    app.debug = True
    app.run(host='0.0.0.0', port=5000, debug=True)
