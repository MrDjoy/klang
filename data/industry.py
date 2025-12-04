#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/12/4 19:04
@Author  : dingyi11@baidu.com
@File    : industry
"""

import akshare as ak
import pandas as pd

# 显示所有列
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)




# stock_industry_df = ak.stock_board_industry_summary_ths()
# stock_industry_df.sort_values(by="净流入", ascending=False, inplace=True)
# print(stock_industry_df)


# stock_board_industry = ak.stock_board_industry_index_ths(symbol="半导体", start_date="20251203", end_date="20251204")
# print(stock_board_industry)


stock_bdt = ak.stock_board_industry_cons_em(symbol="半导体")
print(stock_bdt)

# stock_fd = ak.stock_board_industry_cons_em(symbol="风电")
# print(stock_fd)

stock_robot = ak.stock_board_industry_cons_em(symbol="机器人")
print(stock_robot)

# 减速器