# -*- coding: utf-8 -*-

from screener import screener

if __name__ == '__main__':
    scnr = screener.Screener()
    result_df = scnr.get_recommend_stock()
    if result_df is not None:
        print(result_df)
