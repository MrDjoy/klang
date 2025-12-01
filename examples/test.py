import sys
from pathlib import Path # if you haven't already done so

from examples.test_pattern import close_prices

root = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))


from Klang import (
    C,O,Klang,
    MC,WC,MO,WO,T,WT,MT,
    REF,REFDATE,
    MA,
    SMA,
    HHV,LLV,
    DATE,
    ABS,
    EVERY, EXIST
)
import pandas as pd

pd.set_option('display.max_columns', None)

Klang.Klang_init()

Kl = Klang.Kl

code = Kl.code
date = Kl.date

# 设置为隆基
# code('sh.601012')
# print(C)
#
# print(Kl.day_df)

# # 设置为茅台
# code('sh.600519')
# print(C)
#
# date(start='2025-11-21',end='2025-11-28')
# print(C)
#
#
#显示当天TCL的收盘价
# date(start='2025-11-20',end='2025-12-01')
# code('sh.601566')
# print(C, C[0], C[1], C[2])
# print(Kl.day_df)
# print(Kl.day_df.index)
#
# for i in range(0, len(Kl.day_df)):
#     date = Kl.day_df.index[i]
#     print(date, Kl.day_df['close'].iloc[i], Kl.day_df['close'][date], C.data[date])
#
# print(C.data)
# print(C.data[1], C[1])
#
# close_prices = Kl.day_df['close'].astype(float)[:len(Kl.day_df)]
# print(close_prices.values)
# print(close_prices[0], close_prices[1])
#
# # 系列比，可以计算出每天的涨幅
# print(C.data,C[1].data)
# print(C/C[1])
#
#
# print(REF(C,1))
# print(REFDATE(C,'20210429'))
#
# print(MA(C,5))
# print(SMA(C,5,1))
# print(HHV(C,10))
# print(LLV(C,10))
# print(EVERY(C<O,10))
#
# code('sh.600392')
#
# print(EVERY(C<O,2))
#
# print(ABS(C-O))
#
# print(EXIST(C<O,10))
# print(WC,MC,T,MT[-2],WT[-2])
