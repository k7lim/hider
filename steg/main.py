"""
Command-line interface for the steganography tool.
"""

import argparse
import sys

from .core import encode, decode
from .analysis import analyze
from .clipboard import copy_to_clipboard, read_from_clipboard

# Security limits
MAX_STDIN_SIZE = 10 * 1024 * 1024  # 10MB limit for stdin


def main():
    """Main function to parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="A tool to hide and reveal secret messages in text using Unicode steganography.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  # Encode with default TAG method after first space
  python -m steg encode "Hello world" "secret"

  # Encode with zero-width method at end of text
  python -m steg encode "Hello world" "secret" --method zero-width --inject end

  # Encode after the 2nd word
  python -m steg encode "The quick brown fox" "hidden" --inject word-2

  # Decode with auto-detection
  python -m steg decode "Hello ​‌‌‌​‌​​​‌‌​​‌​‌​‌‌‌​​‌‌​‌‌‌​‌​​world"

  # Analyze text for hidden characters
  cat some_file.txt | python -m steg analyze
"""
    )

    subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')

    # Encode command
    encode_parser = subparsers.add_parser('encode', help='Hide a secret message in visible text.')
    encode_parser.add_argument('visible_text', help='The text to be publicly visible.')
    encode_parser.add_argument('secret_message', help='The secret message to hide.')
    encode_parser.add_argument('--method', '-m', choices=['zero-width', 'tag'], default='tag',
                               help='Encoding method: tag (default) or zero-width (invisible)')
    encode_parser.add_argument('--inject', '-i', default='first-space',
                               help='Injection point: first-space (default), end, word-N (after Nth word), char-N (at character position N)')

    # Decode command
    decode_parser = subparsers.add_parser('decode', help='Reveal a secret message from text.')
    decode_parser.add_argument('text_to_decode', nargs='?', default=None, help='The text containing the hidden message. If not provided, will prompt to use clipboard.')
    decode_parser.add_argument('--method', '-m', choices=['auto', 'zero-width', 'tag'], default='auto',
                               help='Decoding method: auto (default, tries both), zero-width, or tag')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze text for any hidden characters.')
    analyze_parser.add_argument(
        'text_to_analyze',
        nargs='?',
        default=None,
        help='The text to analyze. If not provided, it reads from standard input.'
    )

    # Show help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        print("\n" + "="*60)
        print("QUICK START GUIDE")
        print("="*60)
        print("Most common usage (TAG chars after first space):")
        print('  python -m steg encode "Your public text here" "secret message"')
        print("  → Automatically copies encoded text to clipboard")
        print("\nTo decode any hidden message:")
        print('  python -m steg decode "text with hidden message"')
        print("  OR just: python -m steg decode")
        print("  → Will check clipboard and ask permission to decode")
        print("  → Auto-detects encoding method (zero-width or TAG)")
        print("\nTo analyze text for hidden characters:")
        print('  python -m steg analyze "suspicious text"')
        print("  → Works with piped input: cat file.txt | python -m steg analyze")
        print("\nAdvanced encoding options:")
        print("  --method: tag (default) or zero-width (invisible)")
        print("  --inject: first-space (default), end, word-N, char-N")
        print("\nUseful for watermarking, attribution, and steganography research.")
        print("="*60)
        sys.exit(0)

    # Check for incomplete commands before parsing
    if len(sys.argv) >= 2:
        if sys.argv[1] == 'encode' and len(sys.argv) < 4:
            print("Error: 'encode' command requires both visible text and secret message.")
            print("\nCorrect usage:")
            print('  python -m steg encode "Your visible text" "secret message"')
            print("\nFor full help, run: python -m steg")
            sys.exit(1)

    args = parser.parse_args()

    if args.command == 'encode':
        try:
            encoded_text = encode(args.visible_text, args.secret_message, args.method, args.inject)
            print("Encoded Message:")
            print("-" * 40)
            print(encoded_text)
            print("-" * 40)
            
            # Try to copy to clipboard
            if copy_to_clipboard(encoded_text):
                print("✓ Copied to clipboard!")
            else:
                print("⚠ Could not copy to clipboard automatically")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.command == 'decode':
        try:
            text_to_decode = args.text_to_decode
            
            # If no text provided, offer to use clipboard
            if not text_to_decode:
                clipboard_text = read_from_clipboard()
                if clipboard_text:
                    print(f"No text provided. Current clipboard contains:")
                    print(f"'{clipboard_text[:100]}{'...' if len(clipboard_text) > 100 else ''}'")
                    try:
                        response = input("\nUse clipboard contents for decoding? (y/n): ").lower().strip()
                        # Security: Validate user input
                        if response in ['y', 'yes', '1', 'true']:
                            text_to_decode = clipboard_text
                        elif response in ['n', 'no', '0', 'false', '']:
                            print("Cancelled.")
                            sys.exit(0)
                        else:
                            raise ValueError("Invalid response. Please enter 'y' or 'n'.")
                    except (KeyboardInterrupt, EOFError):
                        print("\nOperation cancelled.")
                        sys.exit(0)
                else:
                    print("Error: No text provided and could not read from clipboard.")
                    print("Usage: python -m steg decode 'text with hidden message'")
                    sys.exit(1)
            
            decoded_text = decode(text_to_decode, args.method)
            if decoded_text:
                print(f"Decoded Secret: {decoded_text}")
            else:
                print("No secret message found.")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.command == 'analyze':
        try:
            if args.text_to_analyze:
                analyze(args.text_to_analyze)
            elif not sys.stdin.isatty():
                # Read from stdin if it's piped
                try:
                    # Security: Limit stdin size to prevent memory exhaustion
                    stdin_data = []
                    total_size = 0
                    for line in sys.stdin:
                        line_size = len(line.encode('utf-8'))
                        if total_size + line_size > MAX_STDIN_SIZE:
                            raise ValueError(f"Input too large (max {MAX_STDIN_SIZE // 1024 // 1024}MB).")
                        stdin_data.append(line)
                        total_size += line_size
                    text_from_pipe = ''.join(stdin_data)
                    analyze(text_from_pipe)
                except KeyboardInterrupt:
                    print("\nOperation cancelled.")
                    sys.exit(0)
            else:
                print("Error: Provide text to analyze or pipe it into the command.")
                analyze_parser.print_help()
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)


if __name__ == '__main__':
    main()