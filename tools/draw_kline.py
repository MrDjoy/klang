#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/12/2 15:46
@Author  : dingyi11@baidu.com
@File    : test_pyecharts
"""
import pandas as pd

from Klang.draw_kline import DrawKline

from typing import List, Sequence, Union

from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from pyecharts.charts import Kline, Line, Bar, Grid

from Klang import Klang
from Klang.pattern.double_vol_indicator import DoubleVolIndicator
from Klang.pattern.qs_patterns import QsPatterns

pd.set_option('display.max_rows', None)
Klang.Klang_init()
Kl = Klang.Kl
code = Kl.code
date = Kl.date
start_date='2024-06-01'
end_date='2025-12-04'
date(start_date, end_date)
# code('sz.301567')
# code('sz.002046')
# code('sz.002855')
# code('sh.603327')
code('sz.300269')
stock_data = Kl.day_df
print(stock_data)

v2i = DoubleVolIndicator(stock_data, fakeup=True)
# 成交量翻倍
vol2df = v2i.get_double_vol_df()
# 趋势拐点检测
qs = QsPatterns(vol2df, 0.1)
qsdf = qs.pattern_detection2()
# qsdf = qs.get_qs_df()
shipan = []
shipandf = qsdf[qsdf['vol2'] == 1]
print(shipandf)
shipan.append(shipandf.iloc[-1]['high']) # 试盘价
shipan.append(qsdf.index.get_loc(shipandf.index.values[-1])) #试盘在整个数据中位置
shipan.append(2) #试盘类型
shipan.append(shipandf.index.values[-1]) #日期
print(qsdf[qsdf['qs'] != -1])
print(shipan)
# 试盘成功检测
qs.find_success_shipan(shipan)

if __name__ == "__main__":
    # data = split_data(origin_data=echarts_data)
    # data = split_data2(qsdf)
    # draw_chart()
    dk = DrawKline(Kl.cur_code, Kl.cur_name, qsdf, qs.high_low_list, qs.shipan_suc_list)
    dk.draw_chart()
