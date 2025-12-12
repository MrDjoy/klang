#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试 SecretStr 字段隐藏功能"""

from datetime import datetime
from pydantic import BaseModel, SecretStr
from typing import Optional

class EmailConfigResponse(BaseModel):
    """邮件配置响应模型"""
    id: int
    smtp_server: str
    smtp_port: int
    sender_email: str
    sender_password: SecretStr
    receiver_email: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            SecretStr: lambda v: "***" if v else None
        }

# 模拟数据库查询结果
class MockConfig:
    def __init__(self):
        self.id = 1
        self.smtp_server = "smtp.example.com"
        self.smtp_port = 587
        self.sender_email = "sender@example.com"
        self.sender_password = "mysecretpassword"
        self.receiver_email = "receiver@example.com"
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

# 测试
if __name__ == "__main__":
    mock_config = MockConfig()

    # 使用 model_validate 验证
    response = EmailConfigResponse.model_validate(mock_config)

    # 输出隐藏后的结果
    print("=== model_dump() 输出 ===")
    print(response.model_dump())

    print("\n=== model_dump_json() 输出 ===")
    print(response.model_dump_json(indent=2))

    print("\n=== 查看原始值 ===")
    print(f"原始密码值: {response.sender_password.get_secret_value()}")