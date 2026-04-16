"""
测试配置
"""

import os
import sys

# 设置测试环境变量
os.environ.setdefault('ENCRYPTION_KEY', 'test_encryption_key_32bytes!!!!')
os.environ.setdefault('APP_ENV', 'test')
os.environ.setdefault('DATABASE_URL', 'postgresql://test:test@localhost:5432/baoke_tong_test')

# pytest 配置
pytest_plugins = [
    "tests.fixtures",
]
