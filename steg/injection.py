"""
Injection point logic for determining where to place hidden characters.
"""


def find_injection_point(visible_text, injection_point):
    """Find where to inject hidden characters based on injection_point parameter."""
    if injection_point == "first-space":
        for i, char in enumerate(visible_text):
            if char.isspace():
                return i + 1
        raise ValueError("No whitespace found for first-space injection")
    
    elif injection_point == "end":
        return len(visible_text)
    
    elif injection_point.startswith("word-"):
        try:
            word_num = int(injection_point.split("-")[1])
            words = visible_text.split()
            if word_num < 1 or word_num > len(words):
                raise ValueError(f"Word {word_num} not found (text has {len(words)} words)")
            # Find position after the specified word
            word_end = 0
            for i in range(word_num):
                word_end = visible_text.find(words[i], word_end) + len(words[i])
            return word_end
        except (ValueError, IndexError):
            raise ValueError(f"Invalid word number in '{injection_point}'")
    
    elif injection_point.startswith("char-"):
        try:
            char_pos = int(injection_point.split("-")[1])
            if char_pos < 0 or char_pos > len(visible_text):
                raise ValueError(f"Character position {char_pos} out of range")
            return char_pos
        except ValueError:
            raise ValueError(f"Invalid character position in '{injection_point}'")
    
    else:
        raise ValueError(f"Unknown injection point: {injection_point}")