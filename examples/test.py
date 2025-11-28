import sys
from pathlib import Path # if you haven't already done so
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
code('sh.600004')
print(C)
print(Kl.day_df)
# date(start='2025-11-19',end='2025-11-28')
# print(C)
# print(Kl.day_df)

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
