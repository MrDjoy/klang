#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/11/30 21:34
@Author  : dingyi11@baidu.com
@File    : test_pattern
"""
from Klang.pattern.zigzag_lib import peak_valley_pivots_np
from Klang.pattern import patterns
from Klang import Klang

Klang.Klang_init()
Kl = Klang.Kl
code = Kl.code
date = Kl.date

code('sh.600004')

# 1. 准备数据(假设是收盘价序列)
close_prices = Kl.day_df['close'].values

# 2. 检测关键转折点
pivots = peak_valley_pivots_np(close_prices, step=3)

# 3. 识别特定模式
pv_index = patterns.create_index(pivots)  # 创建索引

# 4. 检查特定模式
if patterns.pattern_cup_handle(Kl.day_df, pivots, pv_index):  # 检查杯柄模式
    print("发现杯柄形态!")