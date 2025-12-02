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
                            self.high_low_list.append([self.min_low, n, 0, self.data.index[n]])
                        else:
                            # donothing
                            pass
                    if m < n:
                        if (self.max_high - self.min_low) / self.max_high > self.zf:
                            self.current_qs = 'down'
                            self.high_low_list.append([self.max_high, m, 1, self.data.index[m]])
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
                            self.high_low_list.append([self.max_high, m, 1, self.data.index[m]])
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
                            self.high_low_list.append([self.min_low, n, 0, self.data.index[n]])
                            self.max_high = self.data['high'].values[i]
                            m = i
                        else:
                            # donothing
                            pass
        if self.high_low_list[-1][1] < m:
            self.high_low_list.append([self.max_high, m, 1, self.data.index[m]])
        elif self.high_low_list[-1][1] < n:
            self.high_low_list.append([self.min_low, n, 0, self.data.index[n]])

        return self.high_low_list


    def get_qs_df(self):
        marked_data = self.data.copy()
        marked_data['qs'] = -1
        indexs = [item[1] for item in self.high_low_list]
        tags = [item[2] for item in self.high_low_list]
        marked_data['qs'].values[indexs] = tags
        return marked_data


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
        zero_point = self.find_lowest()
        # 判断跌幅满足40%
        list0 = self.high_low_list[:self.index(zero_point)]
        highest_fall = max(list0, key=lambda x: x[0])
        fall_zf = (highest_fall[0] - zero_point[0]) / highest_fall[0]
        if fall_zf < 0.4:
            print(f'最低点跌幅不足40%，零点{zero_point} 前高{highest_fall} 跌幅{fall_zf}')
            zero_point, highest_fall = self.find_fall_zf_max()
            if zero_point is None:
                print('没有找到跌幅超过40%的最低点')
                return
        print(f"确定零点{zero_point} 前高{highest_fall}")
        # 确定1高
        # 按照索引从零点向后遍历，找到比零点高的点，高点价格涨幅满足15%-100%，如果后续有更高的点更新，记录为1高
        list1 = self.high_low_list[self.index(zero_point):]
        one_high = None
        for i in range(len(list1)):
            if list1[i][2] == 1 and (list1[i][0] - zero_point[0]) / zero_point[0] > 0.15:
                if one_high is None:
                    one_high = list1[i]
                elif list1[i][0] > one_high[0]:
                    one_high = list1[i]
                    zf = (list1[i][0] - zero_point[0]) / zero_point[0]
                    if zf > 1:
                        print(f"一高涨幅过大 {one_high} : {zf}")
                # elif list1[i][0] < one_high[0]:
                #     # 趋势下降
                #     break

        print(f"确定一高{one_high}")
        list2 = self.high_low_list[self.index(one_high):]
        # 根据试盘的索引找前面的B点
        shipan_index = shipan[1]
        b_low = None
        for j in range(len(list2)-1, -1, -1):
            if list2[j][1] < shipan_index:
                b_low = list2[j]
                break

        if b_low is None:
            print("没有找到B点")
            return

        print(f"确定B点{b_low}")

        if b_low[2] != 0:
            print(f"试盘点{shipan}在{b_low}上升浪中")

        if one_high[1] > shipan[1]:
            print("一高点不在试盘点之前")
            return

        # 确定二高
        tow_high_list = []
        for k in range(self.index(one_high), self.index(b_low)):
            if self.high_low_list[k][2] == 1:
                if self.high_low_list[k][0] < one_high[0]:
                    tow_high_list.append(self.high_low_list[k])

        if not tow_high_list:
            print("没有找到二高点")
            return

        print(f'可能二高{tow_high_list}')

        for two_high in tow_high_list:
            if shipan[0] > two_high[0]:
                # 往前遍历找二高前的A点
                a_low = None
                for l in range(self.index(two_high), self.index(one_high), -1):
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

    def index(self, point: list):
        try:
            index = self.high_low_list.index(point)
        except ValueError:
            print(f"点{point}不在高低点列表中")
            return None
        return index

    def find_lowest(self):
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

    def find_fall_zf_max(self):
        """
        找到列表中跌幅最大的价格对应点
        """
        if not self.high_low_list:
            return None

        max_fall_zf = 0
        find_lower_point = None
        find_higher_point = None

        for i, point in enumerate(self.high_low_list):
            if point[2] != 0:  # 只处理低点(point[2] == 0)
                continue

            # 确保前面有高点用于计算跌幅
            if i == 0:
                continue

            # 找到当前点之前的所有高点
            previous_highs = [item for item in self.high_low_list[:i] if item[2] == 1]
            if not previous_highs:
                continue

            highest_fall = max(previous_highs, key=lambda x: x[0])
            fall_zf = (highest_fall[0] - point[0]) / highest_fall[0]

            if fall_zf > max_fall_zf:
                max_fall_zf = fall_zf
                find_lower_point = point
                find_higher_point = highest_fall

        print(f'重新确认零点{find_lower_point} 前高{find_higher_point} 最大跌幅{max_fall_zf} ')
        return find_lower_point, find_higher_point


    def find_highest(self):
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