#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
邮件配置管理API路由
"""
from datetime import datetime
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.database import get_db
from app.models.views import EmailConfigCreate, EmailConfigUpdate, ResponseModel
from app.models.models import EmailConfig

router = APIRouter()


@router.get("/email-config", response_model=ResponseModel)
async def get_email_config():
    """获取邮件配置"""
    try:
        async with get_db() as session:
            stmt = select(EmailConfig).order_by(EmailConfig.id.desc()).limit(1)
            result = await session.execute(stmt)
            config = result.scalar_one_or_none()

        if not config:
            return ResponseModel(
                code=200,
                message="success",
                data=None
            )

        # 隐藏敏感信息
        config_dict = config.__dict__
        if 'sender_password' in config_dict:
            config_dict['sender_password'] = '***'  # 密码字段隐藏

        return ResponseModel(
            code=200,
            message="success",
            data=config_dict
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取邮件配置失败: {str(e)}")
    finally:
        pass  # 异步会话会自动关闭


@router.put("/email-config", response_model=ResponseModel)
async def update_email_config(config: EmailConfigUpdate):
    """更新邮件配置"""
    try:
        async with get_db() as session:
            # 检查是否存在配置
            stmt = select(EmailConfig).order_by(EmailConfig.id.desc()).limit(1)
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                # 更新现有配置
                existing.smtp_server = config.smtp_server
                existing.smtp_port = config.smtp_port
                existing.sender_email = config.sender_email
                existing.sender_password = config.sender_password
                existing.receiver_email = config.receiver_email
                existing.sender_name = config.sender_name
                existing.receiver_name = config.receiver_name
                existing.updated_at = datetime.now()
            else:
                # 创建新配置
                existing = EmailConfig(
                    smtp_server=config.smtp_server,
                    smtp_port=config.smtp_port,
                    sender_email=config.sender_email,
                    sender_password=config.sender_password,
                    receiver_email=config.receiver_email,
                    sender_name=config.sender_name,
                    receiver_name=config.receiver_name
                )
                session.add(existing)

            await session.commit()
            await session.refresh(existing)

            # 隐藏敏感信息
            config_dict = existing.__dict__
            if 'sender_password' in config_dict:
                config_dict['sender_password'] = '***'

        return ResponseModel(
            code=200,
            message="邮件配置更新成功",
            data=config_dict
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新邮件配置失败: {str(e)}")
    finally:
        pass


@router.post("/email-config/test", response_model=ResponseModel)
async def test_email_config():
    """测试邮件配置"""
    try:
        async with get_db() as session:
            # 获取邮件配置
            stmt = select(EmailConfig).order_by(EmailConfig.id.desc()).limit(1)
            result = await session.execute(stmt)
            config = result.scalar_one_or_none()

            if not config:
                raise HTTPException(status_code=400, detail="请先配置邮件信息")

            # 测试邮件发送
            from data.monitor import StockMonitor

            monitor = StockMonitor(email_config=config.__dict__)

        test_subject = "盯盘机器人 - 邮件配置测试"
        test_content = """
        这是一封测试邮件，用于验证邮件配置是否正确。

        如果收到此邮件，说明邮件配置成功！

        发送时间：{time}
        配置信息：
        - SMTP服务器：{smtp_server}:{smtp_port}
        - 发送邮箱：{sender_email}
        - 接收邮箱：{receiver_email}

        祝您投资顺利！
        """.format(
            time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            smtp_server=config.smtp_server,
            smtp_port=config.smtp_port,
            sender_email=config.sender_email,
            receiver_email=config.receiver_email
        )

        monitor.send_email(test_subject, test_content)

        return ResponseModel(
            code=200,
            message="测试邮件发送成功，请检查您的邮箱",
            data={
                "test_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "sender": config.sender_email,
                "receiver": config.receiver_email
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"测试邮件发送失败: {str(e)}")
    finally:
        pass