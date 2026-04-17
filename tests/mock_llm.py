"""
Mock LLM Provider for tests

Provides deterministic responses without calling real LLM services.
"""

from baoke_tong.llm import LLMProvider, LLMMessage, LLMResponse


class MockLLMProvider(LLMProvider):
    """
    Mock LLM Provider that returns pre-defined responses.

    Usage:
        mock_llm = MockLLMProvider()
        mock_llm.set_response("Hello from mock")

        gen = ContentGenerator(llm=mock_llm)
    """

    def __init__(self, default_response: str = "Mock response"):
        self._default_response = default_response
        self._responses: list[str] = []
        self._call_count = 0
        self._last_messages: list[LLMMessage] = []

    def set_response(self, text: str):
        """Set a single response for the next call"""
        self._default_response = text

    def set_responses(self, texts: list[str]):
        """Set a sequence of responses for sequential calls"""
        self._responses = list(texts)

    @property
    def model_name(self) -> str:
        return "mock-model"

    @property
    def call_count(self) -> int:
        return self._call_count

    @property
    def last_messages(self) -> list[LLMMessage]:
        return self._last_messages

    def reset(self):
        self._call_count = 0
        self._last_messages = []
        self._responses = []

    async def chat(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        self._call_count += 1
        self._last_messages = messages

        if self._responses:
            text = self._responses.pop(0)
        else:
            text = self._default_response

        return LLMResponse(
            text=text,
            tokens_used=100,
            model="mock-model",
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
