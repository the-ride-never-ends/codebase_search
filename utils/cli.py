#!/usr/bin/env python3
"""
Command line interface module for codebase search utility.

This module provides the command line interface for the codebase search
utility, including argument parsing and the main entry point.
"""
import argparse
from pathlib import Path
import sys
from typing import List, Optional

from utils.traversal import FileTraverser
from utils.search import TextSearchEngine
from utils.formatter import OutputFormatter


def parse_arguments(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Args:
        args: List of command line arguments (defaults to sys.argv[1:]).
    
    Returns:
        Parsed arguments as a Namespace object.
    """
    parser = argparse.ArgumentParser(
        description="Search codebase for patterns with structured output."
    )
    
    # Required arguments
    parser.add_argument(
        "pattern",
        required=True,
        help="The pattern to search for"
    )
    parser.add_argument(
        "path",
        required=True,
        type=str,
        help="The path to search in"
    )
    
    # Search options
    search_options = parser.add_argument_group("Search Options")
    search_options.add_argument(
        "--case-insensitive", "-i",
        action="store_true",
        help="Perform case-insensitive search (default: case-sensitive)"
    )
    search_options.add_argument(
        "--whole-word", "-w",
        action="store_true",
        help="Match whole words only (default: True) (type: bool)"
    )
    search_options.add_argument(
        "--regex", "-r",
        action="store_true",
        help="Interpret pattern as a regular expression (default: True) (type: bool)"
    )
    search_options.add_argument(
        "--extensions", "-e",
        help="Comma-separated list of file extensions to search (e.g., 'py,txt') (type: list[str])",
        type=lambda s: s.split(',') if s else None
    )
    search_options.add_argument(
        "--exclude", "-x",
        help="Comma-separated list of glob patterns to exclude (e.g., '*.git*,*node_modules*') (type: list[str])",
        type=lambda s: s.split(',') if s else None
    )
    search_options.add_argument(
        "--max-depth", "-d",
        type=int,
        help="Maximum directory depth to search"
    )
    search_options.add_argument(
        "--context", "-c",
        type=int,
        default=0,
        help="Number of lines of context to include before and after matches (default: 0) (type: int)"
    )
    
    # Output options
    output_options = parser.add_argument_group("Output Options")
    output_options.add_argument(
        "--format", "-f",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text) (type: str)"
    )
    output_options.add_argument(
        "--output", "-o",
        help="Write output to a file instead of stdout (type: Optional[str])",
    )
    output_options.add_argument(
        "--compact",
        action="store_true",
        help="Use compact output format (one line per match) (default: True) (type: bool)"
    )
    output_options.add_argument(
        "--group-by-file", "-g",
        action="store_true",
        help="Group results by file (default: True) (type: bool)"
    )
    output_options.add_argument(
        "--summary", "-s",
        action="store_true",
        help="Include summary information in output (default: True) (type: bool)"
    )
    
    # Parse arguments
    parsed_args = parser.parse_args(args)
    
    # Derive case_sensitive from case_insensitive (inverse logic)
    parsed_args.case_sensitive = not parsed_args.case_insensitive
    
    return parsed_args


def main() -> int:
    """
    Main function for the codebase search utility.
    
    Parses command line arguments, performs the search, and formats
    and outputs the results.
    
    Returns:
        Exit code: 0 for success with matches, 1 for no matches, 2 for errors.
    """
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Validate path
        search_path = Path(args.path)
        if not search_path.exists():
            sys.stderr.write(f"Error: Path does not exist: {args.path}\n")
            return 2
        
        # Initialize components
        traverser = FileTraverser(search_path)
        search_engine = TextSearchEngine()
        formatter = OutputFormatter()
        
        # Find files to search
        files = traverser.find_files(
            extensions=args.extensions,
            exclude_patterns=args.exclude,
            max_depth=args.max_depth
        )
        
        # Perform search
        all_results = []
        for file_path in files:
            try:
                results = search_engine.search_file(
                    file_path,
                    args.pattern,
                    case_sensitive=args.case_sensitive,
                    whole_word=args.whole_word,
                    use_regex=args.regex,
                    context_lines=args.context
                )
                all_results.extend(results)
            except Exception as e:
                # Skip problematic files but log the error
                sys.stderr.write(f"Warning: Error searching file {file_path}: {str(e)}\n")
        
        # Format results
        output = formatter.format(
            all_results,
            format_type=args.format,
            compact=args.compact,
            group_by_file=args.group_by_file,
            summary=args.summary
        )
        
        # Output results
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
        else:
            print(output)
        
        # Return appropriate code
        return 0 if all_results else 1
    
    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        return 2


def run_cli() -> None:
    """
    Entry point for the CLI that calls main() and exits with the returned code.
    
    This function should be used when running from the command line to properly
    exit the program. For testing, use main() directly to check the return code
    without exiting.
    """
    exit_code = main()
    sys.exit(exit_code)


if __name__ == "__main__":
    run_cli()