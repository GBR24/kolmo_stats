"""
Thin multi-provider LLM client.

Supports Anthropic (claude-*) and OpenAI (gpt-*, o1-*, o3-*) out of the box.
Users supply their own API key — no key is baked in.

Install the provider SDK you need:
    pip install anthropic   # for Claude
    pip install openai      # for GPT / o-series
"""
from __future__ import annotations

from .context import ContextBuilder, SYSTEM_PROMPT
from .retriever import RetrievalResult


class LLMClient:
    def __init__(self):
        self._ctx = ContextBuilder()

    def ask(
        self,
        query: str,
        result: RetrievalResult,
        api_key: str,
        model: str,
    ) -> str:
        messages = self._ctx.to_messages(query, result)
        model_l = model.lower()
        if "claude" in model_l:
            return self._anthropic(messages, api_key, model)
        if any(k in model_l for k in ("gpt", "o1", "o3", "o4")):
            return self._openai(messages, api_key, model)
        raise ValueError(
            f"Cannot infer provider from model name {model!r}. "
            "Use a claude-* or gpt-*/o1-*/o3-* model name."
        )

    # ------------------------------------------------------------------
    # Providers
    # ------------------------------------------------------------------

    def _anthropic(self, messages: list[dict], api_key: str, model: str) -> str:
        try:
            import anthropic
        except ImportError as exc:
            raise ImportError("Run: pip install anthropic") from exc

        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        return response.content[0].text

    def _openai(self, messages: list[dict], api_key: str, model: str) -> str:
        try:
            import openai
        except ImportError as exc:
            raise ImportError("Run: pip install openai") from exc

        client = openai.OpenAI(api_key=api_key)
        full = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        response = client.chat.completions.create(model=model, messages=full)
        return response.choices[0].message.content
