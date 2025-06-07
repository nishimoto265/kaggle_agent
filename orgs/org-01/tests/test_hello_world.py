"""
Comprehensive test suite for Hello World module - Boss Integrated Version

This test suite combines the best testing approaches from all workers:
- Worker-A: Professional subprocess testing and integration tests
- Worker-B: Clean test organization and essential coverage
- Worker-C: Extensive edge cases and performance validation

Test Coverage:
- Core functionality (hello_world, print_hello_world)
- Error handling and validation
- Performance requirements and benchmarking
- CLI functionality and argument parsing
- Edge cases and boundary conditions
- Integration and subprocess testing
"""

import io
import subprocess
import sys
import time
import unittest
from contextlib import redirect_stdout, redirect_stderr
from typing import List, Optional
from unittest.mock import patch, MagicMock

import pytest

from src.hello_world.core import (
    hello_world,
    print_hello_world,
    timed_hello_world,
    benchmark_hello_world,
    HelloWorldError,
    main as core_main
)
from src.hello_world.cli import cli_main, create_parser


class TestHelloWorldCore(unittest.TestCase):
    """Test core hello_world functionality."""
    
    def test_hello_world_default(self):
        """Test default hello_world behavior."""
        result = hello_world()
        self.assertEqual(result, "Hello, World!")
        self.assertIsInstance(result, str)
    
    def test_hello_world_custom_greeting(self):
        """Test custom greeting parameter."""
        result = hello_world("Hi")
        self.assertEqual(result, "Hi, World!")
    
    def test_hello_world_custom_target(self):
        """Test custom target parameter."""
        result = hello_world(target="Python")
        self.assertEqual(result, "Hello, Python!")
    
    def test_hello_world_custom_both(self):
        """Test custom greeting and target."""
        result = hello_world("Greetings", "Universe")
        self.assertEqual(result, "Greetings, Universe!")
    
    def test_hello_world_with_whitespace(self):
        """Test handling of whitespace in parameters."""
        result = hello_world("  Hello  ", "  World  ")
        self.assertEqual(result, "Hello, World!")
    
    def test_hello_world_type_validation_greeting(self):
        """Test type validation for greeting parameter."""
        with self.assertRaises(TypeError) as cm:
            hello_world(123, "World")
        self.assertIn("greeting must be a string", str(cm.exception))
    
    def test_hello_world_type_validation_target(self):
        """Test type validation for target parameter."""
        with self.assertRaises(TypeError) as cm:
            hello_world("Hello", None)
        self.assertIn("target must be a string", str(cm.exception))
    
    def test_hello_world_empty_greeting(self):
        """Test validation of empty greeting."""
        with self.assertRaises(HelloWorldError) as cm:
            hello_world("", "World")
        self.assertIn("greeting cannot be empty", str(cm.exception))
    
    def test_hello_world_empty_target(self):
        """Test validation of empty target."""
        with self.assertRaises(HelloWorldError) as cm:
            hello_world("Hello", "")
        self.assertIn("target cannot be empty", str(cm.exception))
    
    def test_hello_world_whitespace_only_greeting(self):
        """Test validation of whitespace-only greeting."""
        with self.assertRaises(HelloWorldError):
            hello_world("   ", "World")
    
    def test_hello_world_whitespace_only_target(self):
        """Test validation of whitespace-only target."""
        with self.assertRaises(HelloWorldError):
            hello_world("Hello", "   ")
    
    def test_hello_world_unicode_support(self):
        """Test Unicode character support."""
        result = hello_world("Здравствуй", "Мир")
        self.assertEqual(result, "Здравствуй, Мир!")
        
        result = hello_world("こんにちは", "世界")
        self.assertEqual(result, "こんにちは, 世界!")
    
    def test_hello_world_special_characters(self):
        """Test special character handling."""
        result = hello_world("Hello!", "@World")
        self.assertEqual(result, "Hello!, @World!")


class TestPrintHelloWorld(unittest.TestCase):
    """Test print_hello_world functionality."""
    
    def test_print_hello_world_default(self):
        """Test default print behavior."""
        output = io.StringIO()
        print_hello_world(file=output)
        self.assertEqual(output.getvalue().strip(), "Hello, World!")
    
    def test_print_hello_world_custom(self):
        """Test custom parameters."""
        output = io.StringIO()
        print_hello_world("Hi", "Python", file=output)
        self.assertEqual(output.getvalue().strip(), "Hi, Python!")
    
    def test_print_hello_world_flush(self):
        """Test flush parameter."""
        output = io.StringIO()
        print_hello_world(file=output, flush=True)
        self.assertEqual(output.getvalue().strip(), "Hello, World!")
    
    def test_print_hello_world_invalid_stream(self):
        """Test handling of invalid output stream."""
        # Create a mock stream that's not writable
        mock_stream = MagicMock()
        mock_stream.writable.return_value = False
        
        with self.assertRaises(HelloWorldError) as cm:
            print_hello_world(file=mock_stream)
        self.assertIn("not writable", str(cm.exception))
    
    def test_print_hello_world_io_error(self):
        """Test handling of I/O errors."""
        # Create a mock stream that raises IOError on write
        mock_stream = MagicMock()
        mock_stream.write.side_effect = IOError("Mock I/O error")
        
        with self.assertRaises(RuntimeError) as cm:
            print_hello_world(file=mock_stream)
        self.assertIn("Failed to output Hello World", str(cm.exception))
    
    def test_print_hello_world_propagates_validation_errors(self):
        """Test that validation errors from hello_world are propagated."""
        with self.assertRaises(TypeError):
            print_hello_world(123, "World")
        
        with self.assertRaises(HelloWorldError):
            print_hello_world("", "World")


class TestTimedHelloWorld(unittest.TestCase):
    """Test timed_hello_world functionality."""
    
    def test_timed_hello_world_default(self):
        """Test timed execution with default parameters."""
        result, exec_time = timed_hello_world()
        self.assertEqual(result, "Hello, World!")
        self.assertIsInstance(exec_time, float)
        self.assertGreater(exec_time, 0)
        self.assertLess(exec_time, 1.0)  # Performance requirement
    
    def test_timed_hello_world_custom(self):
        """Test timed execution with custom parameters."""
        result, exec_time = timed_hello_world("Hi", "Python")
        self.assertEqual(result, "Hi, Python!")
        self.assertIsInstance(exec_time, float)
        self.assertGreater(exec_time, 0)
    
    def test_timed_hello_world_performance_requirement(self):
        """Test that execution time meets performance requirements."""
        for _ in range(10):  # Test multiple times for consistency
            _, exec_time = timed_hello_world()
            self.assertLess(exec_time, 1.0, "Execution time exceeds 1 second limit")


class TestBenchmarkHelloWorld(unittest.TestCase):
    """Test benchmark_hello_world functionality."""
    
    def test_benchmark_default_iterations(self):
        """Test benchmark with default iterations."""
        avg_time = benchmark_hello_world()
        self.assertIsInstance(avg_time, float)
        self.assertGreater(avg_time, 0)
        self.assertLess(avg_time, 1.0)  # Should be much less than 1 second
    
    def test_benchmark_custom_iterations(self):
        """Test benchmark with custom iterations."""
        avg_time = benchmark_hello_world(100)
        self.assertIsInstance(avg_time, float)
        self.assertGreater(avg_time, 0)
    
    def test_benchmark_single_iteration(self):
        """Test benchmark with single iteration."""
        avg_time = benchmark_hello_world(1)
        self.assertIsInstance(avg_time, float)
        self.assertGreater(avg_time, 0)
    
    def test_benchmark_invalid_iterations_type(self):
        """Test benchmark with invalid iterations type."""
        with self.assertRaises(ValueError):
            benchmark_hello_world("invalid")
    
    def test_benchmark_invalid_iterations_value(self):
        """Test benchmark with invalid iterations value."""
        with self.assertRaises(ValueError):
            benchmark_hello_world(0)
        
        with self.assertRaises(ValueError):
            benchmark_hello_world(-1)
    
    def test_benchmark_performance_consistency(self):
        """Test benchmark performance consistency."""
        times = [benchmark_hello_world(100) for _ in range(5)]
        
        # All times should be reasonable
        for time_val in times:
            self.assertLess(time_val, 0.001)  # Should be very fast
        
        # Times should be relatively consistent (within order of magnitude)
        max_time = max(times)
        min_time = min(times)
        self.assertLess(max_time / min_time, 10)  # Max 10x variation


class TestHelloWorldError(unittest.TestCase):
    """Test HelloWorldError exception class."""
    
    def test_hello_world_error_default_message(self):
        """Test HelloWorldError with default message."""
        error = HelloWorldError()
        self.assertIn("An error occurred in Hello World module", str(error))
        self.assertEqual(error.message, "An error occurred in Hello World module")
    
    def test_hello_world_error_custom_message(self):
        """Test HelloWorldError with custom message."""
        custom_message = "Custom error message"
        error = HelloWorldError(custom_message)
        self.assertEqual(str(error), custom_message)
        self.assertEqual(error.message, custom_message)


class TestCoreMain(unittest.TestCase):
    """Test core main function."""
    
    def test_core_main_success(self):
        """Test successful execution of core main."""
        with redirect_stdout(io.StringIO()) as output:
            result = core_main()
        
        self.assertEqual(result, 0)
        self.assertEqual(output.getvalue().strip(), "Hello, World!")
    
    def test_core_main_keyboard_interrupt(self):
        """Test keyboard interrupt handling in core main."""
        with patch('src.hello_world.core.timed_hello_world') as mock_timed:
            mock_timed.side_effect = KeyboardInterrupt()
            
            with redirect_stderr(io.StringIO()) as stderr:
                result = core_main()
            
            self.assertEqual(result, 130)
            self.assertIn("cancelled by user", stderr.getvalue())


class TestCLIFunctionality(unittest.TestCase):
    """Test CLI functionality."""
    
    def test_create_parser(self):
        """Test parser creation."""
        parser = create_parser()
        self.assertIsInstance(parser, argparse.ArgumentParser)
    
    def test_cli_main_default(self):
        """Test CLI with default arguments."""
        with redirect_stdout(io.StringIO()) as output:
            result = cli_main([])
        
        self.assertEqual(result, 0)
        self.assertEqual(output.getvalue().strip(), "Hello, World!")
    
    def test_cli_main_custom_greeting(self):
        """Test CLI with custom greeting."""
        with redirect_stdout(io.StringIO()) as output:
            result = cli_main(["--greeting", "Hi"])
        
        self.assertEqual(result, 0)
        self.assertEqual(output.getvalue().strip(), "Hi, World!")
    
    def test_cli_main_custom_target(self):
        """Test CLI with custom target."""
        with redirect_stdout(io.StringIO()) as output:
            result = cli_main(["--target", "Python"])
        
        self.assertEqual(result, 0)
        self.assertEqual(output.getvalue().strip(), "Hello, Python!")
    
    def test_cli_main_custom_both(self):
        """Test CLI with custom greeting and target."""
        with redirect_stdout(io.StringIO()) as output:
            result = cli_main(["--greeting", "Hi", "--target", "Python"])
        
        self.assertEqual(result, 0)
        self.assertEqual(output.getvalue().strip(), "Hi, Python!")
    
    def test_cli_main_quiet_mode(self):
        """Test CLI quiet mode."""
        with redirect_stdout(io.StringIO()) as output:
            result = cli_main(["--quiet"])
        
        self.assertEqual(result, 0)
        self.assertEqual(output.getvalue(), "")
    
    def test_cli_main_time_mode(self):
        """Test CLI time mode."""
        with redirect_stdout(io.StringIO()) as stdout:
            with redirect_stderr(io.StringIO()) as stderr:
                result = cli_main(["--time"])
        
        self.assertEqual(result, 0)
        self.assertEqual(stdout.getvalue().strip(), "Hello, World!")
        self.assertIn("Execution time:", stderr.getvalue())
    
    def test_cli_main_benchmark_mode(self):
        """Test CLI benchmark mode."""
        with redirect_stdout(io.StringIO()) as output:
            result = cli_main(["--benchmark", "10"])
        
        self.assertEqual(result, 0)
        output_text = output.getvalue()
        self.assertIn("benchmark", output_text.lower())
        self.assertIn("average execution time", output_text.lower())
    
    def test_cli_main_benchmark_quiet(self):
        """Test CLI benchmark in quiet mode."""
        with redirect_stdout(io.StringIO()) as output:
            result = cli_main(["--benchmark", "10", "--quiet"])
        
        self.assertEqual(result, 0)
        self.assertEqual(output.getvalue(), "")
    
    def test_cli_main_keyboard_interrupt(self):
        """Test CLI keyboard interrupt handling."""
        with patch('src.hello_world.cli.timed_hello_world') as mock_timed:
            mock_timed.side_effect = KeyboardInterrupt()
            
            with redirect_stderr(io.StringIO()) as stderr:
                result = cli_main(["--time"])
            
            self.assertEqual(result, 130)
            self.assertIn("cancelled by user", stderr.getvalue())
    
    def test_cli_main_error_handling(self):
        """Test CLI error handling."""
        with redirect_stderr(io.StringIO()) as stderr:
            result = cli_main(["--greeting", ""])
        
        self.assertEqual(result, 1)
        self.assertIn("Error:", stderr.getvalue())


class TestIntegrationAndSubprocess(unittest.TestCase):
    """Integration tests using subprocess execution."""
    
    def test_module_execution_direct(self):
        """Test direct module execution."""
        result = subprocess.run(
            [sys.executable, "-m", "src.hello_world.core"],
            cwd=".",
            capture_output=True,
            text=True,
            timeout=5
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "Hello, World!")
    
    def test_cli_execution_subprocess(self):
        """Test CLI execution via subprocess."""
        result = subprocess.run(
            [sys.executable, "-m", "src.hello_world.cli"],
            cwd=".",
            capture_output=True,
            text=True,
            timeout=5
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "Hello, World!")
    
    def test_cli_custom_args_subprocess(self):
        """Test CLI with arguments via subprocess."""
        result = subprocess.run(
            [sys.executable, "-m", "src.hello_world.cli", "--greeting", "Hi", "--target", "Python"],
            cwd=".",
            capture_output=True,
            text=True,
            timeout=5
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "Hi, Python!")
    
    def test_performance_requirement_subprocess(self):
        """Test performance requirement via subprocess."""
        start_time = time.time()
        result = subprocess.run(
            [sys.executable, "-m", "src.hello_world.core"],
            cwd=".",
            capture_output=True,
            text=True,
            timeout=5
        )
        end_time = time.time()
        
        self.assertEqual(result.returncode, 0)
        self.assertLess(end_time - start_time, 1.0)  # Should complete well under 1 second


class TestEdgeCasesAndBoundaryConditions(unittest.TestCase):
    """Test edge cases and boundary conditions."""
    
    def test_extremely_long_strings(self):
        """Test with very long input strings."""
        long_greeting = "A" * 1000
        long_target = "B" * 1000
        
        result = hello_world(long_greeting, long_target)
        expected = f"{long_greeting}, {long_target}!"
        self.assertEqual(result, expected)
    
    def test_unicode_edge_cases(self):
        """Test various Unicode edge cases."""
        # Emoji support
        result = hello_world("👋", "🌍")
        self.assertEqual(result, "👋, 🌍!")
        
        # Mixed scripts
        result = hello_world("Hello", "世界")
        self.assertEqual(result, "Hello, 世界!")
        
        # Right-to-left languages
        result = hello_world("مرحبا", "عالم")
        self.assertEqual(result, "مرحبا, عالم!")
    
    def test_memory_efficiency(self):
        """Test memory efficiency with large number of calls."""
        import gc
        
        # Force garbage collection before test
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Make many calls
        for _ in range(1000):
            hello_world()
        
        # Force garbage collection after test
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Object count should not grow significantly
        self.assertLess(final_objects - initial_objects, 100)


# Performance benchmark as pytest fixture for detailed reporting
@pytest.mark.benchmark
def test_performance_benchmark():
    """Performance benchmark test using pytest-benchmark if available."""
    def hello_world_call():
        return hello_world()
    
    # Basic performance test
    start_time = time.perf_counter()
    result = hello_world_call()
    end_time = time.perf_counter()
    
    assert result == "Hello, World!"
    assert end_time - start_time < 1.0


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)