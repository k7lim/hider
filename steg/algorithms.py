"""
Pure steganography algorithm functions.

These functions contain the core encoding/decoding logic without side effects.
"""

# Zero-width character mappings
ZERO_WIDTH_MAP = {
    '0': '\u200b',  # Zero-Width Space
    '1': '\u200c',  # Zero-Width Non-Joiner
}
ZERO_WIDTH_DECODE = {val: key for key, val in ZERO_WIDTH_MAP.items()}

# TAG character base for direct character encoding
TAG_BASE = 0xE0000  # Unicode TAG block base


def encode_zero_width(secret_message: str) -> str:
    """Convert secret message to zero-width characters using binary encoding."""
    binary_secret = ''.join(format(ord(char), '08b') for char in secret_message)
    return ''.join(ZERO_WIDTH_MAP.get(bit, '') for bit in binary_secret)


def encode_tag(secret_message: str) -> str:
    """Convert secret message to TAG characters with direct character mapping."""
    tag_chars = []
    for char in secret_message:
        if ord(char) <= 0x7F:  # Only ASCII characters
            tag_chars.append(chr(TAG_BASE + ord(char)))
        # Note: Silently skip non-ASCII chars (caller can warn if needed)
    return ''.join(tag_chars)


def decode_zero_width(encoded_text: str) -> str:
    """Extract secret message from zero-width characters."""
    binary_secret = ''.join(ZERO_WIDTH_DECODE.get(char, '') for char in encoded_text)
    secret_message = ''
    for i in range(0, len(binary_secret), 8):
        byte = binary_secret[i:i+8]
        if len(byte) == 8:
            try:
                secret_message += chr(int(byte, 2))
            except ValueError:
                pass
    return secret_message


def decode_tag(encoded_text: str) -> str:
    """Extract secret message from TAG characters."""
    secret_chars = []
    for char in encoded_text:
        char_code = ord(char)
        if TAG_BASE <= char_code <= TAG_BASE + 0x7F:
            original_char = chr(char_code - TAG_BASE)
            secret_chars.append(original_char)
    return ''.join(secret_chars)