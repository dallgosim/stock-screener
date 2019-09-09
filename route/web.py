# -*- coding: utf-8 -*-
import datetime
import pickle
from flask import render_template

def hello_world():
    today = datetime.date.today().strftime('%Y-%m-%d')
    # load
    with open('output.pkl', 'rb') as f:
        recomm_df = pickle.load(f)

    if recomm_df is None:
        recomm_html = "There are no recommended items today."
    else:
        recomm_html = recomm_df.to_html(classes='table', header='true')
        recomm_html = recomm_html.replace('\\r\\n', '<br/>')

    return render_template('metric_studio/index.html', recomm_df=recomm_html, today=today)