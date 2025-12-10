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

    def get_double_vol_df(self, pd_index: pd.Index) -> pd.DataFrame:
        """
        获取双倍成交量的交易日数据。

        Returns:
            pd.DataFrame: 交易日数据。
        """
        marked_data = self.data.copy()
        marked_data['vol2'] = marked_data.index.isin(pd_index).astype(int)

        return marked_data

    def get_minshipan_by_dvd(self, pd_index: pd.Index, start_date: str, end_date: str) -> pd.DataFrame:
        """
        通过双倍成交量索引找到指定日期区间的所有符合条件的最高价，返回相对最低的那一天数据。

        Returns:
            pd.DataFrame: 最高价相对最低的那一天的完整数据。
        """
        if len(pd_index) == 0:
            return pd.DataFrame()  # 如果没有符合条件的日期，返回空DataFrame

        dvd_data = self.data.loc[pd_index]
        dvd_data = dvd_data[start_date: end_date]

        if len(dvd_data) == 0:
            return pd.DataFrame()  # 如果在指定日期范围内没有符合条件的日期，返回空DataFrame

        # 找到最高价最低的那一天
        return dvd_data[dvd_data['high'] == dvd_data['high'].min()]

    def to_shipan_list(self, shipan_data: pd.DataFrame) -> list:
        """
        将试盘数据转换为列表形式，包括：
        1. 试盘价
        2. 试盘在整个数据中的位置
        3. 试盘类型=2
        4. 试盘日期

        Args:
            shipan_data (pd.DataFrame): 包含试盘信息的DataFrame。

        Returns:
            list: 包含试盘信息的列表。
        """
        shipan_list = []
        if len(shipan_data) == 0:
            return shipan_list
        for index, row in shipan_data.iterrows():
            shipan_list.append(row['high'])
            shipan_list.append(self.data.index.get_loc(index))
            shipan_list.append(2)
            shipan_list.append(index)
            break
        return shipan_list