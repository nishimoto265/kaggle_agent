"""Command line interface for Hello World module.

This module provides a command line interface for the Hello World functionality.
"""

import argparse
import sys
from typing import List, Optional

from .core import hello_world, print_hello_world, timed_hello_world


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.
    
    Returns:
        argparse.ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        description="Hello World CLI - A simple program that outputs 'Hello, World!'"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress output (for testing purposes)"
    )
    
    parser.add_argument(
        "--time", "-t",
        action="store_true", 
        help="Show execution time"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="Hello World CLI 1.0.0"
    )
    
    return parser


def cli_main(args: Optional[List[str]] = None) -> int:
    """Main CLI entry point.
    
    Args:
        args: Command line arguments. If None, uses sys.argv.
        
    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    parser = create_parser()
    
    try:
        parsed_args = parser.parse_args(args)
        
        if parsed_args.time:
            result, exec_time = timed_hello_world()
            if not parsed_args.quiet:
                print(result)
            print(f"Execution time: {exec_time:.6f}s", file=sys.stderr)
        else:
            if not parsed_args.quiet:
                print_hello_world()
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(cli_main())