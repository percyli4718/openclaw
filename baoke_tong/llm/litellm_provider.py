"""
LiteLLM Provider

基于 LiteLLM 的统一模型调用接口，支持 100+ 模型。
"""

import time
from typing import Optional

from .base import LLMProvider
from .types import LLMMessage, LLMResponse, LLMError


class LiteLLMProvider(LLMProvider):
    """LiteLLM Provider — 通过统一接口调用任何 LLM"""

    def __init__(
        self,
        model: str = "anthropic/claude-3-5-sonnet-20241022",
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        timeout: float = 120.0,
    ):
        """
        Args:
            model: 模型标识，格式 "provider/model_name"
                   示例: "anthropic/claude-3-5-sonnet-20241022"
                         "ollama/qwen2.5:7b"
                         "openai/gpt-4o"
            api_key: API Key（Claude/OpenAI 等云端模型需要）
            api_base: 自定义 API 基础 URL（Ollama 等本地服务需要）
            timeout: 请求超时时间（秒）
        """
        self._model = model
        self._api_key = api_key
        self._api_base = api_base
        self._timeout = timeout

    @property
    def model_name(self) -> str:
        return self._model

    async def chat(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        import litellm

        litellm_messages = [
            {"role": m.role, "content": m.content}
            for m in messages
        ]

        try:
            start = time.monotonic()
            response = await litellm.acompletion(
                model=self._model,
                messages=litellm_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=self._timeout,
                api_key=self._api_key,
                api_base=self._api_base,
            )
            elapsed = time.monotonic() - start

            # 提取文本
            text = ""
            if response.choices and len(response.choices) > 0:
                choice = response.choices[0]
                if hasattr(choice.message, "content"):
                    text = choice.message.content or ""

            # 提取 token 用量
            usage = response.usage
            tokens_used = 0
            if usage:
                tokens_used = getattr(usage, "total_tokens", 0) or 0
                if tokens_used == 0:
                    prompt = getattr(usage, "prompt_tokens", 0) or 0
                    completion = getattr(usage, "completion_tokens", 0) or 0
                    tokens_used = prompt + completion

            # 提取实际使用的模型
            actual_model = getattr(response, "model", self._model)

            return LLMResponse(
                text=text,
                tokens_used=tokens_used,
                model=actual_model,
            )

        except Exception as e:
            provider = self._model.split("/")[0] if "/" in self._model else self._model
            raise LLMError(
                f"{provider} 调用失败: {str(e)}",
                provider=provider,
            )

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> LLMResponse:
        return await self.chat(
            messages=[LLMMessage(role="user", content=prompt)],
            temperature=temperature,
            max_tokens=max_tokens,
        )
