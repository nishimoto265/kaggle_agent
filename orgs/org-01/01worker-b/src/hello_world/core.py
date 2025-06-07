"""Core Hello World functionality.

This module implements the main Hello World functions with proper error handling,
type annotations, and performance optimization.
"""

import sys
import time
from typing import NoReturn


def hello_world() -> str:
    """Return the classic Hello World message.
    
    Returns:
        str: The string "Hello, World!"
        
    Examples:
        >>> hello_world()
        'Hello, World!'
    """
    return "Hello, World!"


def print_hello_world() -> None:
    """Print the Hello World message to stdout.
    
    This function outputs the Hello World message directly to the console.
    Includes error handling for output stream issues.
    
    Raises:
        SystemExit: If output fails due to stream errors
        
    Examples:
        >>> print_hello_world()
        Hello, World!
    """
    try:
        print(hello_world())
    except (OSError, IOError) as e:
        # Handle potential output stream errors
        sys.stderr.write(f"Error writing to stdout: {e}\n")
        sys.exit(1)


def timed_hello_world() -> tuple[str, float]:
    """Return Hello World message with execution time.
    
    Returns:
        tuple[str, float]: A tuple containing the message and execution time in seconds
        
    Examples:
        >>> message, duration = timed_hello_world()
        >>> message
        'Hello, World!'
        >>> duration < 1.0
        True
    """
    start_time = time.perf_counter()
    message = hello_world()
    end_time = time.perf_counter()
    duration = end_time - start_time
    return message, duration


def main() -> NoReturn:
    """Command-line entry point for the Hello World module.
    
    This function provides CLI access to the Hello World functionality.
    Ensures execution completes within 1 second and exits cleanly.
    """
    try:
        message, duration = timed_hello_world()
        print(message)
        
        # Verify performance constraint
        if duration > 1.0:
            sys.stderr.write(f"Warning: Execution took {duration:.4f}s (>1s limit)\n")
            
        sys.exit(0)
    except KeyboardInterrupt:
        sys.stderr.write("\nInterrupted by user\n")
        sys.exit(130)
    except Exception as e:
        sys.stderr.write(f"Unexpected error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()