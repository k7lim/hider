# Unicode Steganography Tool

A command-line tool for hiding secret messages in plain text using invisible Unicode characters. Useful for watermarking, attribution, and steganography research.

## Features

- **Two encoding methods:**
  - Zero-width characters (invisible in most contexts)
  - TAG characters (Unicode TAG block)
- **Flexible injection points:** after first space, end of text, after specific words, or at character positions
- **Auto-detection** when decoding
- **Clipboard integration** for easy copy/paste workflows
- **Comprehensive analysis** of hidden characters

## Quick Start

### Encode (hide a message)
```bash
python -m steg encode "Your public text here" "secret message"
```
→ Automatically copies encoded text to clipboard

### Decode (reveal hidden message)
```bash
python -m steg decode "text with hidden message"
# OR just check clipboard:
python -m steg decode
```

### Analyze text for hidden characters
```bash
python -m steg analyze "suspicious text"
cat file.txt | python -m steg analyze
```

## Advanced Usage

### Different encoding methods
```bash
# Zero-width (default, most invisible)
python -m steg encode "Hello world" "secret" --method zero-width

# TAG characters (like Grok prompt style)
python -m steg encode "Hello world" "secret" --method tag
```

### Different injection points
```bash
# After first space (default)
python -m steg encode "Hello world" "secret" --inject first-space

# At end of text
python -m steg encode "Hello world" "secret" --inject end

# After the 2nd word
python -m steg encode "The quick brown fox" "secret" --inject word-2

# At character position 5
python -m steg encode "Hello world" "secret" --inject char-5
```

## How It Works

The tool embeds secret messages using Unicode steganography:

1. **Zero-width method:** Converts the secret message to binary, then maps each bit to invisible Unicode characters (Zero Width Space `U+200B` and Zero Width Non-Joiner `U+200C`)

2. **TAG method:** Maps each character directly to its corresponding TAG block character (`U+E0000` range)

The hidden characters are injected at the specified position and preserved when text is copied and pasted.

## Project Structure

The tool is organized into focused modules:

```
steg/
├── __init__.py       # Package exports and version info
├── __main__.py       # Module entry point for python -m steg
├── algorithms.py     # Pure encoding/decoding algorithms 
├── analysis.py       # Text analysis for hidden characters
├── clipboard.py      # Cross-platform clipboard operations
├── core.py          # High-level encode/decode orchestration
├── injection.py     # Logic for where to inject hidden chars
└── main.py          # Command-line interface
```

## Testing

Run the test suite to verify functionality:
```bash
python test_steg.py -v
```

## Educational Purpose

This tool is designed for computer science education, demonstrating:
- Unicode steganography techniques
- Binary encoding/decoding
- Command-line argument parsing
- Error handling patterns
- Round-trip data validation

Perfect for students learning about text encoding, steganography, and defensive security techniques.

## Requirements

- Python 3.6+
- Platform-specific clipboard tools:
  - macOS: `pbcopy`/`pbpaste` (built-in)
  - Linux: `xclip`
  - Windows: `clip` (built-in)