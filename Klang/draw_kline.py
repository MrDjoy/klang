#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/12/2 14:11
@Author  : dingyi11@baidu.com
@File    : draw_kline
"""

import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Kline
from pyecharts.charts import Line

class DrawKline:
    def __init__(self, code: str, name: str, stock_data: pd.DataFrame, start_date: str, end_date: str):
        self.code = code
        self.name = name
        self.stock_data = stock_data
        self.start_date = start_date
        self.end_date = end_date
        self.kline = None


    def draw_kline(self):
        # 提取 K 线图所需的数据格式
        kline_data = []
        for index, row in self.stock_data.iterrows():
            prices = [row[col] for col in ['open', 'close', 'low', 'high']]
            print(f"open: {prices[0]} close: {prices[1]} low: {prices[2]} high: {prices[3]}")
            kline_data.append(prices)

        # 配置 Kline 图
        kline = (
            Kline()
            .add_xaxis(xaxis_data=self.stock_data.index.tolist())
            .add_yaxis(series_name="Kline", y_axis=kline_data)
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(is_scale=True),
                yaxis_opts=opts.AxisOpts(is_scale=True),
                title_opts=opts.TitleOpts(title=self.name),
                datazoom_opts=[opts.DataZoomOpts()],
                toolbox_opts=opts.ToolboxOpts(
                    feature={
                        "dataZoom": {"yAxisIndex": "none"},
                        "restore": {},
                        "saveAsImage": {},
                    }
                ),
            )
        )
        self.kline = kline


    def overlap_line(self):
        line = (
            Line()
            .add_xaxis([x[0] for x in m20_data])
            .add_yaxis(
                "",
                [y[1] for y in m20_data],
                linestyle_opts=opts.LineStyleOpts(color="#ff1f19", width=2),
                label_opts=opts.LabelOpts(is_show=False),  # 显式设置 is_show 为 False，尽管这通常是默认的
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="ETF均线折线图"),
                xaxis_opts=opts.AxisOpts(type_="category"),
                yaxis_opts=opts.AxisOpts(name="收盘价",
                                         min_=yaxis_min,  # 设置Y轴最小值
                                         max_=yaxis_max,  # 设置Y轴最大值
                                         splitarea_opts=opts.SplitAreaOpts(is_show=True),
                                         ),
            )
        )