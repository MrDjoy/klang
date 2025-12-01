#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/12/1 14:04
@Author  : dingyi11@baidu.com
@File    : recall_stock
"""
import pandas as pd

from Klang import Klang

def recall_stock(start_date=Klang.get_date(14), end_date=Klang.get_date(0), filter688=True, filterST=True):
    Klang.Klang_init()
    kl = Klang.Kl
    code = kl.code
    date = kl.date
    date(start_date, end_date)

    list_a = []
    list_b = []
    for stock in kl.stocklist:
        # 过滤掉ST股票
        if filterST and stock['name'].startswith('*ST'):
            continue
        # 过滤科创版
        if filter688 and stock['code'].startswith('sh.688'):
            continue

        code(stock['code'])

        # 预处理数据
        df = kl.day_df.astype({'close': float, 'open': float, 'high': float, 'vol': int})

        # 计算条件
        vol_condition = df['vol'] >= df['vol'].shift(1) * 2
        up_candle = df['close'] > df['open']
        big_up = df['close'] / df['close'].shift(1) >= 1.07
        fake_up = df['high'] / df['open'] >= 1.07

        # 筛选符合条件的日期
        condition_a = vol_condition & up_candle & big_up
        condition_b = vol_condition & up_candle & ~big_up & fake_up

        for date_idx in df.index[condition_a]:
            print("放量大阳线:", kl.cur_name, kl.cur_code, date_idx)
            list_a.append({'code': kl.cur_code, 'name': kl.cur_name, 'date': date_idx, 'type': 1})

        for date_idx in df.index[condition_b]:
            print("放量假阳线:", kl.cur_name, kl.cur_code, date_idx)
            list_b.append({'code': kl.cur_code, 'name': kl.cur_name, 'date': date_idx, 'type': 2})

    print(f"放量大阳线:{len(list_a)} 放量假阳线:{len(list_b)}")
    return list_a, list_b


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    recall_stock()
