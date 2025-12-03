#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/12/2 14:11
@Author  : dingyi11@baidu.com
@File    : draw_kline
"""
from typing import List, Sequence, Union
import pandas as pd
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from pyecharts.charts import Kline, Line, Bar, Grid

class DrawKline:
    def __init__(self, code: str, name: str, stock_data: pd.DataFrame,
                 high_low_list: list, shipan_suc_list: list, html_path: str = "D:/klang_data"):
        self.code = code
        self.name = name
        self.stock_data = stock_data
        self.start_date = stock_data.index.values[0]
        self.end_date = stock_data.index.values[-1]
        self.data = self.split_data()
        self.high_low_list = high_low_list
        self.shipan_suc_list = shipan_suc_list
        self.path = html_path

    def split_data(self) -> dict:
        # 时间
        data_pd = self.stock_data
        times = data_pd.index.values.tolist()
        # 成交量
        vols = data_pd['vol'].values.tolist()
        # 价格数据
        datas = []
        for index, row in data_pd.iterrows():
            prices = [row[col] for col in ['open', 'close', 'low', 'high', 'vol', 'vol2']]
            # print(f"open: {prices[0]} close: {prices[1]} low: {prices[2]} high: {prices[3]}")
            datas.append(prices)
        return {
            "datas": datas,
            "times": times,
            "vols": vols
        }

    def split_shipan_data(self) -> Sequence:
        mark_line_data = []
        p = self.shipan_suc_list
        for i in range(len(p)):
            j = i + 1
            if j >= len(p):
                break
            mark_line_data.append(
                [
                    {
                        "xAxis": p[i][1],
                        "yAxis": float(p[i][0]),
                        # "value": vols, # 线上面值？
                    },
                    {
                        "xAxis": p[j][1],
                        "yAxis": float(p[j][0]),
                    },
                ]
            )
        return mark_line_data

    def split_qushi_data(self) -> Sequence:
        mark_point_data = []
        p = self.high_low_list
        for i in range(len(p)):
            # mark_point_data.append({
            #     "x": p[i][1],
            #     "y": float(p[i][0]),
            #     "name": "拐点"
            # })
            # mark_point_data.append(opts.MarkPointItem(x=p[i][1], y=float(p[i][0]), name="x"))
            mark_point_data.append(opts.MarkPointItem(coord=[p[i][1], float(p[i][0])], name="拐点"))
        return mark_point_data

    def calculate_ma(self, day_count: int):
        result: List[Union[float, str]] = []

        for i in range(len(self.data["times"])):
            if i < day_count:
                result.append("-")
                continue
            sum_total = 0.0
            for j in range(day_count):
                sum_total += float(self.data["datas"][i - j][1])
            result.append(abs(float("%.2f" % (sum_total / day_count))))
        return result

    def draw_chart(self):
        kline = (
            Kline()
            .add_xaxis(xaxis_data=self.data["times"])
            .add_yaxis(
                series_name="",
                y_axis=self.data["datas"],
                itemstyle_opts=opts.ItemStyleOpts(
                    color="#ef232a",
                    color0="#14b143",
                    border_color="#ef232a",
                    border_color0="#14b143",
                ),
                markpoint_opts=opts.MarkPointOpts(
                    label_opts=opts.LabelOpts(
                        position="middle", color="blue", font_size=15
                    ),
                    # data=[
                    #     opts.MarkPointItem(type_="max", name="最大值"),
                    #     opts.MarkPointItem(type_="min", name="最小值"),
                    # ]
                    data=self.split_qushi_data(),
                    symbol="triangle",
                    symbol_size=5,
                ),
                markline_opts=opts.MarkLineOpts(
                    label_opts=opts.LabelOpts(
                        position="middle", color="blue", font_size=15
                    ),
                    data=self.split_shipan_data(),
                    symbol="circle",
                ),
            )
            .set_series_opts(
                markarea_opts=opts.MarkAreaOpts(is_silent=True, data=self.split_shipan_data())
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title=self.code + self.name, pos_left="0"),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    is_scale=True,
                    boundary_gap=False,
                    axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                    splitline_opts=opts.SplitLineOpts(is_show=False),
                    split_number=20,
                    min_="dataMin",
                    max_="dataMax",
                ),
                yaxis_opts=opts.AxisOpts(
                    is_scale=True, splitline_opts=opts.SplitLineOpts(is_show=True)
                ),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="line"),
                datazoom_opts=[
                    opts.DataZoomOpts(
                        is_show=False, type_="inside", xaxis_index=[0, 0], range_end=100
                    ),
                    opts.DataZoomOpts(
                        is_show=True, xaxis_index=[0, 1], pos_top="97%", range_end=100
                    ),
                    opts.DataZoomOpts(is_show=False, xaxis_index=[0, 2], range_end=100),
                ],
                # 三个图的 axis 连在一块
                # axispointer_opts=opts.AxisPointerOpts(
                #     is_show=True,
                #     link=[{"xAxisIndex": "all"}],
                #     label=opts.LabelOpts(background_color="#777"),
                # ),
            )
        )

        kline_line = (
            Line()
            .add_xaxis(xaxis_data=self.data["times"])
            .add_yaxis(
                series_name="MA5",
                y_axis=self.calculate_ma(day_count=5),
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(opacity=0.5),
                label_opts=opts.LabelOpts(is_show=False),
            )
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    grid_index=1,
                    axislabel_opts=opts.LabelOpts(is_show=False),
                ),
                yaxis_opts=opts.AxisOpts(
                    grid_index=1,
                    split_number=3,
                    axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                    axistick_opts=opts.AxisTickOpts(is_show=False),
                    splitline_opts=opts.SplitLineOpts(is_show=False),
                    axislabel_opts=opts.LabelOpts(is_show=True),
                ),
            )
        )
        # Overlap Kline + Line
        overlap_kline_line = kline.overlap(kline_line)

        # Bar-1
        bar_1 = (
            Bar()
            .add_xaxis(xaxis_data=self.data["times"])
            .add_yaxis(
                series_name="Volumn",
                y_axis=self.data["vols"],
                xaxis_index=1,
                yaxis_index=1,
                label_opts=opts.LabelOpts(is_show=False),
                # 根据 echarts demo 的原版是这么写的
                # itemstyle_opts=opts.ItemStyleOpts(
                #     color=JsCode("""
                #     function(params) {
                #         var colorList;
                #         if (data.datas[params.dataIndex][1]>data.datas[params.dataIndex][0]) {
                #           colorList = '#ef232a';
                #         } else {
                #           colorList = '#14b143';
                #         }
                #         return colorList;
                #     }
                #     """)
                # )
                # 改进后在 grid 中 add_js_funcs 后变成如下
                itemstyle_opts=opts.ItemStyleOpts(
                    color=JsCode(
                        """
                    function(params) {
                        var colorList;
                        if (barData[params.dataIndex][1] > barData[params.dataIndex][0]) {
                            colorList = '#ef232a';
                            if (params.dataIndex > 0) {
                                var currentData = barData[params.dataIndex];
                                var prevData = barData[params.dataIndex - 1];
                                if (currentData[5] == 1) {
                                    colorList = '#FFD700';
                                }
                            }
                        } else {
                            colorList = '#14b143';
                        }
                        return colorList;
                    }
                    """
                    )
                ),
            )
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    grid_index=1,
                    axislabel_opts=opts.LabelOpts(is_show=False),
                ),
                legend_opts=opts.LegendOpts(is_show=False),
            )
        )

        # Bar-2 (Overlap Bar + Line)
        # bar_2 = (
        #     Bar()
        #     .add_xaxis(xaxis_data=data["times"])
        #     .add_yaxis(
        #         series_name="MACD",
        #         y_axis=data["macds"],
        #         xaxis_index=2,
        #         yaxis_index=2,
        #         label_opts=opts.LabelOpts(is_show=False),
        #         itemstyle_opts=opts.ItemStyleOpts(
        #             color=JsCode(
        #                 """
        #                     function(params) {
        #                         var colorList;
        #                         if (params.data >= 0) {
        #                           colorList = '#ef232a';
        #                         } else {
        #                           colorList = '#14b143';
        #                         }
        #                         return colorList;
        #                     }
        #                     """
        #             )
        #         ),
        #     )
        #     .set_global_opts(
        #         xaxis_opts=opts.AxisOpts(
        #             type_="category",
        #             grid_index=2,
        #             axislabel_opts=opts.LabelOpts(is_show=False),
        #         ),
        #         yaxis_opts=opts.AxisOpts(
        #             grid_index=2,
        #             split_number=4,
        #             axisline_opts=opts.AxisLineOpts(is_on_zero=False),
        #             axistick_opts=opts.AxisTickOpts(is_show=False),
        #             splitline_opts=opts.SplitLineOpts(is_show=False),
        #             axislabel_opts=opts.LabelOpts(is_show=True),
        #         ),
        #         legend_opts=opts.LegendOpts(is_show=False),
        #     )
        # )

        # line_2 = (
        #     Line()
        #     .add_xaxis(xaxis_data=data["times"])
        #     .add_yaxis(
        #         series_name="DIF",
        #         y_axis=data["difs"],
        #         xaxis_index=2,
        #         yaxis_index=2,
        #         label_opts=opts.LabelOpts(is_show=False),
        #     )
        #     .add_yaxis(
        #         series_name="DIF",
        #         y_axis=data["deas"],
        #         xaxis_index=2,
        #         yaxis_index=2,
        #         label_opts=opts.LabelOpts(is_show=False),
        #     )
        #     .set_global_opts(legend_opts=opts.LegendOpts(is_show=False))
        # )
        # 最下面的柱状图和折线图
        # overlap_bar_line = bar_2.overlap(line_2)

        # 最后的 Grid
        grid_chart = Grid()

        # 这个是为了把 data.datas 这个数据写入到 html 中,还没想到怎么跨 series 传值
        # demo 中的代码也是用全局变量传的
        grid_chart.add_js_funcs("var barData = {}".format(self.data["datas"]))

        # K线图和 MA5 的折线图
        grid_chart.add(
            overlap_kline_line,
            grid_opts=opts.GridOpts(pos_left="3%", pos_right="1%", height="60%"),
        )
        # Volumn 柱状图
        grid_chart.add(
            bar_1,
            grid_opts=opts.GridOpts(
                pos_left="3%", pos_right="1%", pos_top="71%", height="10%"
            ),
        )
        # MACD DIFS DEAS
        # grid_chart.add(
        #     overlap_bar_line,
        #     grid_opts=opts.GridOpts(
        #         pos_left="3%", pos_right="1%", pos_top="82%", height="14%"
        #     ),
        # )
        grid_chart.render(f"{self.path}/{self.code}_{self.name}_{self.start_date}_{self.end_date}K线.html")
        print(f"生成k线图成功: {f'{self.path}/{self.code}_{self.name}_{self.start_date}_{self.end_date}K线.html'}")
