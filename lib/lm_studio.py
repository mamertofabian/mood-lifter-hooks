#!/usr/bin/env python3
"""
LM Studio model management for Mood Lifter Hooks.
Uses LM Studio's OpenAI-compatible HTTP API for message generation.
"""

import random
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import requests

try:
    from lib.constants import Defaults, Timeouts
except ImportError:
    # Fallback constants if imports fail
    class Timeouts:
        LLM_NORMAL = 5
        LLM_QUICK = 3

    class Defaults:
        pass


class LMStudioModelManager:
    """Manage LM Studio models via OpenAI-compatible HTTP API."""

    # Default LM Studio API endpoint
    DEFAULT_BASE_URL = "http://localhost:1234/v1"

    # Recommended lightweight models for fast message generation
    RECOMMENDED_MODELS = [
        "llama-3.2-1b-instruct",
        "llama-3.2-3b-instruct",
        "phi-3.5-mini-instruct",
        "qwen2.5-7b-instruct",
        "gemma-2-2b-instruct",
    ]

    # Fallback model name
    DEFAULT_MODEL = "llama-3.2-1b-instruct"

    def __init__(self, base_url: str = None, cache_ttl_minutes: int = 30):
        """
        Initialize the model manager.

        Args:
            base_url: LM Studio API base URL (defaults to localhost:1234/v1)
            cache_ttl_minutes: How long to cache the model list
        """
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.cache_ttl_minutes = cache_ttl_minutes
        self._cached_models: Optional[List[str]] = None
        self._cache_time: Optional[datetime] = None
        self._last_used_model: Optional[str] = None
        self._model_usage_count: Dict[str, int] = {}

    def _is_cache_valid(self) -> bool:
        """Check if the cached model list is still valid."""
        if self._cached_models is None or self._cache_time is None:
            return False

        cache_age = datetime.now() - self._cache_time
        return cache_age < timedelta(minutes=self.cache_ttl_minutes)

    def is_available(self) -> bool:
        """
        Check if LM Studio server is running and accessible.

        Returns:
            True if LM Studio API is accessible
        """
        try:
            response = requests.get(f"{self.base_url}/models", timeout=2)
            return response.status_code == 200
        except (requests.RequestException, requests.ConnectionError, requests.Timeout):
            return False

    def get_available_models(self, refresh: bool = False) -> List[str]:
        """
        Get list of available LM Studio models via API.

        Args:
            refresh: Force refresh of the model list

        Returns:
            List of available model names
        """
        if not refresh and self._is_cache_valid():
            return self._cached_models

        try:
            response = requests.get(f"{self.base_url}/models", timeout=Timeouts.LLM_NORMAL)

            if response.status_code == 200:
                data = response.json()
                models = []

                # Extract model IDs from the OpenAI-compatible response
                if "data" in data:
                    for model in data["data"]:
                        if "id" in model:
                            models.append(model["id"])

                # Cache the results
                self._cached_models = models
                self._cache_time = datetime.now()

                return models

        except (requests.RequestException, requests.ConnectionError, requests.Timeout):
            pass

        # Return empty list on error
        return []

    def get_loaded_model(self) -> Optional[str]:
        """
        Get the currently loaded model.
        In LM Studio, the first model in the list is typically the loaded one.

        Returns:
            Currently loaded model name or None
        """
        models = self.get_available_models()
        return models[0] if models else None

    def get_recommended_available_models(self) -> List[str]:
        """
        Get list of recommended models that are actually available.

        Returns:
            List of available recommended models
        """
        available = self.get_available_models()
        if not available:
            return []

        # Find intersection of recommended and available
        recommended_available = []
        for model in self.RECOMMENDED_MODELS:
            # Check if model or its base name is available
            for avail_model in available:
                if model in avail_model or avail_model in model:
                    if model not in recommended_available:
                        recommended_available.append(avail_model)
                    break

        return recommended_available

    def select_model(self, prefer_variety: bool = True, use_loaded: bool = True) -> str:
        """
        Select a model for message generation.

        Args:
            prefer_variety: Whether to prefer using different models
            use_loaded: Whether to use the currently loaded model if available

        Returns:
            Selected model name
        """
        # First, get the currently loaded model if we should use it
        if use_loaded:
            loaded_model = self.get_loaded_model()
            # If a model is already loaded, use it to avoid loading overhead
            if loaded_model:
                self._last_used_model = loaded_model
                self._model_usage_count[loaded_model] = (
                    self._model_usage_count.get(loaded_model, 0) + 1
                )
                return loaded_model

        # If no model is loaded, try to find a recommended one
        recommended = self.get_recommended_available_models()

        if not recommended:
            # No recommended models available, try any available model
            available = self.get_available_models()
            if available:
                selected = random.choice(available)
                self._last_used_model = selected
                self._model_usage_count[selected] = self._model_usage_count.get(selected, 0) + 1
                return selected
            else:
                # No models available at all, return default
                return self.DEFAULT_MODEL

        # Select from recommended models
        if prefer_variety and len(recommended) > 1:
            # Try to avoid using the same model twice in a row
            if self._last_used_model in recommended and len(recommended) > 1:
                choices = [m for m in recommended if m != self._last_used_model]
            else:
                choices = recommended

            # Weight selection by least used models
            weights = []
            for model in choices:
                usage = self._model_usage_count.get(model, 0)
                # Inverse weight: less used models get higher weight
                weight = max(1, 10 - usage)
                weights.append(weight)

            # Select model with weighted random
            selected = random.choices(choices, weights=weights)[0]
        else:
            # Simple random selection
            selected = random.choice(recommended)

        # Update tracking
        self._last_used_model = selected
        self._model_usage_count[selected] = self._model_usage_count.get(selected, 0) + 1

        return selected


def clean_thinking_tags(text: str) -> str:
    """
    Remove thinking tags from LLM responses.

    Handles various thinking tag formats:
    - <think>...</think>
    - <thinking>...</thinking>
    - <thought>...</thought>

    Args:
        text: The text to clean

    Returns:
        Cleaned text with thinking tags removed
    """
    if not text:
        return text

    # Remove thinking tags and their content (case-insensitive, handles newlines)
    patterns = [
        r"<think>.*?</think>",
        r"<thinking>.*?</thinking>",
        r"<thought>.*?</thought>",
    ]

    cleaned = text
    for pattern in patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.DOTALL)

    # Clean up extra whitespace and newlines
    cleaned = re.sub(r"\n\s*\n+", "\n", cleaned)  # Remove multiple blank lines
    cleaned = cleaned.strip()

    return cleaned


def generate_with_model(
    prompt: str,
    model: Optional[str] = None,
    manager: Optional[LMStudioModelManager] = None,
    timeout: int = 3,
    temperature: float = 0.7,
    max_tokens: int = 50,
) -> Optional[str]:
    """
    Generate text using LM Studio's OpenAI-compatible API.

    Args:
        prompt: The prompt to send to the model
        model: Specific model to use (None for auto-selection)
        manager: Model manager instance (creates new if None)
        timeout: Generation timeout in seconds
        temperature: Sampling temperature (0.0 to 1.0)
        max_tokens: Maximum tokens to generate

    Returns:
        Generated text or None on error
    """
    if manager is None:
        manager = LMStudioModelManager()

    if model is None:
        model = manager.select_model()

    try:
        # Use OpenAI-compatible chat completions endpoint
        response = requests.post(
            f"{manager.base_url}/chat/completions",
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False,
            },
            timeout=timeout,
        )

        if response.status_code == 200:
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                message = data["choices"][0]["message"]["content"].strip()
                # Remove thinking tags from the response
                message = clean_thinking_tags(message)
                # Take first line only for hook messages
                message = message.split("\n")[0].strip()
                return message

    except (requests.RequestException, requests.ConnectionError, requests.Timeout):
        pass

    return None


def test_model_manager():
    """Test the LM Studio model manager."""
    print("Testing LM Studio Model Manager (HTTP API)")
    print("=" * 50)

    manager = LMStudioModelManager()

    # Test LM Studio availability
    print("\n1. LM Studio Server Status:")
    if manager.is_available():
        print("   ✅ LM Studio server is accessible")
    else:
        print("   ❌ LM Studio server is not accessible")
        print("   Make sure LM Studio is running on http://localhost:1234")
        return

    # Test getting available models
    print("\n2. Available Models:")
    models = manager.get_available_models()
    if models:
        for i, model in enumerate(models[:5], 1):
            print(f"   {i}. {model}")
        if len(models) > 5:
            print(f"   ... and {len(models) - 5} more")
    else:
        print("   No models found (load a model in LM Studio)")
        return

    # Test getting currently loaded model
    print("\n3. Currently Loaded Model:")
    loaded = manager.get_loaded_model()
    if loaded:
        print(f"   • {loaded}")
    else:
        print("   No model currently loaded")

    # Test getting recommended models
    print("\n4. Recommended Available Models:")
    recommended = manager.get_recommended_available_models()
    if recommended:
        for model in recommended:
            print(f"   • {model}")
    else:
        print("   No recommended models available")
        print("   Consider loading one of these models in LM Studio:")
        for model in LMStudioModelManager.RECOMMENDED_MODELS[:3]:
            print(f"     - {model}")

    # Test model selection
    print("\n5. Model Selection (3 samples):")
    for i in range(3):
        selected = manager.select_model()
        print(f"   {i+1}. Selected: {selected}")

    # Test generation
    print("\n6. Message Generation Test:")
    prompt = "Generate a brief encouraging message for a developer. Maximum 10 words. Include one emoji. Add humor. Only output the message, no metadata."

    if loaded:
        print(f"\n   Using loaded model ({loaded}):")
        message = generate_with_model(prompt, manager=manager, timeout=5)
        if message:
            print(f"   → {message}")
        else:
            print("   → (Generation failed)")
    else:
        print("\n   Skipping generation test (no model loaded)")

    # Show usage statistics
    print("\n7. Model Usage Statistics:")
    if manager._model_usage_count:
        for model, count in manager._model_usage_count.items():
            print(f"   • {model}: used {count} time(s)")
    else:
        print("   No usage statistics yet")


if __name__ == "__main__":
    test_model_manager()
