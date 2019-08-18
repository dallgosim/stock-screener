# -*- coding: utf-8 -*-
import os
import requests
import pandas as pd
import json
from bs4 import BeautifulSoup
import lxml
from util import timer

SISE_URL = 'https://finance.naver.com/item/sise_day.nhn?code={code}&page={page}'

class StockPrice:
    headers = [
        'date', 'close', 'diff', 'open', 'high', 'low', 'volume'
    ]

    def __init__(self, logger, delay=1):
        self.logger = logger
        self.delay = delay

    def __crawl_stock_price(self, stock_code, max_page=250):
        sise_list = []
        page = 1
        last_date = ''
        while page <= max_page:
            _url = SISE_URL.format(code=stock_code, page=page)
            res = requests.get(_url)
            _list = self.__parse_sise_list(res.text)
            sise_list.extend(_list)
            if _list[0][0].startswith('2010.11') or _list[0][0] == last_date:
                break
            last_date = _list[0][0]
            page += 1
            timer.random_sleep(min_delay=self.delay)

        return sise_list

    def __parse_sise_list(self, res_text):
        item_list = []
        soup = BeautifulSoup(res_text, 'lxml')
        box_list = soup.find_all('table', attrs={'class': 'type2'})
        for box in box_list:
            tr = box.find_all('tr')
            for row in tr:
                td = row.find_all('td')
                if len(td) == 7:
                    items = [item.text.strip() for item in td]
                    item_list.append(items)

        return item_list

    def crawl_price(self, cmp_cd, date):
        if date is None:
            date = timer.get_now('%Y-%m-%d')

        if isinstance(cmp_cd, int):
            cmp_cd = '%06d' % cmp_cd
        stock_price = self.__crawl_stock_price(cmp_cd, max_page=1)
        stock_df = pd.DataFrame(stock_price, columns=self.headers)
        stock_df = stock_df.loc[stock_df['date'] != '']
        stock_df['date'] = stock_df['date'].apply(lambda x: x.replace('.', '-'))
        for col in self.headers[1:]:
            stock_df[col] = stock_df[col].apply(lambda x: x.replace(',', ''))

        stock_df = stock_df.head(1)
        stock_df['code'] = cmp_cd
        self.logger.debug(f'''{cmp_cd}'s price length : {(len(stock_df))}''')
        return stock_df
