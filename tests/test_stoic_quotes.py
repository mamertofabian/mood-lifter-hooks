#!/usr/bin/env python3
"""
Tests for the stoic quotes module.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.stoic_quotes import (
    enhance_stoic_quote_with_lm_studio,
    generate_pure_stoic_wisdom,
    generate_stoic_message,
    get_fallback_stoic_message,
    get_general_stoic_wisdom,
    get_stoic_quote,
)


class TestStoicQuotes(unittest.TestCase):
    """Test cases for stoic quotes functions."""

    def test_get_stoic_quote_no_theme(self):
        """Test getting a random stoic quote without theme filter."""
        quote = get_stoic_quote()
        self.assertIsInstance(quote, dict)
        self.assertIn("text", quote)
        self.assertIn("author", quote)
        self.assertIsInstance(quote["text"], str)
        self.assertIsInstance(quote["author"], str)
        self.assertGreater(len(quote["text"]), 0)
        self.assertGreater(len(quote["author"]), 0)

    def test_get_stoic_quote_with_theme(self):
        """Test getting a stoic quote with theme filter."""
        themes = ["anger", "control", "peace", "obstacles"]

        for theme in themes:
            quote = get_stoic_quote(theme=theme)
            self.assertIsInstance(quote, dict)
            self.assertIn("text", quote)
            self.assertIn("author", quote)
            self.assertIsInstance(quote["text"], str)
            self.assertIsInstance(quote["author"], str)

    def test_get_stoic_quote_invalid_theme(self):
        """Test getting a stoic quote with invalid theme (should fallback)."""
        quote = get_stoic_quote(theme="invalid_theme")
        self.assertIsInstance(quote, dict)
        self.assertIn("text", quote)
        self.assertIn("author", quote)

    def test_get_general_stoic_wisdom(self):
        """Test getting general stoic wisdom."""
        wisdom = get_general_stoic_wisdom()
        self.assertIsInstance(wisdom, str)
        self.assertGreater(len(wisdom), 0)
        # Should be from the GENERAL_STOIC_WISDOM list
        from lib.stoic_quotes import GENERAL_STOIC_WISDOM

        self.assertIn(wisdom, GENERAL_STOIC_WISDOM)

    def test_get_fallback_stoic_message(self):
        """Test fallback stoic message."""
        message = get_fallback_stoic_message()
        self.assertIsInstance(message, str)
        self.assertGreater(len(message), 0)
        # Should contain zen emoji
        self.assertTrue(any(emoji in message for emoji in ["🧘", "💭", "🌊", "⚖️", "🎯"]))

    def test_generate_stoic_message_without_lm_studio(self):
        """Test generating stoic message without LM Studio."""
        message = generate_stoic_message(use_lm_studio=False)
        self.assertIsInstance(message, str)
        self.assertGreater(len(message), 0)
        # Should contain zen emoji
        self.assertTrue(any(emoji in message for emoji in ["🧘", "💭", "🌊", "⚖️", "🎯"]))

    def test_generate_stoic_message_with_general_wisdom(self):
        """Test generating stoic message with general wisdom."""
        message = generate_stoic_message(use_general_wisdom=True, use_lm_studio=False)
        self.assertIsInstance(message, str)
        self.assertGreater(len(message), 0)
        self.assertTrue(message.startswith("🧘"))

    @patch("subprocess.run")
    def test_generate_stoic_message_with_lm_studio(self, mock_run):
        """Test generating stoic message with LM Studio (mocked)."""
        # Mock successful LM Studio response
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "🧘 Stay calm and debug on."
        mock_run.return_value = mock_result

        message = generate_stoic_message(use_lm_studio=True)
        self.assertIsInstance(message, str)
        self.assertGreater(len(message), 0)

    @patch("subprocess.run")
    def test_enhance_stoic_quote_with_lm_studio(self, mock_run):
        """Test enhancing stoic quote with LM Studio (mocked)."""
        # Mock successful LM Studio response
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "🧘 Apply this wisdom to your coding challenges."
        mock_run.return_value = mock_result

        quote = {"text": "Control what you can", "author": "Marcus Aurelius"}
        message = enhance_stoic_quote_with_lm_studio(quote)
        self.assertIsInstance(message, str)
        self.assertGreater(len(message), 0)

    def test_enhance_stoic_quote_with_lm_studio_fallback(self):
        """Test enhancing stoic quote with LM Studio fallback."""
        quote = {"text": "Control what you can", "author": "Marcus Aurelius"}

        with patch("subprocess.run", side_effect=FileNotFoundError):
            message = enhance_stoic_quote_with_lm_studio(quote)
            self.assertIsInstance(message, str)
            self.assertGreater(len(message), 0)
            self.assertIn("Control what you can", message)

    @patch("subprocess.run")
    def test_generate_pure_stoic_wisdom(self, mock_run):
        """Test generating pure stoic wisdom with LM Studio (mocked)."""
        # Mock successful LM Studio response
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "🧘 The bug teaches patience, the fix rewards persistence."
        mock_run.return_value = mock_result

        message = generate_pure_stoic_wisdom()
        self.assertIsInstance(message, str)
        self.assertGreater(len(message), 0)
        self.assertTrue(any(emoji in message for emoji in ["🧘", "💭", "🌊", "⚖️", "🎯"]))

    def test_generate_pure_stoic_wisdom_fallback(self):
        """Test generating pure stoic wisdom fallback."""
        with patch("subprocess.run", side_effect=FileNotFoundError):
            message = generate_pure_stoic_wisdom()
            self.assertIsNone(message)

    def test_generate_pure_stoic_wisdom_with_theme(self):
        """Test generating pure stoic wisdom with specific theme."""
        themes = ["anger", "control", "peace", "obstacles"]

        for theme in themes:
            with patch("subprocess.run") as mock_run:
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_result.stdout = f"🧘 {theme.title()} wisdom for developers."
                mock_run.return_value = mock_result

                message = generate_pure_stoic_wisdom(theme=theme)
                self.assertIsInstance(message, str)
                self.assertGreater(len(message), 0)


class TestStoicQuoteContent(unittest.TestCase):
    """Test cases for stoic quote content quality."""

    def test_stoic_quotes_have_required_fields(self):
        """Test that all stoic quotes have required fields."""
        from lib.stoic_quotes import STOIC_QUOTES

        for quote in STOIC_QUOTES:
            self.assertIn("text", quote)
            self.assertIn("author", quote)
            self.assertIn("theme", quote)
            self.assertIsInstance(quote["text"], str)
            self.assertIsInstance(quote["author"], str)
            self.assertIsInstance(quote["theme"], str)
            self.assertGreater(len(quote["text"]), 10)  # Meaningful quote length
            self.assertGreater(len(quote["author"]), 0)

    def test_general_wisdom_content(self):
        """Test that general wisdom has meaningful content."""
        from lib.stoic_quotes import GENERAL_STOIC_WISDOM

        # Verify we have a reasonable number of wisdom statements
        self.assertGreater(len(GENERAL_STOIC_WISDOM), 5)

        for wisdom in GENERAL_STOIC_WISDOM:
            self.assertIsInstance(wisdom, str)
            self.assertGreater(len(wisdom), 20)  # Meaningful wisdom length
            # Wisdom should be a complete sentence (ends with punctuation)
            self.assertTrue(
                wisdom.endswith(".") or wisdom.endswith("!") or wisdom.endswith("?"),
                f"Wisdom should be a complete sentence: {wisdom}",
            )

    def test_theme_distribution(self):
        """Test that themes are well distributed."""
        from lib.stoic_quotes import STOIC_QUOTES

        themes = {}
        for quote in STOIC_QUOTES:
            theme = quote["theme"]
            themes[theme] = themes.get(theme, 0) + 1

        # Should have multiple themes
        self.assertGreater(len(themes), 3)

        # Should have some themes with multiple quotes (core themes)
        core_themes = ["anger", "control", "peace", "obstacles"]
        for theme in core_themes:
            self.assertGreaterEqual(
                themes.get(theme, 0), 2, f"Core theme '{theme}' should have at least 2 quotes"
            )

        # Should have a reasonable distribution (at least some themes with multiple quotes)
        themes_with_multiple = sum(1 for count in themes.values() if count >= 2)
        self.assertGreaterEqual(
            themes_with_multiple,
            3,
            f"Should have at least 3 themes with 2+ quotes. Theme counts: {themes}",
        )


if __name__ == "__main__":
    unittest.main()
