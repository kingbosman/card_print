#!/usr/bin/env python3
"""
Card Print Generator - Main Entry Point

Generates printable sheets of cards with cut marks based on configuration.
"""

from src.sheet_generator import generate_sheets


def main():
    """Main entry point for the card print generator."""
    generate_sheets("config/current.config")


if __name__ == "__main__":
    main()
