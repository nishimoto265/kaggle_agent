"""Command line interface for Hello World module - Boss Integrated Version.

This module provides a comprehensive command line interface combining:
- Worker-A: Professional argparse configuration and help text
- Worker-C: Benchmark functionality and advanced features
- Worker-B: Clean error handling and exit codes

Features:
- Standard Hello World output
- Execution timing with performance validation
- Benchmarking mode for performance testing
- Customizable greetings and targets
- Quiet mode for scripting
- Professional help and version information
"""

import argparse
import sys
from typing import List, Optional

from .core import (
    hello_world, 
    print_hello_world, 
    timed_hello_world, 
    benchmark_hello_world,
    HelloWorldError,
    __version__
)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser with comprehensive options.
    
    Enhanced from Worker-A with additional features from Worker-C.
    
    Returns:
        argparse.ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        description="Hello World CLI - A comprehensive program for generating customizable greetings",
        epilog="Examples:\n"
               "  %(prog)s                    # Standard 'Hello, World!'\n"
               "  %(prog)s --greeting Hi --target Python\n"
               "  %(prog)s --time             # Show execution time\n"
               "  %(prog)s --benchmark 1000   # Performance benchmark\n"
               "  %(prog)s --quiet            # Suppress output",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Core functionality arguments
    parser.add_argument(
        "--greeting", "-g",
        default="Hello",
        help="Greeting part of the message (default: Hello)"
    )
    
    parser.add_argument(
        "--target", "-T",
        default="World", 
        help="Target of the greeting (default: World)"
    )
    
    # Output control arguments
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress message output (useful for timing/benchmarking)"
    )
    
    # Performance and timing arguments
    parser.add_argument(
        "--time", "-t",
        action="store_true", 
        help="Show execution time and performance validation"
    )
    
    parser.add_argument(
        "--benchmark", "-b",
        type=int,
        metavar="N",
        help="Run performance benchmark with N iterations (default: 1000)"
    )
    
    # Utility arguments
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"Hello World CLI {__version__}"
    )
    
    return parser


def cli_main(args: Optional[List[str]] = None) -> int:
    """Main CLI entry point with comprehensive functionality.
    
    Enhanced from Worker-A with Worker-C features and Worker-B error handling.
    
    Args:
        args: Command line arguments. If None, uses sys.argv.
        
    Returns:
        int: Exit code (0 for success, 1 for error, 130 for keyboard interrupt).
    """
    parser = create_parser()
    
    try:
        parsed_args = parser.parse_args(args)
        
        # Handle benchmark mode (from Worker-C)
        if parsed_args.benchmark is not None:
            iterations = parsed_args.benchmark if parsed_args.benchmark > 0 else 1000
            
            if not parsed_args.quiet:
                print(f"Running benchmark with {iterations} iterations...")
            
            avg_time = benchmark_hello_world(iterations)
            
            if not parsed_args.quiet:
                print(f"Average execution time: {avg_time:.6f} seconds")
                print(f"Performance status: {'✓ PASS' if avg_time < 1.0 else '✗ FAIL'} "
                      f"(<1s requirement)")
            
            # Return performance-based exit code
            return 0 if avg_time < 1.0 else 1
        
        # Handle timing mode (enhanced from Worker-A)
        elif parsed_args.time:
            result, exec_time = timed_hello_world(parsed_args.greeting, parsed_args.target)
            
            if not parsed_args.quiet:
                print(result)
            
            print(f"Execution time: {exec_time:.6f}s", file=sys.stderr)
            
            # Performance validation from Worker-A
            if exec_time >= 1.0:
                print(f"WARNING: Execution time exceeds 1s requirement", file=sys.stderr)
                return 1
        
        # Handle standard mode with customization (from Worker-C)
        else:
            if not parsed_args.quiet:
                print_hello_world(parsed_args.greeting, parsed_args.target)
        
        return 0
        
    except KeyboardInterrupt:
        # Enhanced keyboard interrupt handling from Worker-B
        print("\nOperation cancelled by user", file=sys.stderr)
        return 130
    except (HelloWorldError, ValueError, TypeError) as e:
        # Specific error handling for known exceptions
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        # Generic error handling
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def main() -> None:
    """Entry point for package execution."""
    sys.exit(cli_main())


if __name__ == "__main__":
    main()