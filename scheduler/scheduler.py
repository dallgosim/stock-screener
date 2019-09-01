# -*- coding: utf-8 -*-
import pickle
import pandas as pd
import datetime

from screener import screener
from crawler import stock_price_daily
from util import const, mysql_controller, timer


def run_screener():
    scnr = screener.Screener(const.MODEL_NAME)
    result_df = scnr.get_recommend_stock()
    with open('output.pkl', 'wb') as f:
        pickle.dump(result_df, f)
    print(f'run_screener job done : {datetime.datetime.now()}')

def get_company_list():
    _mysql = mysql_controller.MysqlController()
    query = f'''SELECT distinct cmp_cd FROM {const.COMPANY_LIST_TABLE};'''
    return _mysql.select_dataframe(query)

def crawl_daily_price():
    sp = stock_price_daily.StockPrice()
    cmp_list = get_company_list()['cmp_cd'].values.tolist()

    today = timer.get_now('%Y-%m-%d')
    result_df = pd.DataFrame([])
    for _cmp in cmp_list:
        _df = sp.crawl_price(_cmp[1:], today)
        result_df = pd.concat([result_df, _df])    
    sp.save_price(result_df)
    print(f'crawl_daily_price job done : {datetime.datetime.now()}')