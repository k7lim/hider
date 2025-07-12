"""
Core orchestration functions that coordinate between different modules.
"""

from .algorithms import encode_zero_width, encode_tag, decode_zero_width, decode_tag
from .injection import find_injection_point

# Security limits
MAX_SECRET_LENGTH = 10000  # Maximum characters in secret message
MAX_VISIBLE_LENGTH = 100000  # Maximum characters in visible text


def encode(visible_text, secret_message, method="tag", injection_point="first-space"):
    """
    Encodes a secret message into visible text using specified method and injection point.
    """
    if not visible_text:
        raise ValueError("Visible text cannot be empty for encoding.")
    
    # Security: Validate input lengths
    if len(visible_text) > MAX_VISIBLE_LENGTH:
        raise ValueError(f"Visible text too long (max {MAX_VISIBLE_LENGTH} characters).")
    
    if len(secret_message) > MAX_SECRET_LENGTH:
        raise ValueError(f"Secret message too long (max {MAX_SECRET_LENGTH} characters).")

    # find_injection_point already raises ValueError, no need to catch
    inject_pos = find_injection_point(visible_text, injection_point)

    if method == "zero-width":
        hidden_encoding = encode_zero_width(secret_message)
    elif method == "tag":
        # Check for non-ASCII characters and warn
        non_ascii_chars = [char for char in secret_message if ord(char) > 0x7F]
        if non_ascii_chars:
            print(f"Warning: Skipping non-ASCII characters in TAG mode: {non_ascii_chars}")
        hidden_encoding = encode_tag(secret_message)
    else:
        raise ValueError(f"Unknown encoding method '{method}'")
    
    # Insert hidden characters at the specified position
    return visible_text[:inject_pos] + hidden_encoding + visible_text[inject_pos:]


def decode(text_with_hidden_message, method="auto"):
    """
    Decodes a secret message hidden with specified method (auto-detects if not specified).
    """
    if method == "auto":
        # Try both methods and return whichever gives a result
        zero_width_result = decode(text_with_hidden_message, "zero-width")
        tag_result = decode(text_with_hidden_message, "tag")
        return zero_width_result if zero_width_result else tag_result
    
    elif method == "zero-width":
        return decode_zero_width(text_with_hidden_message)
    
    elif method == "tag":
        return decode_tag(text_with_hidden_message)
    
    else:
        raise ValueError(f"Unknown decoding method '{method}'")