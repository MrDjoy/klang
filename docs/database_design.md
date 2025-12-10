# 数据库设计文档

## 数据库选择
- 数据库类型：SQLite（轻量级，适合单机部署）
- 数据库文件：`stock_monitor.db`

## 表结构设计

### 1. trading_plans (交易计划表)
```sql
CREATE TABLE trading_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_code VARCHAR(20) NOT NULL,          -- 股票代码
    stock_name VARCHAR(100) NOT NULL,         -- 股票名称
    buy_price DECIMAL(10, 4) NOT NULL,        -- 买入价格
    stop_loss_price DECIMAL(10, 4) NOT NULL,  -- 止损价格
    take_profit_price DECIMAL(10, 4) NOT NULL,-- 止盈价格
    quantity INTEGER NOT NULL,                -- 购买股数
    threshold DECIMAL(5, 4) DEFAULT 0.0100,   -- 价格阈值
    date_up_rate DECIMAL(5, 4) DEFAULT 0.0300, -- 当日涨幅阈值
    date_down_rate DECIMAL(5, 4) DEFAULT 0.0400, -- 当日跌幅阈值
    total_down_rate DECIMAL(5, 4) DEFAULT 0.0400, -- 持仓亏损阈值
    status VARCHAR(10) DEFAULT 'enable',      -- 状态: enable/disable
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trading_plans_stock_code ON trading_plans(stock_code);
CREATE INDEX idx_trading_plans_status ON trading_plans(status);
```

### 2. monitor_tasks (盯盘任务表)
```sql
CREATE TABLE monitor_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trading_plan_id INTEGER NOT NULL,         -- 关联的交易计划ID
    interval_minutes INTEGER NOT NULL,        -- 执行间隔(分钟)
    last_run_time DATETIME,                   -- 最后执行时间
    next_run_time DATETIME,                   -- 下次执行时间
    status VARCHAR(10) DEFAULT 'stopped',     -- 状态: running/stopped
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trading_plan_id) REFERENCES trading_plans(id) ON DELETE CASCADE
);

CREATE INDEX idx_monitor_tasks_status ON monitor_tasks(status);
CREATE INDEX idx_monitor_tasks_next_run ON monitor_tasks(next_run_time);
```

### 3. email_configs (邮件配置表)
```sql
CREATE TABLE email_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    smtp_server VARCHAR(100) NOT NULL,        -- SMTP服务器
    smtp_port INTEGER NOT NULL,               -- SMTP端口
    sender_email VARCHAR(100) NOT NULL,       -- 发送者邮箱
    sender_password VARCHAR(200) NOT NULL,    -- 发送者授权码(加密存储)
    receiver_email VARCHAR(100) NOT NULL,     -- 接收者邮箱
    sender_name VARCHAR(100) DEFAULT '盯盘机器人', -- 发送者名称
    receiver_name VARCHAR(100) DEFAULT '投资者', -- 接收者名称
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 4. execution_logs (执行日志表)
```sql
CREATE TABLE execution_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,                 -- 任务ID
    stock_code VARCHAR(20) NOT NULL,          -- 股票代码
    execution_time DATETIME NOT NULL,         -- 执行时间
    result VARCHAR(20) NOT NULL,              -- 执行结果: success/failed/checked
    signal_type VARCHAR(20) DEFAULT 'none',   -- 信号类型: none/buy/stop_loss/take_profit
    latest_price DECIMAL(10, 4),              -- 最新的价格
    open_price DECIMAL(10, 4),                -- 开盘价
    high_price DECIMAL(10, 4),                -- 最高价
    low_price DECIMAL(10, 4),                 -- 最低价
    volume BIGINT,                            -- 成交量
    change_rate DECIMAL(5, 2),                -- 涨跌幅
    error_message TEXT,                       -- 错误信息
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES monitor_tasks(id) ON DELETE CASCADE
);

CREATE INDEX idx_execution_logs_task_id ON execution_logs(task_id);
CREATE INDEX idx_execution_logs_execution_time ON execution_logs(execution_time);
CREATE INDEX idx_execution_logs_signal_type ON execution_logs(signal_type);
```

## 字段说明

### trading_plans 表字段说明：
- `threshold`: 价格阈值百分比，如0.01表示1%
- `date_up_rate`: 当日涨幅阈值百分比，超过则触发止盈
- `date_down_rate`: 当日跌幅阈值百分比，超过则触发止损  
- `total_down_rate`: 持仓亏损阈值百分比，超过则触发止损

### monitor_tasks 表字段说明：
- `interval_minutes`: 监控频率，如15表示每15分钟监控一次
- `status`: running - 运行中，stopped - 已停止

## 数据关系
- monitor_tasks.trading_plan_id → trading_plans.id (一对多)
- execution_logs.task_id → monitor_tasks.id (一对多)

## 初始化数据示例

### 交易计划示例：
```sql
INSERT INTO trading_plans (
    stock_code, stock_name, buy_price, stop_loss_price, take_profit_price, 
    quantity, threshold, date_up_rate, date_down_rate, total_down_rate
) VALUES 
('603338', '浙江鼎力', 60.73, 30.0, 70.0, 200, 0.0, 0.03, 0.04, 0.04),
('000001', '平安银行', 12.5, 11.0, 15.0, 1000, 0.01, 0.05, 0.03, 0.05);
```

### 邮件配置示例：
```sql
INSERT INTO email_configs (
    smtp_server, smtp_port, sender_email, sender_password, 
    receiver_email, sender_name, receiver_name
) VALUES (
    'smtp.qq.com', 587, 'monitor@qq.com', 'your-auth-code',
    'user@qq.com', '盯盘机器人', '投资者'
);
```