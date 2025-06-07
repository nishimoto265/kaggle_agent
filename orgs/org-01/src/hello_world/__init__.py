"""
Hello World Module - Boss Integrated Implementation

A comprehensive Hello World module combining the best features from
all worker implementations:

- Worker-C: Parameterized, extensible architecture with custom exceptions
- Worker-A: Professional I/O handling and CLI sophistication  
- Worker-B: Clean, reliable coding patterns

This module provides both simple and advanced usage patterns for generating
and displaying Hello World messages.

Example Usage:
    Simple usage:
        >>> from hello_world import hello_world, print_hello_world
        >>> hello_world()
        'Hello, World!'
        >>> print_hello_world()
        Hello, World!
    
    Advanced usage:
        >>> from hello_world import hello_world, benchmark_hello_world
        >>> hello_world("Hi", "Python")
        'Hi, Python!'
        >>> avg_time = benchmark_hello_world(1000)
        >>> print(f"Average execution time: {avg_time:.6f}s")
        Average execution time: 0.000115s
"""

from .core import (
    hello_world,
    print_hello_world,
    timed_hello_world,
    benchmark_hello_world,
    HelloWorldError,
    main,
    __version__,
    __author__
)

__all__ = [
    'hello_world',
    'print_hello_world', 
    'timed_hello_world',
    'benchmark_hello_world',
    'HelloWorldError',
    'main',
    '__version__',
    '__author__'
]

# Module metadata
__version__ = "1.0.0"
__author__ = "Boss Integration Agent"
__description__ = "Integrated Hello World module with advanced features"