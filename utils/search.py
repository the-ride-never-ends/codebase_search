#!/usr/bin/env python3
"""
Text search engine module for codebase search utility.

This module provides functionality for searching text content in files
and collecting search results with context.
"""

import re
from pathlib import Path
from typing import List, Optional, Union, Pattern


class SearchResult:
    """
    Class to represent a single search result.
    
    Stores file path, line number, matched line content, and optional
    context lines before and after the match.
    """
    
    def __init__(
        self,
        file_path: str,
        line_number: int,
        line_content: str,
        context_before: Optional[List[str]] = None,
        context_after: Optional[List[str]] = None
    ):
        """
        Initialize a SearchResult object.
        
        Args:
            file_path: Path to the file containing the match.
            line_number: Line number of the match.
            line_content: Content of the line containing the match.
            context_before: Optional list of lines before the match.
            context_after: Optional list of lines after the match.
        """
        self.file_path = file_path
        self.line_number = line_number
        self.line_content = line_content
        self.context_before = context_before or []
        self.context_after = context_after or []


class TextSearchEngine:
    """
    Engine for searching text patterns in files.
    
    Provides methods to search for patterns in files with various options
    for case sensitivity, whole word matching, and regex support.
    """
    
    def __init__(self):
        """Initialize the TextSearchEngine."""
        pass
    
    def search_file(
        self,
        file_path: Union[str, Path],
        pattern: str,
        case_sensitive: bool = True,
        whole_word: bool = False,
        use_regex: bool = False,
        context_lines: int = 0
    ) -> List[SearchResult]:
        """
        Search for a pattern in a file.
        
        Args:
            file_path: Path to the file to search.
            pattern: The pattern to search for.
            case_sensitive: Whether the search is case sensitive.
            whole_word: Whether to match whole words only.
            use_regex: Whether to interpret the pattern as a regex pattern.
            context_lines: Number of context lines to include before and after matches.
        
        Returns:
            A list of SearchResult objects for each match found.
        """
        file_path_str = str(file_path)
        results = []
        
        try:
            # Compile the search pattern
            search_pattern = self._compile_pattern(
                pattern, case_sensitive, whole_word, use_regex
            )
            
            # Read file lines with a buffer for context
            file_lines = []
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_lines = f.readlines()
            except UnicodeDecodeError:
                # Try again with latin-1 encoding if utf-8 fails
                with open(file_path, 'r', encoding='latin-1') as f:
                    file_lines = f.readlines()
            
            # Process lines for matches
            for i, line in enumerate(file_lines):
                line_num = i + 1  # Line numbers are 1-based
                
                if search_pattern.search(line):
                    # Get context lines before match
                    start_idx = max(0, i - context_lines)
                    context_before = file_lines[start_idx:i] if context_lines > 0 else []
                    context_before = [line.rstrip('\n') for line in context_before]
                    
                    # Get context lines after match
                    end_idx = min(len(file_lines), i + context_lines + 1)
                    context_after = file_lines[i+1:end_idx] if context_lines > 0 else []
                    context_after = [line.rstrip('\n') for line in context_after]
                    
                    # Create search result
                    result = SearchResult(
                        file_path=file_path_str,
                        line_number=line_num,
                        line_content=line.rstrip('\n'),
                        context_before=context_before,
                        context_after=context_after
                    )
                    
                    results.append(result)
                    
        except (IOError, OSError) as e:
            # Handle file access errors silently in search function
            pass
        
        return results
    
    def _compile_pattern(
        self,
        pattern: str,
        case_sensitive: bool,
        whole_word: bool,
        use_regex: bool
    ) -> Pattern:
        """
        Compile a search pattern based on the specified options.
        
        Args:
            pattern: The pattern to compile.
            case_sensitive: Whether the pattern is case sensitive.
            whole_word: Whether to match whole words only.
            use_regex: Whether to interpret the pattern as a regex pattern.
        
        Returns:
            A compiled regular expression pattern.
        """
        # Escape pattern if not using regex
        if not use_regex:
            pattern = re.escape(pattern)
        
        # Add word boundary anchors if whole_word is True
        if whole_word:
            pattern = r'\b' + pattern + r'\b'
        
        # Compile with appropriate flags
        flags = 0 if case_sensitive else re.IGNORECASE
        return re.compile(pattern, flags)