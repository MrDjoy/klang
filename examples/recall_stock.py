#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/12/1 14:04
@Author  : dingyi11@baidu.com
@File    : recall_stock
"""
import pandas as pd

from Klang import Klang
from Klang.pattern.qs_patterns import QsPatterns
from Klang.pattern.double_vol_indicator import DoubleVolIndicator

def recall_stock(limit:int = 10,start_date=Klang.get_date(14), end_date=Klang.get_date(0), filter688=True, filterST=True):
    Klang.Klang_init()
    kl = Klang.Kl
    Klang.Kl.date(start_date, end_date)

    list_a = []
    list_b = []
    big_up_cnt = 0
    fake_up_cnt = 0
    for stock in kl.stocklist:
        # 过滤掉ST股票
        if filterST and stock['name'].startswith('*ST'):
            continue
        # 过滤科创版
        if filter688 and stock['code'].startswith('sh.688'):
            continue

        Klang.Kl.code(stock['code'])

        v2i = DoubleVolIndicator(kl.day_df)
        v2idf = v2i.get_double_vol_df()

        #valid_indices = v2idf[v2idf['vol2'] == 1].index
        for index, row in v2idf.iterrows():
            if row['vol2'] == 1:
                print("放量日期:", kl.cur_name, kl.cur_code, index)
                list_a.append({'code': kl.cur_code, 'name': kl.cur_name, 'date': index, 'type': 1})
                big_up_cnt += 1

        if big_up_cnt >= limit:
            break

    print(f"放量大阳线:{len(list_a)} 放量假阳线:{len(list_b)}")
    return list_a, list_b


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    lista, _ = recall_stock(10)
    for up_stock in lista:
        print(up_stock)
        Klang.Kl.date('2024-06-01', '2025-12-01')
        Klang.Kl.code(up_stock['code'])
        day_df = Klang.Kl.day_df
        vol2df = DoubleVolIndicator(day_df).get_double_vol_df()
        qs = QsPatterns(vol2df)
        qs.pattern_detection()
        qsdf = qs.get_qs_df()
        print(qsdf)
        # 获取最近试盘点
        shipan = []
        try:
            shipandf = qsdf[qsdf['vol2'] == 1]
            shipan.append(shipandf.iloc[-1]['high'])
            shipan.append(qsdf.index.get_loc(shipandf.index.values[-1]))
            shipan.append(1)
        except KeyError:
            print(f"警告：在{up_stock['code']}中未找到日期{up_stock['date']}")
            exit(1)

        print(f"试盘信息{shipan}")
        list3_2 = qs.find_success_shipan(shipan)


