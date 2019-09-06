# -*- coding: utf-8 -*-

import pandas as pd
import argparse
import pickle
import datetime

from screener import screener
from crawler import stock_price, stock_price_daily, metric_daily, recommendation_item_daily
from util import mysql_controller
from util import const, timer


def get_company_list():
    _mysql = mysql_controller.MysqlController()
    query = f'''SELECT cmp_cd FROM {const.COMPANY_LIST_TABLE};'''
    return _mysql.select_dataframe(query)


def test():
    scnr = screener.Screener(const.MODEL_NAME)
    result_df = scnr.get_recommend_stock()
    with open('output.pkl', 'wb') as f:
        pickle.dump(result_df, f)
    print(f'run_screener job done : {datetime.datetime.now()}')
    return

def test1():
    sp = stock_price_daily.StockPrice()
    cmp_list = get_company_list()['cmp_cd'].values.tolist()

    result_df = pd.DataFrame([])
    for _cmp in cmp_list[:10]:
        _df = sp.crawl_price(_cmp[1:], '2019-08-29')
        result_df = pd.concat([result_df, _df])
    
    sp.save_price(result_df)
    return

def test2():
    sp = metric_daily.MetricCrawler()
    cmp_list = get_company_list()['cmp_cd'].values.tolist()

    result_df = pd.DataFrame([])
    for _cmp in cmp_list[:10]:
        _df = sp.crawl_fnguide(_cmp[1:])
        result_df = pd.concat([result_df, _df])
    result_df['date'] = timer.get_now('%Y-%m-%d')
    sp.save_price(result_df)
    return


def test3():
    ri = recommendation_item_daily.RecommendationItem()

    # in
    result_df = ri.crawl_daily_item('20190829', '20190829', 1)
    ri.save_price(result_df, const.NAVER_IN_TABLE)

    # out
    result_df = ri.crawl_daily_item('20190829', '20190829', 2)
    ri.save_price(result_df, const.NAVER_OUT_TABLE)
    return
    

def arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', dest='MYSQL_USER', type=str,
                        help='MariaDB user', required=True)
    parser.add_argument('-p', dest='MYSQL_PASSWD', type=str,
                        help='MariaDB password', required=True)
    args = parser.parse_args()

    const.MYSQL_USER = args.MYSQL_USER
    const.MYSQL_PASSWD = args.MYSQL_PASSWD
    return


if __name__ == '__main__':
    arg_parse()

    test3()
