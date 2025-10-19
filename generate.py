#!/usr/bin/env python3
"""
Card Print Generator - Main Entry Point

Generates printable sheets of cards with cut marks based on configuration.
"""

import sys
from src.sheet_generator import generate_sheets


def main():
    """Main entry point for the card print generator."""
    # Use config file from command line if provided, otherwise use default
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config/current.conf"
    generate_sheets(config_file)


if __name__ == "__main__":
    main()
