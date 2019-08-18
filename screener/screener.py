# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import datetime
import xgboost as xgb
import pickle

from crawler import recommendation_item, stock_price, metric
import util.logger


class Screener:

    def __init__(self):
        self.logger = util.logger.init_logger(__file__)

        model_name = 'metricstudio_xgb_20190730_626'
        self.model = self._load_model(model_name)
        if self.model is None:
            self.logger.error("The model is not exist. Please check your model name")

    def get_recommend_stock(self):
        today = datetime.date.today().strftime('%Y-%m-%d')
        in_df = self._recomm_item_crawl(today.replace('-', ''))
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
            crawl_df = pd.concat([crawl_df, result_df])
        result_df = pd.merge(in_df, crawl_df, left_on='cmp_cd', right_on='code')

        # predict
        result_df['pred'] = self._predict_stock(result_df)
        return result_df

    def _load_model(self, model_name):
        model = None
        with open(f'./models/{model_name}.pkl', 'rb') as f:
            model = pickle.load(f)
        return model

    def _recomm_item_crawl(self, date):
        self.logger.debug('=== item crawling start ===')
        ri = recommendation_item.RecommendationItem(self.logger, delay=0.1)
        df = ri.crawl_daily_item(date, date)
        return df

    def _predict_stock(self, metric_df):
        x = metric_df[['PER', 'PBR', 'PSR', 'PCR', 'ROE', 'EV/EBITDA']]
        X_real = xgb.DMatrix(x)

        pred_y = self.model.predict(X_real)
        pred_y = np.asarray([np.argmax(line) for line in pred_y])[0]
        return pred_y

    def _price_crawl(self, company, date=None):
        self.logger.debug('=== price crawling start ===')
        sp = stock_price.StockPrice(self.logger, delay=0.2)
        df = sp.crawl_price(company, date)
        return df

    def _metric_crawl(self, company):
        '''
        crawl 당기 EPS, CFPS, BPS, SPS, ROE, 자산총계
        '''
        self.logger.debug('=== fnguide crawling start ===')
        sp = metric.MetricCrawler(self.logger, delay=0.1)
        df = sp.crawl_fnguide(company)
        return df

    def _calc_metric(self, df):
        df['close'] = df['close'].astype('int')
        df['PER'] = df['close']/df['EPS']
        df['PCR'] = df['close']/df['CFPS']
        df['PBR'] = df['close']/df['BPS']
        df['PSR'] = df['close']/df['SPS']
        return df[['code', 'date', 'close', 'PER', 'PCR', 'PBR', 'PSR', 'EV/EBITDA', 'ROE']]
