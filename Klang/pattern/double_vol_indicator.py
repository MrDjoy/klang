#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/12/2 16:59
@Author  : dingyi11@baidu.com
@File    : double_vol_indicator.py
"""

import pandas as pd


class DoubleVolIndicator:
    def __init__(self, data: pd.DataFrame, volthr: int = 2, upthr: float = 1.07, fakeup: bool = True):
        """
        初始化DoubleVolIndicator类实例。

        Args:
            data (pd.DataFrame): 包含收盘价和成交量的数据集。
            volthr (int): 成交量阈值，默认为2倍。
            upthr (float): 涨幅阈值，默认为1.07，即7个点
            fakeup (bool): 是否使用假阳线作为判断标准，默认为True。
        """
        self.data = data
        self.volthr = volthr
        self.upthr = upthr
        self.fakeup = fakeup

    def get_double_vol_days(self) -> pd.Index:
        """
        获取双倍成交量的交易日索引。

        Returns:
            pd.Index: 交易日索引。
        """
        # 预处理数据
        df = self.data.astype({'close': float, 'open': float, 'high': float, 'vol': int})

        # 计算条件
        vol_condition = df['vol'] >= df['vol'].shift(1) * 2
        up_candle = df['close'] > df['open']
        big_up = df['close'] / df['close'].shift(1) >= 1.07
        fake_up = df['high'] / df['open'] >= 1.07

        # 筛选符合条件的日期
        condition = vol_condition & up_candle & big_up
        if self.fakeup:
            condition = vol_condition & up_candle & fake_up

        return df.index[condition]

    def get_double_vol_df(self) -> pd.DataFrame:
        """
        获取双倍成交量的交易日数据。

        Returns:
            pd.DataFrame: 交易日数据。
        """
        marked_data = self.data.copy()
        marked_data['vol2'] = marked_data.index.isin(self.get_double_vol_days()).astype(int)
        return marked_data