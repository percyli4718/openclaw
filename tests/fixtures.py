"""
测试夹具（Fixtures）
"""

import pytest
import os
from pathlib import Path


@pytest.fixture
def test_audit_log_path(tmp_path):
    """创建临时审计日志文件路径"""
    return str(tmp_path / "test_audit_logs.jsonl")


@pytest.fixture
def test_env():
    """设置测试环境变量"""
    os.environ['ENCRYPTION_KEY'] = 'test_encryption_key_32bytes!!!!'
    os.environ['APP_ENV'] = 'test'
    yield
    # 清理环境变量
    os.environ.pop('ENCRYPTION_KEY', None)
    os.environ.pop('APP_ENV', None)


@pytest.fixture
def sample_customer_data():
    """示例客户数据"""
    return {
        "name": "测试客户",
        "age": 35,
        "occupation": "软件工程师",
        "income": "50-100 万",
        "family_status": "已婚有子女"
    }


@pytest.fixture
def sample_product_data():
    """示例产品数据"""
    return {
        "product_name": "健康保",
        "product_type": "重疾险",
        "target_audience": "25-40 岁白领"
    }
