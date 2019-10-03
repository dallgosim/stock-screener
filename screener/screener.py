# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import datetime
import xgboost as xgb
import pickle

from crawler import recommendation_item, stock_price, metric
from util import logger, mysql_controller, timer


class Screener:

    def __init__(self, model_name):
        self.logger = logger.APP_LOGGER
        self.model_name = model_name
        self.model = self._load_model(model_name)
        self.mysql = mysql_controller.MysqlController()
        if self.model is None:
            self.logger.error("The model is not exist. Please check your model name")

    def _load_model(self, model_name):
        model = None
        with open(f'./models/{model_name}.pkl', 'rb') as f:
            model = pickle.load(f)
        return model

    def get_recommend_stock(self, print_cols=['code', 'cmp_nm_kor', 'close', 'pred', 'reason_in']):
        today = datetime.date.today().strftime('%Y-%m-%d')
        in_df = self._recomm_item_crawl(today.replace('-', ''))

        if len(in_df) == 0:
            self.logger.info("There are no recommended items today.")
            return None

        in_df = in_df.drop_duplicates(['cmp_cd'])
        crawl_df = pd.DataFrame([])
        for _, row in in_df.iterrows():
            company = row['cmp_cd']

            # crawl data
            price_df = self._price_crawl(company, today)
            metric_df = self._metric_crawl(company)
            if metric_df is None:
                continue

            result_df = pd.merge(price_df[['code', 'date', 'close']], metric_df, on='code')
            result_df = self._calc_metric(result_df)
            result_df = result_df[['code', 'date', 'close', 'PER', 'PCR', 'PBR', 'PSR', 'EV/EBITDA', 'ROE']]
            crawl_df = pd.concat([crawl_df, result_df])
        result_df = pd.merge(in_df, crawl_df, left_on='cmp_cd', right_on='code')

        # predict
        result_df['pred'], _, _ = self.predict_stock(result_df)
        return result_df[print_cols]

    def daily_recommend_stock(self, print_cols, today=None):
        if today is None:
            query = '''
            SELECT t3.cmp_nm_kor as cmp_nm_kor, m1.*
            FROM
                company_list t3, (SELECT t1.*, t2.close
                FROM metric t1, stock_price t2
                WHERE
                    t1.cmp_cd=t2.cmp_cd
                    AND t1.date=t2.date
                    AND t1.date=(SELECT date
											FROM metric
											ORDER BY date DESC
											LIMIT 1)) m1
            WHERE
                right(t3.cmp_cd,6)=m1.cmp_cd;
            '''
        else:
            query = f'''
            SELECT t3.cmp_nm_kor as cmp_nm_kor, m1.*
            FROM
                company_list t3, (SELECT t1.*, t2.close
                FROM metric t1, stock_price t2
                WHERE
                    t1.cmp_cd=t2.cmp_cd
                    AND t1.date=t2.date
                    AND t1.date="{today}") m1
            WHERE
                right(t3.cmp_cd,6)=m1.cmp_cd;
            '''
            

        # 데이터 가져와서
        _mysql = mysql_controller.MysqlController()
        metric_df = _mysql.select_dataframe(query)
        if len(metric_df) == 0:
            return None

        # infer
        metric_df = self._calc_metric(metric_df)
        metric_df = metric_df[['cmp_cd', 'date', 'close', 'PER', 'PCR', 'PBR', 'PSR', 'EV/EBITDA', 'ROE']]
        metric_df['pred'], metric_df['pos'], metric_df['neg'] = self.predict_stock(metric_df)
        metric_df['model'] = self.model_name
        return metric_df[print_cols]

    def predict_stock(self, metric_df):
        x = metric_df[['PER', 'PBR', 'PSR', 'PCR', 'ROE', 'EV/EBITDA']]
        X_real = xgb.DMatrix(x)

        pred_y = self.model.predict(X_real)
        pred = np.asarray([np.argmax(line) for line in pred_y])
        neg = np.asarray([line[0] for line in pred_y])
        pos = np.asarray([line[1] for line in pred_y])
        return pred, pos, neg

    def _recomm_item_crawl(self, date):
        self.logger.debug('=== item crawling start ===')
        ri = recommendation_item.RecommendationItem(delay=0.1)
        df = ri.crawl_daily_item(date, date)
        return df

    def _price_crawl(self, company, date=None):
        self.logger.debug('=== price crawling start ===')
        sp = stock_price.StockPrice(delay=0.2)
        df = sp.crawl_price(company, date)
        return df

    def _metric_crawl(self, company):
        '''
        crawl 당기 EPS, CFPS, BPS, SPS, ROE, 자산총계
        '''
        self.logger.debug('=== fnguide crawling start ===')
        sp = metric.MetricCrawler(delay=0.1)
        df = sp.crawl_fnguide(company)
        return df

    def _calc_metric(self, df):
        df['close'] = df['close'].astype('int')
        df['PER'] = df['close']/df['EPS']
        df['PCR'] = df['close']/df['CFPS']
        df['PBR'] = df['close']/df['BPS']
        df['PSR'] = df['close']/df['SPS']
        return df

    def save_items(self, recom_df, table):
        if len(recom_df) > 0:
            self.mysql.insert_dataframe(recom_df, table)
