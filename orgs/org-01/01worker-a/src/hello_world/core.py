"""Core Hello World functionality.

This module provides the main functionality for outputting "Hello, World!".
It includes both a function that returns the string and a function that prints it.
"""

import sys
import time
from typing import Optional


def hello_world() -> str:
    """Return the Hello World string.
    
    Returns:
        str: The string "Hello, World!"
        
    Examples:
        >>> hello_world()
        'Hello, World!'
    """
    return "Hello, World!"


def print_hello_world(output_stream: Optional[object] = None) -> None:
    """Print Hello World to the specified output stream.
    
    Args:
        output_stream: Output stream to write to. Defaults to sys.stdout.
        
    Examples:
        >>> print_hello_world()
        Hello, World!
    """
    if output_stream is None:
        output_stream = sys.stdout
    
    try:
        print(hello_world(), file=output_stream)
    except (OSError, IOError) as e:
        # Handle potential I/O errors gracefully
        raise RuntimeError(f"Failed to output Hello World: {e}") from e


def timed_hello_world() -> tuple[str, float]:
    """Return Hello World string with execution time measurement.
    
    Returns:
        tuple[str, float]: A tuple containing the Hello World string and 
                          the execution time in seconds.
                          
    Examples:
        >>> result, exec_time = timed_hello_world()
        >>> result
        'Hello, World!'
        >>> exec_time < 1.0
        True
    """
    start_time = time.perf_counter()
    result = hello_world()
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    
    return result, execution_time


def main() -> None:
    """Main entry point for CLI execution.
    
    This function is called when the module is executed directly.
    It prints "Hello, World!" and ensures execution time is under 1 second.
    """
    try:
        result, exec_time = timed_hello_world()
        print(result)
        
        # Verify performance requirement
        if exec_time >= 1.0:
            print(f"Warning: Execution took {exec_time:.4f}s (exceeds 1s limit)", 
                  file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()