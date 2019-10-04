# -*- coding: utf-8 -*-
import pickle
import pandas as pd
import datetime

from screener import screener
from crawler import stock_price_daily, metric_daily, recommendation_item_daily
from util import const, mysql_controller, timer


def run_screener():
    scnr = screener.Screener(const.MODEL_NAME)
    result_df = scnr.get_recommend_stock()
    with open('output.pkl', 'wb') as f:
        pickle.dump(result_df, f)
    print(f'run_screener job done : {datetime.datetime.now()}')
    infer_model()

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

def crawl_daily_metric():
    sp = metric_daily.MetricCrawler()
    cmp_list = get_company_list()['cmp_cd'].values.tolist()

    result_df = pd.DataFrame([])
    for _cmp in cmp_list:
        _df = sp.crawl_fnguide(_cmp[1:])
        result_df = pd.concat([result_df, _df])
    result_df['date'] = timer.get_now('%Y-%m-%d')
    sp.save_price(result_df)
    print(f'crawl_daily_metric job done : {datetime.datetime.now()}')

def crawl_daily_inout():
    today = timer.get_now('%Y%m%d')
    ri = recommendation_item_daily.RecommendationItem()

    # in
    result_df = ri.crawl_daily_item(today, today, 1)
    ri.save_price(result_df, const.NAVER_IN_TABLE)

    # out
    result_df = ri.crawl_daily_item(today, today, 2)
    ri.save_price(result_df, const.NAVER_OUT_TABLE)
    print(f'crawl_daily_in/out job done : {datetime.datetime.now()}')

def infer_model():
    scnr = screener.Screener(const.MODEL_NAME)
    cols = ['cmp_cd', 'close', 'pos', 'neg', 'pred', 'model', 'date']
    recom_df = scnr.daily_recommend_stock(print_cols=cols)
    if recom_df is not None:
        scnr.save_items(recom_df, const.MODEL_RECOMMEND_TABLE)
    print(f'infer model job done : {datetime.datetime.now()}')

def test():
    # 현재 추천종목만 보기
    '''SELECT t1.*
        FROM naver_in_items t1
        LEFT JOIN naver_out_items t2
        ON
            t1.cmp_cd = t2.cmp_cd
            AND t1.brk_cd = t2.brk_cd
            AND t1.pf_cd = t2.pf_cd
        WHERE t2.cmp_cd IS NULL;'''