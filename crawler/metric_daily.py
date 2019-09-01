# -*- coding: utf-8 -*-
import os
import requests
import pandas as pd
import json
import datetime
import re
from bs4 import BeautifulSoup
from util import timer, logger, const, mysql_controller

FINANCE_RATIO_URL = 'http://comp.fnguide.com/SVO2/ASP/SVD_FinanceRatio.asp'
INVEST_URL = 'http://comp.fnguide.com/SVO2/ASP/SVD_Invest.asp'


class MetricCrawler:

    # frq, frqTyp => 0:연간, 1:분기
    param = {
        'pGB': 'S7',
        'cID': 'S7',
        'MenuYn': 'N',
        'ReportGB': 'D',
        'NewMenuID': '15',
        'stkGb': '701',
    }

    def __init__(self, delay=1):
        self.logger = logger.APP_LOGGER
        self.delay = delay
        self.mysql = mysql_controller.MysqlController()

    def crawl_fnguide(self, cmp_cd):
        self.logger.debug(f'Fnguide crawling start')

        header = {
            'Host': 'comp.fnguide.com',
        }
        result = []
        cmp_dict = dict()
        gicode = 'A%06d'%int(cmp_cd)
        cmp_dict['code'] = cmp_cd

        for url in [INVEST_URL, FINANCE_RATIO_URL]:
            res = requests.get(f'{url}?gicode={gicode}', headers=header)
            soup = BeautifulSoup(res.text, 'lxml')
            table_list = soup.find_all('table', attrs={'class': 'us_table_ty1'})
            for tb in table_list:
                trs = tb.find_all('tr')[1:]
                for tr in trs:
                    td = list(tr.children)

                    if int(td[1].attrs.get('colspan', 0)) > 0:
                        continue

                    # 지표 key-value
                    key = td[1].find_all('span', attrs={'class': 'txt_acd'})
                    if len(key) > 0:
                        key = key[0].text
                    else:
                        key = td[1].text
                    key = key.strip()

                    val = td[-2].text.strip()
                    if key == 'EV/EBITDA':  # 1년주기여서, 작년기준으로 사용
                        val = td[-4].text.strip()
                    if len(val) > 0:
                        try:
                            cmp_dict[key] = float(val.replace(',', ''))
                        except:
                            pass
        result.append(cmp_dict)

        timer.random_sleep(min_delay=self.delay)

        df_result = pd.DataFrame(result)
        try:
            df_result = df_result[['code', 'EPS', 'CFPS', 'BPS', 'SPS', 'EV/EBITDA', 'ROE']]
        except KeyError:
            self.logger.debug(f"{df_result[['code']]}, KeyError : ['EV/EBITDA'] not in index")
            df_result = None

        self.logger.debug(f'Fnguide crawling complete')
        return df_result
    
    def save_price(self, price_df):
        price_df = price_df.rename(columns={"code": "cmp_cd"})
        self.mysql.insert_dataframe(price_df, const.METRIC_TABLE)
