# -*- coding: utf-8 -*-
import os
import requests
import pandas as pd
import json
import datetime
import time
from util import timer, logger, mysql_controller, const

RECOMM_URL = 'https://recommend.wisereport.co.kr/v1/Home/GetInOut'


class RecommendationItem:
    in_cols = [
        'anl_dt', 'brk_cd', 'brk_nm_kor', 'cmp_cd', 'cmp_nm_kor',
        'in_diff_reason', 'in_dt', 'num', 'pf_cd', 'pf_nm_kor',
        'pre_dt', 'reason_in', 'totrow', #'in_adj_price',
        # 'cnt', 'file_nm', 'pre_adj_price',
        # 'recommend_adj_price', 'recomm_price', 'recomm_rate',
        # 'in_dt_crawl',
        'recomm_price'
    ]
    out_cols = [
        'brk_cd', 'cmp_cd', 'pf_cd', 'in_dt', 'out_dt', 'diff_dt',
        'reason_out', 'out_adj_price', 'accu_rtn', 
        # 'out_dt_crawl'
    ]
    param = {
        'startDt': '20190107',
        'endDt': '20190207',
        'brkCd': 0,
        'pfCd': 0,
        'perPage': 20,
        'curPage': 1,
        'proc': 1, #신규추천:1, 추천제외:2
    }

    def __init__(self, delay=1):
        self.logger = logger.APP_LOGGER
        self.delay = delay
        self.mysql = mysql_controller.MysqlController()

    def __crawl(self, date, proc):
        self.logger.debug(f'RecommendationItem crawling {proc} : {date}')

        self.param['startDt'] = date
        self.param['endDt'] = date
        self.param['proc'] = proc
        curr_page = 1
        max_page = 1
        item_df = pd.DataFrame([])
        while curr_page <= max_page:
            self.param['curPage'] = curr_page
            res = requests.post(RECOMM_URL, data=self.param)
            res = json.loads(res.text)
            if len(res['data']) > 0:
                res = res['data']
                res = pd.DataFrame.from_dict(res)
                item_df = pd.concat([item_df, res])
                max_page = int(res['TOTROW'].values[0])
            curr_page += 1
        self.logger.debug(f'RecommendationItem crawl complete {proc}: {date} ({len(item_df)})')

        timer.random_sleep(min_delay=self.delay)
        item_df.columns = map(str.lower, item_df.columns)
        return item_df

    def crawl_daily_item(self, from_date, to_date, proc=1):
        start_date = datetime.datetime.strptime(from_date, '%Y%m%d')
        end_date = datetime.datetime.strptime(to_date, '%Y%m%d') + datetime.timedelta(days=1)
        end_date = end_date.strftime('%Y%m%d')

        i = 0
        _df = pd.DataFrame([])
        while True:
            curr_date = start_date + datetime.timedelta(days=i)
            curr = str(curr_date.date()).replace('-', '')

            if curr == end_date:
                break

            _df = pd.concat([_df, self.__crawl(curr, proc)])
            i += 1

        if len(_df) > 0:
            _df = _df[self.in_cols] if proc==1 else _df[self.out_cols]
        return _df

    def save_price(self, recom_df, table):
        if len(recom_df) > 0:
            self.mysql.insert_dataframe(recom_df, table)
