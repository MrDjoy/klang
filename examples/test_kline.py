#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/12/1 10:57
@Author  : dingyi11@baidu.com
@File    : test_kline
"""
import yfinance as yf
from pyecharts import options as opts
from pyecharts.charts import Kline
from Klang import Klang

Klang.Klang_init()
Kl = Klang.Kl
code = Kl.code
date = Kl.date

start_date='2025-01-01'
end_date='2025-12-01'
date(start_date, end_date)
code('sh.600004')

stock_data = Kl.day_df

print(stock_data)

# 提取 K 线图所需的数据格式
kline_data = []
for index, row in stock_data.iterrows():
    prices = [row[col] for col in ['open', 'close', 'low', 'high']]
    print(f"open: {prices[0]} close: {prices[1]} low: {prices[2]} high: {prices[3]}")
    kline_data.append(prices)

# 配置 Kline 图
kline = (
    Kline()
    .add_xaxis(xaxis_data=stock_data.index.tolist())
    .add_yaxis(series_name="Kline", y_axis=kline_data)
    .set_global_opts(
        xaxis_opts=opts.AxisOpts(is_scale=True),
        yaxis_opts=opts.AxisOpts(is_scale=True),
        title_opts=opts.TitleOpts(title=Kl.cur_name),
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

# 渲染图表
kline.render(f"{Kl.cur_code}_{Kl.cur_name}_{start_date}_{end_date}.html")