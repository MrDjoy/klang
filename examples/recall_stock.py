#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/12/1 14:04
@Author  : dingyi11@baidu.com
@File    : recall_stock
"""
import pandas as pd

from Klang import Klang
from Klang.draw_kline import DrawKline
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
        if filterST and (stock['name'].startswith('*ST') or stock['name'].startswith('ST')):
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
    lista, _ = recall_stock(1000)
    # for up_stock in lista:
        # print(up_stock)
        # Klang.Kl.date('2024-06-01', '2025-12-02')
        # Klang.Kl.code(up_stock['code'])
        # day_df = Klang.Kl.day_df
        # v2i = DoubleVolIndicator(day_df, fakeup=True)
        # # 成交量翻倍
        # vol2df = v2i.get_double_vol_df()
        # # 趋势拐点检测
        # qs = QsPatterns(vol2df, 0.1)
        # qs.pattern_detection()
        # qsdf = qs.get_qs_df()
        # shipan = []
        # shipandf = qsdf[qsdf['vol2'] == 1]
        # print(shipandf)
        # shipan.append(shipandf.iloc[-1]['high'])  # 试盘价
        # shipan.append(qsdf.index.get_loc(shipandf.index.values[-1]))  # 试盘在整个数据中位置
        # shipan.append(2)  # 试盘类型
        # shipan.append(shipandf.index.values[-1])  # 日期
        # print(qsdf[qsdf['qs'] != -1])
        # print(shipan)
        # # 试盘成功检测
        # qs.find_success_shipan(shipan)

        # if len(qs.shipan_suc_list) == 6:
        #     dk = DrawKline(Klang.Kl.cur_code, Klang.Kl.cur_name, qsdf, qs.high_low_list, qs.shipan_suc_list)
        #     dk.draw_chart()


