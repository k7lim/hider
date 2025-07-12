#!/usr/bin/env python3
"""
Tests for steg-tool.py - Educational test suite for Unicode steganography

These tests demonstrate key concepts:
- Steganography should be reversible (encode → decode → original)
- Different methods produce different encodings but same results
- Error handling for edge cases
- Auto-detection of encoding methods
"""

import unittest
import sys
import os

# Import the functions from steg-tool.py by executing it in controlled way
import subprocess
import tempfile

def run_encode(visible_text, secret_message, method="zero-width", injection_point="first-space"):
    """Test helper to run encode via subprocess"""
    cmd = ["python3", "-m", "steg", "encode", visible_text, secret_message, 
           "--method", method, "--inject", injection_point]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Encode failed: {result.stderr}")
    # Extract just the encoded text from output
    lines = result.stdout.strip().split('\n')
    # Find the line with the encoded text (between dashes)
    for i, line in enumerate(lines):
        if line.startswith('----'):
            return lines[i+1] if i+1 < len(lines) else ""
    return ""

def run_decode(text_to_decode, method="auto"):
    """Test helper to run decode via subprocess"""
    cmd = ["python3", "-m", "steg", "decode", text_to_decode, "--method", method]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return ""
    # Extract secret from output
    for line in result.stdout.strip().split('\n'):
        if line.startswith("Decoded Secret: "):
            return line[16:]  # Remove "Decoded Secret: " prefix
    return ""

def run_encode_expect_error(visible_text, secret_message, injection_point="first-space"):
    """Test helper that expects encode to fail"""
    cmd = ["python3", "-m", "steg", "encode", visible_text, secret_message, 
           "--inject", injection_point]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode != 0  # Return True if it failed as expected


class TestSteganography(unittest.TestCase):
    
    def test_zero_width_round_trip(self):
        """Test that zero-width encoding is reversible"""
        visible = "Hello world"
        secret = "test"
        
        encoded = run_encode(visible, secret, method="zero-width")
        decoded = run_decode(encoded, method="zero-width")
        
        self.assertEqual(decoded, secret, "Zero-width round-trip should preserve secret")
        # Encoded text should look the same visually but be different
        self.assertNotEqual(encoded, visible, "Encoded text should be different from original")
    
    def test_tag_round_trip(self):
        """Test that TAG character encoding is reversible"""
        visible = "Hello world"
        secret = "test"
        
        encoded = run_encode(visible, secret, method="tag")
        decoded = run_decode(encoded, method="tag")
        
        self.assertEqual(decoded, secret, "TAG round-trip should preserve secret")
        self.assertNotEqual(encoded, visible, "Encoded text should be different from original")
    
    def test_auto_detection(self):
        """Test that auto-detection works for both encoding methods"""
        visible = "Hello world"
        secret = "secret"
        
        # Test zero-width auto-detection
        zero_width_encoded = run_encode(visible, secret, method="zero-width")
        auto_decoded_zw = run_decode(zero_width_encoded, method="auto")
        self.assertEqual(auto_decoded_zw, secret, "Auto-detection should work for zero-width")
        
        # Test TAG auto-detection
        tag_encoded = run_encode(visible, secret, method="tag")
        auto_decoded_tag = run_decode(tag_encoded, method="auto")
        self.assertEqual(auto_decoded_tag, secret, "Auto-detection should work for TAG")
    
    def test_different_injection_points_same_result(self):
        """Test that different injection points produce different text but same decoded result"""
        visible = "The quick brown fox"
        secret = "hidden"
        
        # Different injection points
        first_space = run_encode(visible, secret, injection_point="first-space")
        end = run_encode(visible, secret, injection_point="end")
        word_2 = run_encode(visible, secret, injection_point="word-2")
        
        # All should be different encodings
        self.assertNotEqual(first_space, end)
        self.assertNotEqual(first_space, word_2)
        self.assertNotEqual(end, word_2)
        
        # But all should decode to the same secret
        self.assertEqual(run_decode(first_space), secret)
        self.assertEqual(run_decode(end), secret)
        self.assertEqual(run_decode(word_2), secret)
    
    def test_empty_secret_message(self):
        """Test encoding/decoding empty secret message"""
        visible = "Hello world"
        secret = ""
        
        encoded = run_encode(visible, secret)
        decoded = run_decode(encoded)
        
        self.assertEqual(decoded, secret, "Empty secret should round-trip correctly")
    
    def test_no_whitespace_error(self):
        """Test that text with no whitespace fails gracefully with first-space injection"""
        visible = "Helloworld"  # No spaces
        secret = "test"
        
        failed = run_encode_expect_error(visible, secret, injection_point="first-space")
        self.assertTrue(failed, "Should fail when no whitespace and using first-space injection")
    
    def test_no_hidden_content(self):
        """Test decoding text with no hidden content returns empty string"""
        normal_text = "This is just normal text with no hidden content"
        
        decoded = run_decode(normal_text)
        self.assertEqual(decoded, "", "Text with no hidden content should return empty string")
    
    def test_invalid_injection_points(self):
        """Test that invalid injection points fail gracefully"""
        visible = "Hello world"
        secret = "test"
        
        # Word that doesn't exist
        failed1 = run_encode_expect_error(visible, secret, injection_point="word-99")
        self.assertTrue(failed1, "Should fail for non-existent word")
        
        # Character position out of range
        failed2 = run_encode_expect_error(visible, secret, injection_point="char-999")
        self.assertTrue(failed2, "Should fail for out-of-range character position")
    
    def test_empty_visible_text_error(self):
        """Test that empty visible text fails appropriately"""
        visible = ""
        secret = "test"
        
        failed = run_encode_expect_error(visible, secret)
        self.assertTrue(failed, "Should fail for empty visible text")
    
    def test_zero_width_vs_tag_visibility(self):
        """Educational test showing the difference between encoding methods"""
        visible = "Hello world"
        secret = "test"
        
        zero_width_encoded = run_encode(visible, secret, method="zero-width")
        tag_encoded = run_encode(visible, secret, method="tag")
        
        # Both should decode to same secret
        self.assertEqual(run_decode(zero_width_encoded), secret)
        self.assertEqual(run_decode(tag_encoded), secret)
        
        # But encodings should be different
        self.assertNotEqual(zero_width_encoded, tag_encoded)
        
        # Print for educational purposes (normally avoid prints in tests)
        print(f"\nOriginal: {repr(visible)}")
        print(f"Zero-width: {repr(zero_width_encoded)}")
        print(f"TAG: {repr(tag_encoded)}")


class TestBasicFunctionality(unittest.TestCase):
    """Test basic encoding/decoding without complex injection logic"""
    
    def test_basic_encode_decode_works(self):
        """Smoke test that basic encoding and decoding work"""
        visible = "Hello world"
        secret = "test"
        
        # Just test that we can encode and decode without errors
        encoded = run_encode(visible, secret)
        self.assertTrue(len(encoded) > len(visible), "Encoded text should be longer")
        
        decoded = run_decode(encoded)
        self.assertEqual(decoded, secret, "Should decode to original secret")
    
    def test_different_methods_both_work(self):
        """Test that both zero-width and TAG methods function"""
        visible = "Hello world"
        secret = "test"
        
        # Both methods should work
        zw_encoded = run_encode(visible, secret, method="zero-width")
        tag_encoded = run_encode(visible, secret, method="tag")
        
        self.assertEqual(run_decode(zw_encoded), secret)
        self.assertEqual(run_decode(tag_encoded), secret)
        
        # And they should produce different encodings
        self.assertNotEqual(zw_encoded, tag_encoded)


if __name__ == '__main__':
    # Run with verbose output to see the educational print statements
    unittest.main(verbosity=2)