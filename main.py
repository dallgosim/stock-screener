# -*- coding: utf-8 -*-

from screener import screener

if __name__ == '__main__':
    scnr = screener.Screener()
    result_df = scnr.get_recommend_stock()
    print(result_df[['code', 'cmp_nm_kor', 'pred', 'reason_in']])
