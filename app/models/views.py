#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
盯盘机器人Web应用 - 数据模型定义
"""
from datetime import datetime, time
from typing import Optional, List
from pydantic import BaseModel, field_validator, SecretStr


class TradingPlanBase(BaseModel):
    """交易计划基础模型"""
    stock_code: str
    stock_name: str
    buy_price: float
    stop_loss_price: float
    take_profit_price: float
    quantity: int
    threshold: float = 0.01
    date_up_rate: float = 0.03
    date_down_rate: float = 0.04
    total_down_rate: float = 0.04
    status: str = "enable"

    @field_validator('threshold', 'date_up_rate', 'date_down_rate', 'total_down_rate', mode='before')
    def round_to_two_decimals(cls, v):
        """将浮点数保留2位小数"""
        if isinstance(v, float):
            return round(v, 2)
        return v


class TradingPlanCreate(TradingPlanBase):
    """创建交易计划模型"""
    pass


class TradingPlanUpdate(TradingPlanBase):
    """更新交易计划模型"""
    pass


class TradingPlanResponse(TradingPlanBase):
    """交易计划响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MonitorTaskBase(BaseModel):
    """盯盘任务基础模型"""
    trading_plan_id: int
    interval_minutes: int = 15
    status: str = "stopped"
    start_time: time = time(9, 30)  # 默认9:30开盘时间
    end_time: time = time(15, 0)    # 默认15:00收盘时间


class MonitorTaskCreate(MonitorTaskBase):
    """创建盯盘任务模型"""
    pass


class MonitorTaskUpdate(MonitorTaskBase):
    """更新盯盘任务模型"""
    pass

class MonitorTaskResponse(MonitorTaskBase):
    """盯盘任务响应模型"""
    id: int
    last_run_time: Optional[datetime] = None
    next_run_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    stock_code: str  # 从关联模型获取
    stock_name: str  # 从关联模型获取

    class Config:
        from_attributes = True


class EmailConfigBase(BaseModel):
    """邮件配置基础模型"""
    smtp_server: str
    smtp_port: int
    sender_email: str
    sender_password: SecretStr
    receiver_email: str
    sender_name: str = "盯盘机器人"
    receiver_name: str = "投资者"


class EmailConfigCreate(EmailConfigBase):
    """创建邮件配置模型"""
    pass


class EmailConfigUpdate(EmailConfigBase):
    """更新邮件配置模型"""
    pass


class EmailConfigResponse(EmailConfigBase):
    """邮件配置响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            SecretStr: lambda v: "***" if v else None
        }


class ExecutionLogResponse(BaseModel):
    """执行日志响应模型"""
    id: int
    task_id: int
    stock_code: str
    execution_time: datetime
    result: str
    signal_type: str
    latest_price: Optional[float] = None
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    volume: Optional[int] = None
    change_rate: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SystemStatusResponse(BaseModel):
    """系统状态响应模型"""
    total_plans: int
    active_tasks: int
    stopped_tasks: int
    last_monitor_time: Optional[datetime] = None
    system_status: str


class PaginationParams(BaseModel):
    """分页参数模型"""
    page: int = 1
    size: int = 20


class PaginatedResponse(BaseModel):
    """分页响应模型"""
    total: int
    page: int
    size: int
    items: List


class ResponseModel(BaseModel):
    """通用响应模型"""
    code: int
    message: str
    data: Optional[dict] = None


# 用于内部监控的数据结构
class StockPriceData(BaseModel):
    """股票价格数据模型"""
    stock_code: str
    latest: float
    open: float
    high: float
    low: float
    volume: int
    change_rate: float
    name: str
    timestamp: datetime


class MonitorSignal(BaseModel):
    """监控信号模型"""
    signal_type: str  # 'buy', 'stop_loss', 'take_profit', 'none'
    stock_code: str
    current_price: float
    target_price: Optional[float] = None
    reason: str
    timestamp: datetime