# -*- coding: utf-8 -*-

import pandas as pd
import argparse

from crawler import stock_price_daily
from util import mysql_controller
from util import const


def get_company_list():
    _mysql = mysql_controller.MysqlController()
    query = f'''SELECT cmp_cd FROM {const.COMPANY_LIST_TABLE};'''
    return _mysql.select_dataframe(query)


def test():
    sp = stock_price_daily.StockPrice()
    cmp_list = get_company_list()['cmp_cd'].values.tolist()

    result_df = pd.DataFrame([])
    for _cmp in cmp_list[:10]:
        _df = sp.crawl_price(_cmp[1:], '2019-08-29')
        result_df = pd.concat([result_df, _df])
    
    sp.save_price(result_df)
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
    
    cmp_list = ['005930', '012330']

    test()
