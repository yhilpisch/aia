#!/usr/bin/env python3
"""
Extract all user prompts from a Codex session JSON file.

Reads 'codex_session.json' by default and writes the text of every user
input prompt into an output text file (default 'user_prompts.txt'),
separating each prompt by a blank line.

Usage:
    python3 extract_user_prompts.py [INPUT_JSON] [OUTPUT_TXT]
"""

import json
import sys


def extract_prompts(input_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        session = json.load(f)
    prompts = []
    for item in session.get('items', []):
        if item.get('role') == 'user':
            for entry in item.get('content', []):
                text = entry.get('text')
                if text:
                    prompts.append(text)
    return prompts


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Extract user prompts from Codex session JSON.'
    )
    parser.add_argument(
        'input_json', nargs='?', default='codex_session.json',
        help='Path to the session JSON file'
    )
    parser.add_argument(
        'output_txt', nargs='?', default='user_prompts.txt',
        help='Path to write extracted prompts'
    )
    args = parser.parse_args()

    try:
        prompts = extract_prompts(args.input_json)
    except FileNotFoundError:
        print(f"Error: file not found: {args.input_json}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {args.input_json}: {e}", file=sys.stderr)
        sys.exit(1)

    if not prompts:
        print(f"No user prompts found in {args.input_json}", file=sys.stderr)
        sys.exit(1)

    with open(args.output_txt, 'w', encoding='utf-8') as f:
        for p in prompts:
            f.write(p.rstrip())
            f.write("\n\n")

    print(f"Wrote {len(prompts)} prompts to {args.output_txt}")


if __name__ == '__main__':
    main()