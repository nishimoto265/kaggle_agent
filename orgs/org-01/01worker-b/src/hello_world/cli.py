"""Command-line interface for Hello World module.

This module provides CLI functionality for the Hello World package,
allowing direct execution from the command line.
"""

import argparse
import sys
from typing import NoReturn

from .core import hello_world, print_hello_world, timed_hello_world


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser.
    
    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        prog="hello_world",
        description="Output Hello, World! message",
        epilog="Example: python -m hello_world.cli --quiet"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Return message without printing"
    )
    
    parser.add_argument(
        "--time", "-t",
        action="store_true",
        help="Show execution time"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="hello_world 1.0.0"
    )
    
    return parser


def cli_main() -> NoReturn:
    """Main CLI entry point.
    
    Parses command-line arguments and executes appropriate functionality.
    """
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        if args.time:
            message, duration = timed_hello_world()
            if not args.quiet:
                print(message)
            print(f"Execution time: {duration:.6f} seconds", file=sys.stderr)
        elif args.quiet:
            message = hello_world()
            # In quiet mode, just return the message without printing
            sys.exit(0)
        else:
            print_hello_world()
            
        sys.exit(0)
        
    except KeyboardInterrupt:
        sys.stderr.write("\nInterrupted by user\n")
        sys.exit(130)
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    cli_main()