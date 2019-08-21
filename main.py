# -*- coding: utf-8 -*-
import os
import pickle
import datetime
from flask import Flask
from flask import render_template
from apscheduler.schedulers.background import BackgroundScheduler

from scheduler import scheduler

# scheduler
sched = BackgroundScheduler({'apscheduler.timezone': 'Asia/Seoul'})
@sched.scheduled_job('cron', hour='9')
def timed_job():
    scheduler.run_screener()
    print(f'Schedule job done : {datetime.datetime.now()}')
sched.start()

if not os.path.exists('output.pkl'):
    scheduler.run_screener()

# web server
app = Flask(__name__)

@app.route('/metric_studio', methods=['GET', 'POST'])
def hello_world():
    today = datetime.date.today().strftime('%Y-%m-%d')
    with open('output.pkl', 'rb') as f:
        recomm_df = pickle.load(f)
    if recomm_df is None:
        recomm_html = "There are no recommended items today."
    else:
        recomm_html = recomm_df.to_html()
    return render_template('metric_studio/index.html', recomm_df=recomm_html, today=today)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000, debug=True)