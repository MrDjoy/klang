import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base
import pytest_asyncio

# 延迟导入get_db，避免在测试中直接使用原始版本
def get_original_get_db():
    from app.database import get_db
    return get_db

# 测试数据库配置（使用SQLite内存数据库）
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

TestAsyncSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def override_get_db():
    """覆盖数据库会话"""
    async with TestAsyncSessionLocal() as session:
        try:
            print('🔥 Override: run override_get_db')
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """自动设置和清理测试数据库"""
    # 创建所有表
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 覆盖依赖
    original_get_db = get_original_get_db()
    # 打印当前覆盖状态
    print(f"依赖覆盖前: {app.dependency_overrides}")
    app.dependency_overrides[original_get_db] = override_get_db
    print(f"依赖覆盖后: {app.dependency_overrides}")

    yield

    # 测试结束后删除所有表
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def client():
    """返回测试客户端"""
    # 确保依赖覆盖已设置
    original_get_db = get_original_get_db()
    app.dependency_overrides[original_get_db] = override_get_db

    client = TestClient(app)

    # 验证依赖覆盖
    print(f"TestClient依赖覆盖: {original_get_db in app.dependency_overrides}")
    return client

@pytest.fixture
def sample_trading_plan():
    """返回示例交易计划数据"""
    return {
        "stock_code": "600000",
        "stock_name": "浦发银行",
        "buy_price": 10.5,
        "stop_loss_price": 9.5,
        "take_profit_price": 12.0,
        "quantity": 1000,
        "threshold": 0.01,
        "date_up_rate": 0.05,
        "date_down_rate": 0.03,
        "total_down_rate": 0.05
    }