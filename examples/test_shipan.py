#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/12/2 19:15
@Author  : dingyi11@baidu.com
@File    : test_shipan
"""
from Klang import Klang
from Klang.pattern.double_vol_indicator import DoubleVolIndicator
from Klang.pattern.qs_patterns import QsPatterns


Klang.Klang_init()
Kl = Klang.Kl
code = Kl.code
date = Kl.date
start_date='2024-06-01'
end_date='2025-11-28'
date(start_date, end_date)
code('sz.301567')
# code('sz.002046')
# code('sz.002855')
stock_data = Kl.day_df
print(stock_data)


v2i = DoubleVolIndicator(stock_data, fakeup=True)
vol2df = v2i.get_double_vol_df()
qs = QsPatterns(vol2df, 0.1)
qs.pattern_detection()
qsdf = qs.get_qs_df()

shipan = []
shipandf = qsdf[qsdf['vol2'] == 1]
print(shipandf)
shipan.append(shipandf.iloc[-1]['high'])
shipan.append(qsdf.index.get_loc(shipandf.index.values[-1]))
shipan.append(1)
shipan.append(shipandf.index.values[-1])
print(qsdf[qsdf['qs'] != -1])
print(shipan)

qs.find_success_shipan(shipan)