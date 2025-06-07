"""
Hello World CLI Implementation - Worker-C

Command-line interface for the Hello World module with comprehensive
argument parsing and user-friendly error handling.

Usage:
    python -m hello_world.cli
    python -m hello_world.cli --greeting "Hi" --target "Python"
    python -m hello_world.cli --benchmark 1000
"""

import argparse
import sys
from typing import List, Optional

from .core import hello_world, print_hello_world, benchmark_hello_world, HelloWorldError


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the command-line argument parser.
    
    Returns:
        argparse.ArgumentParser: Configured parser instance
    """
    parser = argparse.ArgumentParser(
        prog="hello_world",
        description="Generate and display customizable greeting messages",
        epilog="Example: python -m hello_world.cli --greeting 'Hi' --target 'Python'"
    )
    
    parser.add_argument(
        "--greeting",
        default="Hello",
        help="The greeting part of the message (default: Hello)"
    )
    
    parser.add_argument(
        "--target", 
        default="World",
        help="The target of the greeting (default: World)"
    )
    
    parser.add_argument(
        "--benchmark",
        type=int,
        metavar="N",
        help="Run benchmark with N iterations and show performance stats"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress normal output (useful for benchmarking)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    return parser


def run_benchmark(iterations: int, quiet: bool = False) -> int:
    """Run performance benchmark and display results.
    
    Args:
        iterations: Number of benchmark iterations
        quiet: Whether to suppress detailed output
        
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    try:
        if not quiet:
            print(f"Running benchmark with {iterations} iterations...")
        
        avg_time = benchmark_hello_world(iterations)
        
        if not quiet:
            print(f"Average execution time: {avg_time:.6f} seconds")
            print(f"Total time for {iterations} calls: {avg_time * iterations:.6f} seconds")
            
            # Check performance requirement (1 second total for reasonable iterations)
            if avg_time * 1000 < 1.0:  # If 1000 calls take less than 1 second
                print("✅ Performance requirement satisfied (< 1 second for 1000 calls)")
            else:
                print("⚠️  Performance requirement check: consider optimization")
        
        return 0
        
    except Exception as e:
        print(f"Benchmark failed: {e}", file=sys.stderr)
        return 1


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI function with argument parsing and execution.
    
    Args:
        argv: Command line arguments (default: sys.argv[1:])
        
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    parser = create_parser()
    
    try:
        args = parser.parse_args(argv)
        
        # Handle benchmark mode
        if args.benchmark is not None:
            if args.benchmark <= 0:
                print("Error: benchmark iterations must be positive", file=sys.stderr)
                return 1
            return run_benchmark(args.benchmark, args.quiet)
        
        # Handle normal greeting mode
        if not args.quiet:
            print_hello_world(args.greeting, args.target)
        
        return 0
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 1
    except HelloWorldError as e:
        print(f"Hello World Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())