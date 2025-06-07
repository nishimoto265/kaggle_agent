"""
Hello World Module - Worker-C Implementation

A simple module demonstrating basic functionality with comprehensive testing and documentation.
Implements the classic "Hello, World!" output functionality with CLI support.

Author: Worker-C
Date: 2025-06-07
"""

from .core import hello_world, print_hello_world, HelloWorldError

__version__ = "1.0.0"
__author__ = "Worker-C"

__all__ = [
    "hello_world",
    "print_hello_world", 
    "HelloWorldError",
]