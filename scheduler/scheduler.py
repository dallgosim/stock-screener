# -*- coding: utf-8 -*-
from screener import screener
import pickle


def run_screener():
    scnr = screener.Screener()
    result_df = scnr.get_recommend_stock()
    if result_df is not None:
        with open('output.pkl', 'wb') as f:
            pickle.dump(result_df, f)
