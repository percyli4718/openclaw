"""
LLM 通用类型定义

模型无关的统一消息格式和响应格式。
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMMessage:
    """统一消息格式"""
    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass
class LLMResponse:
    """统一响应格式"""
    text: str
    tokens_used: int = 0
    model: str = "unknown"


class LLMError(Exception):
    """LLM 调用异常"""
    def __init__(self, message: str, provider: str = "", status_code: Optional[int] = None):
        super().__init__(message)
        self.provider = provider
        self.status_code = status_code
