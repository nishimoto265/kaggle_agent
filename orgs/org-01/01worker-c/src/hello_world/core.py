"""
Hello World Core Implementation - Worker-C

This module provides the core functionality for generating and displaying
the classic "Hello, World!" message with comprehensive error handling.

Functions:
    hello_world() -> str: Returns the "Hello, World!" string
    print_hello_world() -> None: Prints the "Hello, World!" message
    
Classes:
    HelloWorldError: Custom exception for hello world operations

Example:
    >>> from hello_world import hello_world, print_hello_world
    >>> message = hello_world()
    >>> print(message)
    Hello, World!
    >>> print_hello_world()
    Hello, World!
"""

import sys
import time
from typing import Optional, TextIO


class HelloWorldError(Exception):
    """Custom exception for Hello World module operations."""
    
    def __init__(self, message: str = "An error occurred in Hello World module") -> None:
        """Initialize HelloWorldError with custom message.
        
        Args:
            message: Error message describing the issue
        """
        super().__init__(message)
        self.message = message


def hello_world(greeting: str = "Hello", target: str = "World") -> str:
    """Generate a customizable greeting message.
    
    This function creates a greeting message by combining the greeting
    and target parameters with proper formatting.
    
    Args:
        greeting: The greeting part of the message (default: "Hello")
        target: The target of the greeting (default: "World")
        
    Returns:
        str: The formatted greeting message
        
    Raises:
        HelloWorldError: If inputs are invalid or empty
        TypeError: If inputs are not strings
        
    Example:
        >>> hello_world()
        'Hello, World!'
        >>> hello_world("Hi", "Python")
        'Hi, Python!'
    """
    if not isinstance(greeting, str):
        raise TypeError(f"greeting must be a string, got {type(greeting).__name__}")
    
    if not isinstance(target, str):
        raise TypeError(f"target must be a string, got {type(target).__name__}")
    
    if not greeting.strip():
        raise HelloWorldError("greeting cannot be empty or whitespace")
    
    if not target.strip():
        raise HelloWorldError("target cannot be empty or whitespace")
    
    # Clean inputs and format message
    greeting_clean = greeting.strip()
    target_clean = target.strip()
    
    return f"{greeting_clean}, {target_clean}!"


def print_hello_world(
    greeting: str = "Hello", 
    target: str = "World",
    file: Optional[TextIO] = None,
    flush: bool = False
) -> None:
    """Print the hello world message to output stream.
    
    This function prints the formatted greeting message with options
    for output customization and error handling.
    
    Args:
        greeting: The greeting part of the message (default: "Hello")
        target: The target of the greeting (default: "World")
        file: Output stream (default: sys.stdout)
        flush: Whether to forcibly flush the stream (default: False)
        
    Raises:
        HelloWorldError: If message generation fails
        OSError: If output stream is not writable
        
    Example:
        >>> print_hello_world()
        Hello, World!
        >>> print_hello_world("Greetings", "Universe")
        Greetings, Universe!
    """
    try:
        message = hello_world(greeting, target)
        
        # Use sys.stdout as default if no file specified
        output_stream = file or sys.stdout
        
        # Check if stream is writable
        if hasattr(output_stream, 'writable') and not output_stream.writable():
            raise HelloWorldError("Output stream is not writable")
        
        print(message, file=output_stream, flush=flush)
        
    except (TypeError, HelloWorldError) as e:
        # Re-raise our known exceptions
        raise
    except Exception as e:
        # Wrap unexpected exceptions
        raise HelloWorldError(f"Failed to print hello world message: {e}") from e


def benchmark_hello_world(iterations: int = 1000) -> float:
    """Benchmark the hello_world function performance.
    
    Measures the execution time for multiple calls to hello_world()
    to ensure performance requirements are met.
    
    Args:
        iterations: Number of function calls to benchmark (default: 1000)
        
    Returns:
        float: Average execution time per call in seconds
        
    Raises:
        ValueError: If iterations is not a positive integer
        HelloWorldError: If benchmarking fails
        
    Example:
        >>> avg_time = benchmark_hello_world(100)
        >>> print(f"Average time: {avg_time:.6f} seconds")
    """
    if not isinstance(iterations, int) or iterations <= 0:
        raise ValueError("iterations must be a positive integer")
    
    try:
        start_time = time.perf_counter()
        
        for _ in range(iterations):
            hello_world()
        
        end_time = time.perf_counter()
        
        total_time = end_time - start_time
        avg_time = total_time / iterations
        
        return avg_time
        
    except Exception as e:
        raise HelloWorldError(f"Benchmarking failed: {e}") from e


def main() -> int:
    """Main CLI entry point for the hello world module.
    
    Provides command-line interface functionality with basic argument
    handling and error management.
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    try:
        # Simple CLI - could be enhanced with argparse for more options
        print_hello_world()
        return 0
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    """Direct script execution entry point."""
    sys.exit(main())