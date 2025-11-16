#!/usr/bin/env python3
"""
Tests for the LM Studio module, particularly thinking tag removal.
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.lm_studio import LMStudioModelManager, clean_thinking_tags, generate_with_model


class TestCleanThinkingTags(unittest.TestCase):
    """Test cases for the clean_thinking_tags function."""

    def test_clean_simple_think_tag(self):
        """Test removal of simple <think> tags."""
        text = "<think>This is internal thinking</think>Here is the actual message"
        expected = "Here is the actual message"
        self.assertEqual(clean_thinking_tags(text), expected)

    def test_clean_thinking_tag(self):
        """Test removal of <thinking> tags."""
        text = "<thinking>Processing the request...</thinking>Final output"
        expected = "Final output"
        self.assertEqual(clean_thinking_tags(text), expected)

    def test_clean_thought_tag(self):
        """Test removal of <thought> tags."""
        text = "<thought>Analyzing...</thought>Result here"
        expected = "Result here"
        self.assertEqual(clean_thinking_tags(text), expected)

    def test_clean_multiline_thinking_tags(self):
        """Test removal of thinking tags spanning multiple lines."""
        text = """<think>
        This is a long thought process
        spanning multiple lines
        with lots of internal reasoning
        </think>
        The actual message is here"""
        expected = "The actual message is here"
        self.assertEqual(clean_thinking_tags(text), expected)

    def test_clean_multiple_thinking_tags(self):
        """Test removal of multiple thinking tags in the same response."""
        text = """<think>First thought</think>
        Some text here
        <think>Second thought</think>
        More actual content"""
        result = clean_thinking_tags(text)
        # Should contain both lines of actual content
        self.assertIn("Some text here", result)
        self.assertIn("More actual content", result)
        # Should not contain thinking tags
        self.assertNotIn("<think>", result)
        self.assertNotIn("</think>", result)

    def test_clean_mixed_tag_types(self):
        """Test removal of different types of thinking tags in the same text."""
        text = """<think>Internal thinking</think>
        <thinking>More analysis</thinking>
        <thought>Final consideration</thought>
        This is the output"""
        expected = "This is the output"
        self.assertEqual(clean_thinking_tags(text), expected)

    def test_clean_case_insensitive(self):
        """Test that tag removal is case-insensitive."""
        text = "<THINK>Uppercase tags</THINK>Output"
        expected = "Output"
        self.assertEqual(clean_thinking_tags(text), expected)

        text2 = "<ThInK>Mixed case tags</ThInK>Output"
        expected2 = "Output"
        self.assertEqual(clean_thinking_tags(text2), expected2)

    def test_clean_text_without_tags(self):
        """Test that text without thinking tags is unchanged."""
        text = "This is a normal message without any thinking tags"
        self.assertEqual(clean_thinking_tags(text), text)

    def test_clean_empty_string(self):
        """Test handling of empty string."""
        self.assertEqual(clean_thinking_tags(""), "")

    def test_clean_none_value(self):
        """Test handling of None value."""
        self.assertIsNone(clean_thinking_tags(None))

    def test_clean_tags_at_start(self):
        """Test removal of tags at the start of text."""
        text = "<think>Initial thought</think>Message starts here"
        expected = "Message starts here"
        self.assertEqual(clean_thinking_tags(text), expected)

    def test_clean_tags_at_end(self):
        """Test removal of tags at the end of text."""
        text = "Message here<think>trailing thought</think>"
        expected = "Message here"
        self.assertEqual(clean_thinking_tags(text), expected)

    def test_clean_tags_in_middle(self):
        """Test removal of tags in the middle of text."""
        text = "Start of message<think>middle thought</think>end of message"
        expected = "Start of messageend of message"
        self.assertEqual(clean_thinking_tags(text), expected)

    def test_clean_whitespace_handling(self):
        """Test that extra whitespace is properly cleaned up."""
        text = """<think>Thought 1</think>


        <think>Thought 2</think>

        Actual message"""
        result = clean_thinking_tags(text)
        # Should remove extra blank lines
        self.assertNotIn("\n\n\n", result)
        self.assertIn("Actual message", result)

    def test_clean_nested_tags(self):
        """Test handling of nested-like patterns (though not true nesting)."""
        text = "<think>Outer <think>Inner</think> thought</think>Message"
        # Should handle greedy matching properly
        result = clean_thinking_tags(text)
        self.assertIn("Message", result)
        self.assertNotIn("<think>", result)

    def test_clean_emoji_preservation(self):
        """Test that emojis in the actual message are preserved."""
        text = "<think>Should I include an emoji?</think>🚀 Great work today!"
        expected = "🚀 Great work today!"
        self.assertEqual(clean_thinking_tags(text), expected)

    def test_clean_special_characters(self):
        """Test that special characters in the message are preserved."""
        text = "<think>Processing</think>Message with \"quotes\" and 'apostrophes'"
        expected = "Message with \"quotes\" and 'apostrophes'"
        self.assertEqual(clean_thinking_tags(text), expected)

    def test_clean_unicode_characters(self):
        """Test that unicode characters are handled properly."""
        text = "<think>Analyzing</think>Message with unicode: café, naïve, 日本語"
        expected = "Message with unicode: café, naïve, 日本語"
        self.assertEqual(clean_thinking_tags(text), expected)


class TestGenerateWithModelThinkingTags(unittest.TestCase):
    """Test that generate_with_model properly handles thinking tags."""

    @patch("lib.lm_studio.requests.post")
    def test_generate_with_model_removes_thinking_tags(self, mock_post):
        """Test that generate_with_model removes thinking tags from responses."""
        # Mock a response with thinking tags
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "<think>I should make this encouraging</think>🚀 Keep coding!"
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        result = generate_with_model("test prompt")

        # Should not contain thinking tags
        self.assertNotIn("<think>", result)
        self.assertNotIn("</think>", result)
        self.assertIn("🚀 Keep coding!", result)

    @patch("lib.lm_studio.requests.post")
    def test_generate_with_model_multiline_thinking_tags(self, mock_post):
        """Test handling of multiline thinking tags in responses."""
        # Mock a response with multiline thinking tags
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": """<think>
                        This is a complex thought
                        spanning multiple lines
                        </think>
                        ✨ You're doing amazing!"""
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        result = generate_with_model("test prompt")

        # Should not contain thinking tags
        self.assertNotIn("<think>", result)
        self.assertNotIn("</think>", result)
        self.assertIn("✨ You're doing amazing!", result)

    @patch("lib.lm_studio.requests.post")
    def test_generate_with_model_mixed_thinking_tags(self, mock_post):
        """Test handling of mixed thinking tag types."""
        # Mock a response with different tag types
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": """<thinking>Analyzing request</thinking>
                        <think>Deciding on tone</think>
                        💪 Great progress today!"""
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        result = generate_with_model("test prompt")

        # Should not contain any thinking tags
        self.assertNotIn("<think>", result)
        self.assertNotIn("</think>", result)
        self.assertNotIn("<thinking>", result)
        self.assertNotIn("</thinking>", result)
        self.assertIn("💪 Great progress today!", result)

    @patch("lib.lm_studio.requests.post")
    def test_generate_with_model_no_thinking_tags(self, mock_post):
        """Test that normal responses without thinking tags work correctly."""
        # Mock a normal response without thinking tags
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "🎯 Focus and conquer!"}}]
        }
        mock_post.return_value = mock_response

        result = generate_with_model("test prompt")

        self.assertEqual(result, "🎯 Focus and conquer!")


class TestLMStudioModelManager(unittest.TestCase):
    """Test cases for LMStudioModelManager class."""

    @patch("lib.lm_studio.requests.get")
    def test_is_available_success(self, mock_get):
        """Test that is_available returns True when server is accessible."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        manager = LMStudioModelManager()
        self.assertTrue(manager.is_available())

    @patch("lib.lm_studio.requests.get")
    def test_is_available_failure(self, mock_get):
        """Test that is_available returns False when server is not accessible."""
        import requests

        mock_get.side_effect = requests.ConnectionError("Connection failed")

        manager = LMStudioModelManager()
        self.assertFalse(manager.is_available())


if __name__ == "__main__":
    unittest.main()
