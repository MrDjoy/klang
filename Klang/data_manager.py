import pandas as pd
from .baostock_data import BaoStockData
from .data_source_config import use_baostock, use_original
from .common import get_date

class DataManager:
    def __init__(self, freq="d"):
        self.freq = freq
        self._init_data_sources()

    def _init_data_sources(self):
        """根据当前数据源设置初始化数据源"""
        self.baostock_data = BaoStockData(self.freq) if use_baostock() else None
        self.original_data = None  # 原有数据源将在运行时动态导入

    def get_data(self, Kl, code, start_date, end_date):
        if use_baostock():
            # 使用baostock数据源
            return self._get_data_from_baostock(code, start_date, end_date)
        else:
            # 使用原有数据源
            return self._get_data_from_original(Kl, code, start_date, end_date)

    def _get_data_from_baostock(self, code, start_date, end_date):
        """从baostock获取数据"""
        return self.baostock_data.get_data(code, start_date, end_date)

    def _get_data_from_original(self, Kl, code, start_date, end_date):
        """从原有数据源获取数据"""
        # 动态导入原有数据源，避免循环导入
        if self.original_data is None:
            from .data_klang import GetData
            self.original_data = GetData(self.freq)

        return self.original_data.get_data(Kl, code, start_date, end_date)

# 创建全局实例
day_data_manager = DataManager(freq="d")
week_data_manager = DataManager(freq="w")
month_data_manager = DataManager(freq="m")

def set_data_source(source):
    """设置数据源"""
    from .data_source_config import set_data_source
    result = set_data_source(source)
    # 重新初始化所有数据管理器
    day_data_manager._init_data_sources()
    week_data_manager._init_data_sources()
    month_data_manager._init_data_sources()
    return result

def get_data_source():
    """获取当前数据源"""
    from .data_source_config import get_data_source
    return get_data_source()

def shutdown_baostock():
    """关闭baostock连接"""
    if BaoStockData is not None:
        BaoStockData.shutdown()