"""
Hermes Agent 技能模块

包含保险行业核心技能：
- 内容生成：朋友圈文案、短视频脚本、海报文案
- 客户分析：客户画像、分层分析、需求预测
- 跟进管理：跟进计划、定时消息、跟进记录
"""

from .content_gen import ContentGenerator
from .customer import CustomerAnalyst
from .followup import FollowupManager

__all__ = [
    "ContentGenerator",
    "CustomerAnalyst",
    "FollowupManager",
]
