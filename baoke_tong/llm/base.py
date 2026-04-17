"""
LLM Provider 抽象基类

所有具体 Provider（Anthropic、Ollama 等）必须实现此接口。
扩展新 Provider 只需新建文件实现此接口，并在工厂函数中添加分支。
"""

from abc import ABC, abstractmethod
from .types import LLMMessage, LLMResponse


class LLMProvider(ABC):
    """LLM Provider 抽象接口"""

    @abstractmethod
    async def chat(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """
        对话式调用

        Args:
            messages: 消息列表
            temperature: 温度参数 (0-1)
            max_tokens: 最大生成 token 数

        Returns:
            LLMResponse
        """
        ...

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """
        单轮生成调用（内部转为 chat 调用）

        Args:
            prompt: 提示词
            max_tokens: 最大生成 token 数
            temperature: 温度参数

        Returns:
            LLMResponse
        """
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """当前使用的模型名称"""
        ...
