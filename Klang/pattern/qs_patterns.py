#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/12/1 20:42
@Author  : dingyi11@baidu.com
@File    : qs_patterns.py
"""

import pandas as pd

class QsPatterns:

    def __init__(self, data: pd.DataFrame, zf: float = 0.1):
        self.data = data
        self.zf = zf
        self.max_high = 0
        self.min_low = 0
        self.high_low_list = []
        self.current_qs = None
        # self.m = 0
        # self.n = 0


    def pattern_detection(self):
        m = 0
        n = 0
        for i in range(len(self.data)):
            if not self.current_qs:
                if i == 0:
                    self.max_high = self.data['high'].values[i]
                    self.min_low = self.data['low'].values[i]
                else:
                    if self.data['high'].values[i] > self.max_high:
                        self.max_high = self.data['high'].values[i]
                        m = i
                    elif self.data['low'].values[i] < self.min_low:
                        self.min_low = self.data['low'].values[i]
                        n = i
                    if m > n:
                        # 判断是否满足增幅条件，更新为上升趋势
                        if (self.max_high - self.min_low) / self.min_low > self.zf:
                            self.current_qs = 'up'
                            self.high_low_list.append([self.min_low, n, 0])
                        else:
                            # donothing
                            pass
                    if m < n:
                        if (self.max_high - self.min_low) / self.max_high > self.zf:
                            self.current_qs = 'down'
                            self.high_low_list.append([self.max_high, m, 1])
                        else:
                            # donothing
                            pass
            else:
                if self.current_qs == 'up':
                    if self.data['high'].values[i] > self.max_high:
                        self.max_high = self.data['high'].values[i]
                        m = i
                    else:
                        # 判断是否扭转上升趋势
                        if (self.max_high - self.data['low'].values[i]) / self.max_high > self.zf:
                            self.current_qs = 'down'
                            self.high_low_list.append([self.max_high, m, 1])
                            self.min_low = self.data['low'].values[i]
                            n = i
                        else:
                            # donothing
                            pass
                elif self.current_qs == 'down':
                    if self.data['low'].values[i] < self.min_low:
                        self.min_low = self.data['low'].values[i]
                        n = i
                    else:
                        # 判断是否扭转下降趋势
                        if (self.data['high'].values[i] - self.min_low) / self.min_low > self.zf:
                            self.current_qs = 'up'
                            self.high_low_list.append([self.min_low, n, 0])
                            self.max_high = self.data['high'].values[i]
                            m = i
                        else:
                            # donothing
                            pass
        if self.high_low_list[-1][1] < m:
            self.high_low_list.append([self.max_high, m, 1])
        elif self.high_low_list[-1][1] < n:
            self.high_low_list.append([self.min_low, n, 0])

        return self.high_low_list

    def find_success_shipan(self, shipan: list):
        """
        找3-2浪
        1.找到趋势中最低点，前面跌幅达到40%以上，记录为0点
        2.从最低点开始，找到比它高的点，高点涨幅满足15%-35%，如果后续有更高的点更新，记录为1高
        3.一高点和试盘点之间，遍历高点，高点价格小于一高和试盘价，记录二高，二高可能有多个，记录成列表
        """
        list3_2 = []
        if shipan is None or len(shipan) < 2:
            print(f'试盘参数不满足要求 {shipan}')
            return
        if len(self.high_low_list) < 3:
            print('记录点不足3个，无法形成3浪')
            return
        zero_point = self.find_lowest_index()
        # 判断跌幅满足40%
        highest_fall = max(self.high_low_list[:zero_point[1]], key=lambda x: x[0])
        if (highest_fall[0] - zero_point[0]) / highest_fall[0] < 0.4:
            print(f'跌幅不足40%，无法形成3浪 零点{zero_point} 前高{highest_fall}')
            return

        # 确定1高
        list1 = self.high_low_list[zero_point[1]:]
        one_high = None
        for i in range(len(list1)):
            if list1[i][2] == 1 and (list1[i][0] - zero_point[0]) / zero_point[0] > 0.15:
                if one_high is None:
                    one_high = list1[i]
                elif list1[i][0] > one_high[0]:
                    one_high = list1[i]
                    if (list1[i][0] - zero_point[0]) / zero_point[0] > 0.35:
                        print(f"一高涨幅过大 {one_high}")

        list2 = self.high_low_list[one_high[1]:]
        # 根据试盘的索引找前面的B点
        shipan_index = shipan[1]
        b_low_index = 0
        for j in range(len(list2)):
            b_low_index = b_low_index + 1
            if list2[j][1] >= shipan_index:
                break
        b_low = list2[b_low_index]
        if b_low[2] != 0:
            print(f"试盘点{shipan}在{b_low}上升浪中")

        if one_high[1] <= b_low[1]:
            print("一高点不在试盘点之前")
            return

        # 确定二高
        tow_high_list = []
        for k in range(one_high[1], b_low[1]):
            if self.high_low_list[k][2] == 1:
                if self.high_low_list[k][0] < one_high[0]:
                    tow_high_list.append(self.high_low_list[k])

        if not tow_high_list:
            print("没有找到二高点")
            return

        for two_high in tow_high_list:
            if shipan[0] > two_high[0]:
                # 往前遍历找二高前的A点
                a_low = None
                for l in range(two_high[1], one_high[1], -1):
                    if self.high_low_list[l][2] == 0:
                        a_low = self.high_low_list[l]
                        break
                if a_low is None:
                    print(f"没有找到A点 零点{zero_point} 一高{one_high} 二高{two_high} B点{b_low} 试盘{shipan} ")
                    return

                print(f"试盘成功，零点{zero_point} 一高{one_high} A点{a_low} 二高{two_high} B点{b_low} 试盘{shipan}")
                list3_2.append(zero_point)
                list3_2.append(one_high)
                list3_2.append(a_low)
                list3_2.append(two_high)
                list3_2.append(b_low)
                list3_2.append(shipan)
                break

        return list3_2


    def find_lowest_index(self):
        """
        找到列表中最小的价格对应的索引
        :return: 最低价格子列表
        """
        if not self.high_low_list:
            return None

        # 使用min函数找到包含最低价格的子列表
        # 每个子列表是[价格, 索引]，所以比较第一个元素（价格）
        lowest_item = min(self.high_low_list, key=lambda x: x[0])

        return lowest_item

    def find_highest_index(self):
        """
        找到列表中最高价格对应的索引
        :return: 最高价格子列表
        """
        if not self.high_low_list:
            return None

        highest_item = max(self.high_low_list, key=lambda x: x[0])
        return highest_item

    def get_price_statistics(self):
        """
        获取价格统计信息
        :return: 包含最低价、最高价及其索引的字典
        """
        if not self.high_low_list:
            return None

        lowest_item = min(self.high_low_list, key=lambda x: x[0])
        highest_item = max(self.high_low_list, key=lambda x: x[0])

        return {
            'lowest_price': lowest_item[0],
            'lowest_index': lowest_item[1],
            'highest_price': highest_item[0],
            'highest_index': highest_item[1],
            'price_range': highest_item[0] - lowest_item[0]
        }