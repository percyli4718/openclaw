"""
LLM Provider 模块

基于 LiteLLM 的模型无关调用抽象。
支持 100+ 模型（Anthropic、OpenAI、Ollama、Gemini、通义千问等）。

用法:
    from baoke_tong.llm import get_llm_provider, LLMMessage

    llm = get_llm_provider()
    response = await llm.chat([LLMMessage(role="user", content="你好")])
    print(response.text)

扩展新模型：
    只需修改环境变量 LITELLM_MODEL，无需修改代码。
    示例: "openai/gpt-4o"、"gemini/gemini-2.0-flash"、"ollama/llama3"
"""

from .types import LLMMessage, LLMResponse, LLMError
from .base import LLMProvider
from .litellm_provider import LiteLLMProvider


def get_llm_provider() -> LLMProvider:
    """根据 settings.LITELLM_MODEL 返回 LiteLLM Provider 实例。"""
    from ..config import settings

    model = settings.LITELLM_MODEL
    # 根据模型前缀选择对应的 API key
    if model.startswith("anthropic"):
        api_key = settings.ANTHROPIC_API_KEY
    elif model.startswith("openai"):
        api_key = settings.OPENAI_API_KEY
    else:
        api_key = None

    return LiteLLMProvider(
        model=model,
        api_key=api_key,
        api_base=settings.OLLAMA_BASE_URL if "ollama" in model.lower() else None,
    )


__all__ = [
    "LLMProvider",
    "LLMMessage",
    "LLMResponse",
    "LLMError",
    "LiteLLMProvider",
    "get_llm_provider",
]
