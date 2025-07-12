"""
Unicode Steganography Tool

A modular package for hiding secret messages in plain text using invisible Unicode characters.
"""

from .algorithms import encode_zero_width, encode_tag, decode_zero_width, decode_tag
from .injection import find_injection_point
from .clipboard import copy_to_clipboard, read_from_clipboard
from .analysis import analyze
from .core import encode, decode

__version__ = "1.0.0"
__all__ = [
    "encode", "decode", "analyze",
    "encode_zero_width", "encode_tag", "decode_zero_width", "decode_tag",
    "find_injection_point", "copy_to_clipboard", "read_from_clipboard"
]