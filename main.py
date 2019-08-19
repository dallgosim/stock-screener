# -*- coding: utf-8 -*-
import os
import pickle
from flask import Flask
from flask import render_template

from scheduler import scheduler

# scheduler.run_screener()

app = Flask(__name__)

@app.route('/metric_studio', methods=['GET', 'POST'])
def hello_world():
    with open('output.pkl', 'rb') as f:
        recomm_df = pickle.load(f)
    return render_template('metric_studio/index.html', recomm_df=recomm_df.to_html())

if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=5000, debug=True)