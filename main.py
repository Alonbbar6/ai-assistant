#!/usr/bin/env python3
"""
Personal AI Assistant — entry point.

Usage:
    python main.py              # text mode
    python main.py --voice      # voice input + output
    python main.py --voice-in   # voice input only
"""

import argparse
import sys
import os


def check_env():
    from config import ANTHROPIC_API_KEY
    if not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Personal AI Assistant")
    parser.add_argument("--voice", action="store_true", help="Enable voice input and output")
    parser.add_argument("--voice-in", action="store_true", help="Enable voice input only")
    args = parser.parse_args()

    check_env()

    from ui.cli import run_cli
    run_cli(voice_output=args.voice)


if __name__ == "__main__":
    main()
