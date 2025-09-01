#!/usr/bin/env python3
"""
Ollama model management for Mood Lifter Hooks.
Provides model rotation and selection for variety.
"""

import subprocess
import random
import json
import time
from typing import Optional, List, Dict, Tuple
from datetime import datetime, timedelta
from lib.constants import Timeouts, Defaults


class OllamaModelManager:
    """Manage ollama models for variety in message generation."""
    
    # Recommended models for fast, efficient message generation
    RECOMMENDED_MODELS = [
        "phi3.5:3.8b",      # Microsoft's efficient model
        "mistral:7b-instruct",  # Good for instructions
        "llama3.2:1b",      # Very fast, lightweight
        "gemma2:2b",        # Google's small model
        "qwen2.5:0.5b",     # Alibaba's tiny model
    ]
    
    # Fallback if no recommended models are available
    DEFAULT_MODEL = "phi3.5:3.8b"
    
    def __init__(self, cache_ttl_minutes: int = 30):
        """
        Initialize the model manager.
        
        Args:
            cache_ttl_minutes: How long to cache the model list
        """
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
    
    def get_available_models(self, refresh: bool = False) -> List[str]:
        """
        Get list of available ollama models.
        
        Args:
            refresh: Force refresh of the model list
            
        Returns:
            List of available model names
        """
        if not refresh and self._is_cache_valid():
            return self._cached_models
        
        try:
            # Run ollama list command
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=Timeouts.OLLAMA_NORMAL
            )
            
            if result.returncode == 0:
                # Parse the output
                lines = result.stdout.strip().split('\n')
                models = []
                
                # Skip header line if present
                for line in lines[1:] if lines else []:
                    # Extract model name (first column)
                    parts = line.split()
                    if parts:
                        model_name = parts[0]
                        # Remove size suffixes if present (e.g., :latest)
                        if ':' in model_name and not any(c.isdigit() for c in model_name.split(':')[1]):
                            model_name = model_name.split(':')[0]
                        models.append(model_name)
                
                # Cache the results
                self._cached_models = models
                self._cache_time = datetime.now()
                
                return models
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            pass
        
        # Return empty list on error
        return []
    
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
            model_base = model.split(':')[0] if ':' in model else model
            if model in available or model_base in available:
                recommended_available.append(model)
        
        return recommended_available
    
    def select_model(self, prefer_variety: bool = True) -> str:
        """
        Select a model for message generation.
        
        Args:
            prefer_variety: Whether to prefer using different models
            
        Returns:
            Selected model name
        """
        recommended = self.get_recommended_available_models()
        
        if not recommended:
            # No recommended models available, try any available model
            available = self.get_available_models()
            if available:
                return random.choice(available)
            else:
                # No models available at all, return default
                return self.DEFAULT_MODEL
        
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
    
    def pull_model(self, model_name: str) -> bool:
        """
        Pull (download) a model if not available.
        
        Args:
            model_name: Name of the model to pull
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"Pulling model {model_name}... This may take a while.")
            result = subprocess.run(
                ["ollama", "pull", model_name],
                capture_output=True,
                text=True,
                timeout=Timeouts.OLLAMA_DOWNLOAD
            )
            
            if result.returncode == 0:
                print(f"Successfully pulled {model_name}")
                # Refresh cache
                self.get_available_models(refresh=True)
                return True
            else:
                print(f"Failed to pull {model_name}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"Timeout while pulling {model_name}")
            return False
        except Exception as e:
            print(f"Error pulling {model_name}: {e}")
            return False
    
    def ensure_model_available(self, model_name: str) -> bool:
        """
        Ensure a model is available, pulling it if necessary.
        
        Args:
            model_name: Name of the model
            
        Returns:
            True if model is available, False otherwise
        """
        available = self.get_available_models()
        model_base = model_name.split(':')[0] if ':' in model_name else model_name
        
        if model_name in available or model_base in available:
            return True
        
        # Try to pull the model
        return self.pull_model(model_name)


def generate_with_model(
    prompt: str,
    model: Optional[str] = None,
    manager: Optional[OllamaModelManager] = None,
    timeout: int = 3
) -> Optional[str]:
    """
    Generate text using ollama with model selection.
    
    Args:
        prompt: The prompt to send to the model
        model: Specific model to use (None for auto-selection)
        manager: Model manager instance (creates new if None)
        timeout: Generation timeout in seconds
        
    Returns:
        Generated text or None on error
    """
    if manager is None:
        manager = OllamaModelManager()
    
    if model is None:
        model = manager.select_model()
    
    try:
        result = subprocess.run(
            ["ollama", "run", model, "--verbose=false"],
            input=prompt,
            text=True,
            capture_output=True,
            timeout=timeout
        )
        
        if result.returncode == 0 and result.stdout:
            # Clean up the output
            message = result.stdout.strip().split('\n')[0].strip()
            return message
            
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        pass
    
    return None


def test_model_manager():
    """Test the ollama model manager."""
    print("Testing Ollama Model Manager")
    print("=" * 50)
    
    manager = OllamaModelManager()
    
    # Test getting available models
    print("\n1. Available Models:")
    models = manager.get_available_models()
    if models:
        for model in models[:5]:  # Show first 5
            print(f"   • {model}")
        if len(models) > 5:
            print(f"   ... and {len(models) - 5} more")
    else:
        print("   No models found (ollama might not be installed)")
    
    # Test getting recommended models
    print("\n2. Recommended Available Models:")
    recommended = manager.get_recommended_available_models()
    if recommended:
        for model in recommended:
            print(f"   • {model}")
    else:
        print("   No recommended models available")
    
    # Test model selection
    print("\n3. Model Selection (5 samples):")
    for i in range(5):
        selected = manager.select_model()
        print(f"   {i+1}. Selected: {selected}")
    
    # Test generation with model rotation
    print("\n4. Message Generation with Different Models:")
    prompt = "Generate a brief encouraging message for a developer. Maximum 10 words. Include one emoji. Only output the message, no metadata."
    
    for i in range(3):
        model = manager.select_model()
        print(f"\n   Using {model}:")
        message = generate_with_model(prompt, model=model, manager=manager)
        if message:
            print(f"   → {message}")
        else:
            print(f"   → (Generation failed)")
    
    # Show usage statistics
    print("\n5. Model Usage Statistics:")
    for model, count in manager._model_usage_count.items():
        print(f"   • {model}: used {count} time(s)")


if __name__ == "__main__":
    test_model_manager()