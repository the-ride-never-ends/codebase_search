#!/usr/bin/env python3
"""
Codebase Search Utility

A Python-based command-line utility that efficiently searches codebases for
specific keywords or patterns, providing clear and structured results.

This utility provides:
- Fast file system traversal with filtering options
- Text pattern search with regex and whole word support
- Multiple output formats (text, JSON)
- Context line inclusion
- Summary information

Usage:
    python codebase_search.py <pattern> <path> [options]

Example:
    python codebase_search.py "search_pattern" /path/to/codebase --extensions py,txt --context 2
"""

from .utils.cli import run_cli

if __name__ == "__main__":
    run_cli()