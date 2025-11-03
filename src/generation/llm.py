"""
OpenAI LLM interface for medical response generation.
"""

import os
from typing import Dict, Optional

from openai import OpenAI


class MedicalLLM:
    """OpenAI LLM wrapper optimized for medical question answering."""

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 1500,
    ):
        """
        Initialize OpenAI client for medical LLM generation.

        Args:
            model_name: OpenAI model identifier (default: gpt-4-turbo-preview)
            temperature: Sampling temperature, lower for factual responses
            max_tokens: Maximum tokens in response
        """
        self.model_name = model_name or os.getenv("LLM_MODEL", "gpt-4-turbo-preview")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", temperature))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", max_tokens))

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")

        self.client = OpenAI(api_key=api_key)

    def generate(self, prompt: str) -> str:
        """
        Generate text response from prompt.

        Args:
            prompt: Input prompt text

        Returns:
            Generated response text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")

    def generate_with_metadata(self, prompt: str) -> Dict:
        """
        Generate response with usage statistics.

        Args:
            prompt: Input prompt text

        Returns:
            Dictionary with 'text' and 'usage' keys
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return {
                "text": response.choices[0].message.content.strip(),
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
            }
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")

