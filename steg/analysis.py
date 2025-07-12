"""
Text analysis functions for detecting hidden characters.
"""

import unicodedata


def analyze(text_to_analyze):
    """
    Identifies and prints all non-standard, potentially invisible characters in a text.
    """
    print("Analyzing text for hidden or non-standard Unicode characters...\n")
    found = False
    for i, char in enumerate(text_to_analyze):
        category = unicodedata.category(char)
        # 'Cc' is Control, 'Cf' is Format (includes many invisible chars), 'Cs' is Surrogate
        if category in ['Cc', 'Cf', 'Cs']:
            found = True
            char_name = unicodedata.name(char, 'UNKNOWN CHARACTER')
            print(f"  - Found at position {i}: U+{ord(char):04X} ({char_name})")

    if not found:
        print("No common invisible formatting or control characters were found.")