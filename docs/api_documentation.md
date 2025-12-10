# 自动盯盘机器人Web应用 API接口文档

## 概述
基于FastAPI框架的股票自动盯盘机器人Web应用，提供交易计划管理、盯盘任务管理和邮件配置功能。

## 基础信息
- 基础URL：`http://localhost:8000`
- API前缀：`/api/v1`
- 认证方式：无（简单内部使用）
- 数据格式：JSON

## 响应格式
```json
{
    "code": 200,
    "message": "success",
    "data": {}
}
```

## API接口详情

### 1. 交易计划管理接口

#### 1.1 获取交易计划列表
- **URL**: `GET /api/v1/trading-plans`
- **参数**:
  - `page` (可选): 页码，默认1
  - `size` (可选): 每页数量，默认20
  - `status` (可选): 状态筛选，enable/disable
- **响应**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "total": 100,
        "page": 1,
        "size": 20,
        "items": [
            {
                "id": 1,
                "stock_code": "603338",
                "stock_name": "浙江鼎力",
                "buy_price": 60.73,
                "stop_loss_price": 30.0,
                "take_profit_price": 70.0,
                "quantity": 200,
                "threshold": 0.0,
                "date_up_rate": 0.03,
                "date_down_rate": 0.04,
                "total_down_rate": 0.04,
                "status": "enable",
                "created_at": "2024-01-01 10:00:00",
                "updated_at": "2024-01-01 10:00:00"
            }
        ]
    }
}
```

#### 1.2 创建交易计划
- **URL**: `POST /api/v1/trading-plans`
- **请求体**:
```json
{
    "stock_code": "603338",
    "stock_name": "浙江鼎力",
    "buy_price": 60.73,
    "stop_loss_price": 30.0,
    "take_profit_price": 70.0,
    "quantity": 200,
    "threshold": 0.0,
    "date_up_rate": 0.03,
    "date_down_rate": 0.04,
    "total_down_rate": 0.04
}
```

#### 1.3 更新交易计划
- **URL**: `PUT /api/v1/trading-plans/{plan_id}`
- **请求体**: 同创建接口

#### 1.4 获取单个交易计划
- **URL**: `GET /api/v1/trading-plans/{plan_id}`

#### 1.5 删除交易计划
- **URL**: `DELETE /api/v1/trading-plans/{plan_id}`

#### 1.6 启用/禁用交易计划
- **URL**: `PATCH /api/v1/trading-plans/{plan_id}/status`
- **请求体**:
```json
{
    "status": "enable"  // 或 "disable"
}
```

### 2. 盯盘任务管理接口

#### 2.1 获取盯盘任务列表
- **URL**: `GET /api/v1/monitor-tasks`
- **参数**:
  - `page`, `size` (同交易计划)
  - `status` (可选): running/stopped
- **响应**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "total": 10,
        "page": 1,
        "size": 20,
        "items": [
            {
                "id": 1,
                "trading_plan_id": 1,
                "stock_code": "603338",
                "stock_name": "浙江鼎力",
                "interval_minutes": 15,
                "last_run_time": "2024-01-01 14:30:00",
                "next_run_time": "2024-01-01 14:45:00",
                "status": "running",
                "created_at": "2024-01-01 10:00:00",
                "updated_at": "2024-01-01 14:30:00"
            }
        ]
    }
}
```

#### 2.2 创建盯盘任务
- **URL**: `POST /api/v1/monitor-tasks`
- **请求体**:
```json
{
    "trading_plan_id": 1,
    "interval_minutes": 15
}
```

#### 2.3 启动盯盘任务
- **URL**: `POST /api/v1/monitor-tasks/{task_id}/start`

#### 2.4 停止盯盘任务
- **URL**: `POST /api/v1/monitor-tasks/{task_id}/stop`

#### 2.5 获取任务执行日志
- **URL**: `GET /api/v1/monitor-tasks/{task_id}/logs`
- **参数**: `page`, `size`
- **响应**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "items": [
            {
                "id": 1,
                "task_id": 1,
                "stock_code": "603338",
                "execution_time": "2024-01-01 14:30:00",
                "result": "checked",
                "signal_type": "none",
                "latest_price": 62.5,
                "created_at": "2024-01-01 14:30:00"
            }
        ]
    }
}
```

### 3. 邮件配置管理接口

#### 3.1 获取邮件配置
- **URL**: `GET /api/v1/email-config`

#### 3.2 更新邮件配置
- **URL**: `PUT /api/v1/email-config`
- **请求体**:
```json
{
    "smtp_server": "smtp.qq.com",
    "smtp_port": 587,
    "sender_email": "monitor@example.com",
    "sender_password": "your-auth-code",
    "receiver_email": "user@example.com",
    "sender_name": "盯盘机器人",
    "receiver_name": "投资者"
}
```

#### 3.3 测试邮件配置
- **URL**: `POST /api/v1/email-config/test`

### 4. 系统监控接口

#### 4.1 健康检查
- **URL**: `GET /api/v1/health`

#### 4.2 获取系统状态
- **URL**: `GET /api/v1/status`
- **响应**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "total_plans": 10,
        "active_tasks": 5,
        "stopped_tasks": 2,
        "last_monitor_time": "2024-01-01 14:30:00",
        "system_status": "running"
    }
}
```

## 数据结构定义

### TradingPlan (交易计划)
```python
class TradingPlan(BaseModel):
    id: int
    stock_code: str
    stock_name: str
    buy_price: float
    stop_loss_price: float
    take_profit_price: float
    quantity: int
    threshold: float
    date_up_rate: float
    date_down_rate: float
    total_down_rate: float
    status: str  # enable/disable
    created_at: datetime
    updated_at: datetime
```

### MonitorTask (盯盘任务)
```python
class MonitorTask(BaseModel):
    id: int
    trading_plan_id: int
    stock_code: str
    stock_name: str
    interval_minutes: int
    last_run_time: Optional[datetime]
    next_run_time: Optional[datetime]
    status: str  # running/stopped
    created_at: datetime
    updated_at: datetime
```

### EmailConfig (邮件配置)
```python
class EmailConfig(BaseModel):
    smtp_server: str
    smtp_port: int
    sender_email: str
    sender_password: str
    receiver_email: str
    sender_name: str
    receiver_name: str
    created_at: datetime
    updated_at: datetime
```

### ExecutionLog (执行日志)
```python
class ExecutionLog(BaseModel):
    id: int
    task_id: int
    stock_code: str
    execution_time: datetime
    result: str
    signal_type: str  # none/buy/stop_loss/take_profit
    latest_price: float
    created_at: datetime
```

## 错误码说明
- 200: 成功
- 400: 请求参数错误
- 404: 资源不存在
- 500: 服务器内部错误