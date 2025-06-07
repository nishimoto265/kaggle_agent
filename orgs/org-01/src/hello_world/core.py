"""
Hello World Core Implementation - Boss Integrated Version

This module provides the core functionality for generating and displaying
the classic "Hello, World!" message with comprehensive error handling,
customization options, and performance monitoring.

Integration Strategy:
- Base: Worker-C's parameterized and extensible architecture
- Enhanced: Worker-A's professional CLI and I/O handling
- Refined: Worker-B's clean coding principles

Functions:
    hello_world() -> str: Returns the customizable greeting string
    print_hello_world() -> None: Prints the greeting with advanced I/O handling
    benchmark_hello_world() -> float: Performance benchmarking utility
    
Classes:
    HelloWorldError: Custom exception for hello world operations

Example:
    >>> from hello_world import hello_world, print_hello_world
    >>> message = hello_world()
    >>> print(message)
    Hello, World!
    >>> print_hello_world("Hi", "Python")
    Hi, Python!
"""

import sys
import time
from typing import Optional, TextIO, Tuple

__version__ = "1.0.0"
__author__ = "Boss Integration Agent"


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
    and target parameters with proper formatting and validation.
    
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
        >>> hello_world("Greetings", "Universe")
        'Greetings, Universe!'
    """
    # Type validation - enhanced from Worker-C
    if not isinstance(greeting, str):
        raise TypeError(f"greeting must be a string, got {type(greeting).__name__}")
    
    if not isinstance(target, str):
        raise TypeError(f"target must be a string, got {type(target).__name__}")
    
    # Content validation - enhanced from Worker-C
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
    """Print the hello world message to output stream with advanced I/O handling.
    
    This function prints the formatted greeting message with comprehensive
    error handling and output stream validation - enhanced from Worker-A.
    
    Args:
        greeting: The greeting part of the message (default: "Hello")
        target: The target of the greeting (default: "World")
        file: Output stream (default: sys.stdout)
        flush: Whether to forcibly flush the stream (default: False)
        
    Raises:
        HelloWorldError: If message generation or output fails
        RuntimeError: If output stream handling fails (from Worker-A)
        
    Example:
        >>> print_hello_world()
        Hello, World!
        >>> print_hello_world("Greetings", "Universe")
        Greetings, Universe!
    """
    try:
        # Generate message using enhanced hello_world function
        message = hello_world(greeting, target)
        
        # Use sys.stdout as default if no file specified
        output_stream = file or sys.stdout
        
        # Enhanced stream validation from Worker-A
        if hasattr(output_stream, 'writable') and not output_stream.writable():
            raise HelloWorldError("Output stream is not writable")
        
        # Print with error handling
        print(message, file=output_stream, flush=flush)
        
    except (TypeError, HelloWorldError) as e:
        # Re-raise our known exceptions
        raise
    except (OSError, IOError) as e:
        # Enhanced I/O error handling from Worker-A
        raise RuntimeError(f"Failed to output Hello World: {e}") from e
    except Exception as e:
        # Wrap unexpected exceptions
        raise HelloWorldError(f"Failed to print hello world message: {e}") from e


def timed_hello_world(
    greeting: str = "Hello", 
    target: str = "World"
) -> Tuple[str, float]:
    """Return Hello World string with execution time measurement.
    
    Enhanced timing functionality combining Worker-A and Worker-C approaches.
    
    Args:
        greeting: The greeting part of the message (default: "Hello")
        target: The target of the greeting (default: "World")
    
    Returns:
        Tuple[str, float]: A tuple containing the greeting string and 
                          the execution time in seconds.
                          
    Example:
        >>> result, exec_time = timed_hello_world()
        >>> result
        'Hello, World!'
        >>> exec_time < 1.0
        True
    """
    start_time = time.perf_counter()
    result = hello_world(greeting, target)
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    
    return result, execution_time


def benchmark_hello_world(iterations: int = 1000) -> float:
    """Benchmark the hello_world function performance.
    
    Measures the execution time for multiple calls to hello_world()
    to ensure performance requirements are met. Enhanced from Worker-C.
    
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
        Average time: 0.000115 seconds
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
    
    Enhanced CLI functionality combining Worker-A's professional approach
    with Worker-C's flexibility and Worker-B's clean error handling.
    
    Returns:
        int: Exit code (0 for success, 1 for error, 130 for keyboard interrupt)
    """
    try:
        # Enhanced execution with timing validation from Worker-A
        result, exec_time = timed_hello_world()
        print(result)
        
        # Performance requirement validation from Worker-A
        if exec_time >= 1.0:
            print(f"Warning: Execution took {exec_time:.4f}s (exceeds 1s limit)", 
                  file=sys.stderr)
            
        return 0
        
    except KeyboardInterrupt:
        # Enhanced keyboard interrupt handling from Worker-B
        print("\nOperation cancelled by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    """Direct script execution entry point with proper exit handling."""
    sys.exit(main())