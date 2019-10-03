# -*- coding: utf-8 -*-
import datetime
import pickle
from flask import render_template

from util import const, mysql_controller, timer

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

def get_recom_list():
    query = '''
    SELECT ttt1.*, ROUND(ttt2.pos, 3) as pos, ROUND(ttt2.neg, 3) as neg, ttt2.pred
    FROM
        (SELECT tt1.*, tt2.open as price
        FROM
            (SELECT t1.cmp_cd, t1.cmp_nm_kor, t1.brk_nm_kor, t1.pf_nm_kor,
                    t1.in_dt, t1.reason_in
                    FROM naver_in_items t1
                    LEFT JOIN naver_out_items t2
                    ON
                        t1.cmp_cd = t2.cmp_cd
                        AND t1.brk_cd = t2.brk_cd
                        AND t1.pf_cd = t2.pf_cd
                    WHERE t2.cmp_cd IS NULL) as tt1,
                stock_price as tt2
            WHERE tt1.cmp_cd=tt2.cmp_cd
                AND tt1.in_dt=tt2.date) ttt1,
        recommended_items ttt2
    WHERE
        ttt1.cmp_cd=ttt2.cmp_cd
        AND ttt1.in_dt=ttt2.date
    ORDER BY in_dt DESC;
    '''
    _mysql = mysql_controller.MysqlController()
    recomm_df = _mysql.select_dataframe(query)
    if recomm_df is None:
        recomm_html = "There are no recommended items today."
    else:
        recomm_html = recomm_df.to_html(classes='table', header='true')
        recomm_html = recomm_html.replace('\\r\\n', '<br/>')

    today = datetime.date.today().strftime('%Y-%m-%d')
    return render_template('metric_studio/index.html', recomm_df=recomm_html, today=today)
