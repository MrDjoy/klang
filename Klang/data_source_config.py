import os
import json

class DataSourceConfig:
    def __init__(self):
        self.config_file = os.path.expanduser("~/.klang/data_source_config.json")
        self._load_config()

    def _load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except:
                self.config = {"data_source": "original"}  # 默认使用原有数据源
        else:
            self.config = {"data_source": "original"}
            self._save_config()

    def _save_config(self):
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def set_data_source(self, source):
        allowed_sources = ["original", "baostock"]
        if source not in allowed_sources:
            raise ValueError(f"数据源必须是: {allowed_sources}")

        self.config["data_source"] = source
        self._save_config()

    def get_data_source(self):
        return self.config.get("data_source", "original")

    def use_baostock(self):
        return self.get_data_source() == "baostock"

    def use_original(self):
        return self.get_data_source() == "original"

# 全局配置实例
_config = DataSourceConfig()

def set_data_source(source):
    """设置数据源"""
    return _config.set_data_source(source)

def get_data_source():
    """获取当前数据源"""
    return _config.get_data_source()

def use_baostock():
    """是否使用baostock数据源"""
    return _config.use_baostock()

def use_original():
    """是否使用原始数据源"""
    return _config.use_original()