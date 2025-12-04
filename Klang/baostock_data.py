import baostock as bs
import pandas as pd
import os
from threading import Lock
from .common import get_date

class BaoStockData:
    def __init__(self, freq="d"):
        self.freq = freq
        self._logged_in = False
        self.lock = Lock()

    def _ensure_login(self):
        if not self._logged_in:
            with self.lock:
                if not self._logged_in:
                    lg = bs.login()
                    if lg.error_code != '0':
                        raise Exception(f"Baostock登录失败: {lg.error_msg}")
                    self._logged_in = True

    def get_data(self, code, start_date, end_date, json=False):
        self._ensure_login()

        # 映射频率
        freq_map = {"d": "d", "w": "w", "m": "m"}
        frequency = freq_map.get(self.freq, "d")

        # 查询数据
        fields = "date,open,high,low,close,volume,turn,amount"
        rs = bs.query_history_k_data_plus(
            code, fields,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
            adjustflag="3"
        )

        if rs.error_code != '0':
            raise Exception(f"Baostock查询失败: {rs.error_msg}")

        df = rs.get_data()

        print(f"{code} {rs}")
        # 转换数据类型
        for col in ['open', 'high', 'low', 'close', 'volume', 'turn']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # 设置索引
        df = df.set_index('date')

        if json:
            # 返回Python对象而不是JSON字符串，避免转义问题
            js = df.reset_index().to_dict(orient="records")
            return js

        return df

    @staticmethod
    def shutdown():
        bs.logout()