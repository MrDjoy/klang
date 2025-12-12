# Alembic 迁移配置说明

## Alembic 如何找到 SQLAlchemy Models

Alembic 通过以下配置发现项目中的 SQLAlchemy 模型：

### 1. `alembic.ini` 配置文件
- **script_location**: 指定迁移脚本目录 (`alembic/`)
- **sqlalchemy.url**: 数据库连接字符串（同步连接）
- **prepend_sys_path**: 将当前目录添加到 Python 路径

### 2. `alembic/env.py` 关键配置
```python
# 导入项目的 Metadata 对象
from app.database import Base
target_metadata = Base.metadata
```

### 3. 依赖关系链
```
alembic migrate →
读取 alembic.ini →
加载 alembic/env.py →
导入 app.database.Base →
识别所有从 Base 继承的 SQLAlchemy 模型
```

## 执行数据库迁移

### 生成迁移脚本
```bash
uv run alembic revision --autogenerate -m "add_time_range_to_monitor_task"
```

### 执行迁移
```bash
uv run alembic upgrade head
```

### 检查迁移状态
```bash
uv run alembic current
```

## 注意事项

1. **时区问题**: Alembic 不支持异步驱动程序，必须使用同步连接
2. **模型导入**: 确保 `app/database.py` 中的 `Base` 正确导入
3. **环境变量**: 确认数据库连接信息正确配置在 `.env` 文件中

## 故障排查

### 如果迁移失败：
1. 检查 `.env` 文件中的数据库连接信息
2. 确认 PostgreSQL 服务正在运行
3. 验证数据库用户有创建表的权限
4. 查看 `alembic/env.py` 中的导入路径是否正确

### Models 变更检测规则：
- 新增/删除表
- 新增/删除字段
- 字段类型变更
- 索引和约束变更