"""
Comprehensive Test Suite for Hello World Module - Worker-C

This test module provides 100% code coverage for the hello_world module,
testing all functions, error conditions, and edge cases.

Test Categories:
- Core functionality tests
- Error handling tests
- CLI functionality tests
- Performance/benchmark tests
- Integration tests
"""

import io
import sys
import time
import pytest
from unittest.mock import patch, MagicMock

# Import the module under test
from src.hello_world.core import (
    hello_world,
    print_hello_world,
    benchmark_hello_world,
    main,
    HelloWorldError
)
from src.hello_world.cli import create_parser, run_benchmark, main as cli_main


class TestHelloWorldCore:
    """Test cases for core hello_world functionality."""
    
    def test_hello_world_default(self):
        """Test hello_world with default parameters."""
        result = hello_world()
        assert result == "Hello, World!"
        assert isinstance(result, str)
    
    def test_hello_world_custom_greeting(self):
        """Test hello_world with custom greeting."""
        result = hello_world("Hi")
        assert result == "Hi, World!"
    
    def test_hello_world_custom_target(self):
        """Test hello_world with custom target."""
        result = hello_world(target="Python")
        assert result == "Hello, Python!"
    
    def test_hello_world_custom_both(self):
        """Test hello_world with both custom parameters."""
        result = hello_world("Greetings", "Universe")
        assert result == "Greetings, Universe!"
    
    def test_hello_world_whitespace_handling(self):
        """Test hello_world handles whitespace correctly."""
        result = hello_world("  Hello  ", "  World  ")
        assert result == "Hello, World!"
    
    def test_hello_world_empty_greeting_error(self):
        """Test hello_world raises error for empty greeting."""
        with pytest.raises(HelloWorldError, match="greeting cannot be empty"):
            hello_world("")
        
        with pytest.raises(HelloWorldError, match="greeting cannot be empty"):
            hello_world("   ")
    
    def test_hello_world_empty_target_error(self):
        """Test hello_world raises error for empty target."""
        with pytest.raises(HelloWorldError, match="target cannot be empty"):
            hello_world("Hello", "")
        
        with pytest.raises(HelloWorldError, match="target cannot be empty"):
            hello_world("Hello", "   ")
    
    def test_hello_world_type_error_greeting(self):
        """Test hello_world raises TypeError for non-string greeting."""
        with pytest.raises(TypeError, match="greeting must be a string"):
            hello_world(123)
        
        with pytest.raises(TypeError, match="greeting must be a string"):
            hello_world(None)
    
    def test_hello_world_type_error_target(self):
        """Test hello_world raises TypeError for non-string target."""
        with pytest.raises(TypeError, match="target must be a string"):
            hello_world("Hello", 123)
        
        with pytest.raises(TypeError, match="target must be a string"):
            hello_world("Hello", None)


class TestPrintHelloWorld:
    """Test cases for print_hello_world functionality."""
    
    def test_print_hello_world_default(self, capsys):
        """Test print_hello_world with default parameters."""
        print_hello_world()
        captured = capsys.readouterr()
        assert captured.out == "Hello, World!\n"
        assert captured.err == ""
    
    def test_print_hello_world_custom(self, capsys):
        """Test print_hello_world with custom parameters."""
        print_hello_world("Hi", "Python")
        captured = capsys.readouterr()
        assert captured.out == "Hi, Python!\n"
    
    def test_print_hello_world_custom_file(self):
        """Test print_hello_world with custom file output."""
        output = io.StringIO()
        print_hello_world(file=output)
        assert output.getvalue() == "Hello, World!\n"
    
    def test_print_hello_world_flush(self):
        """Test print_hello_world with flush parameter."""
        output = io.StringIO()
        print_hello_world(file=output, flush=True)
        assert output.getvalue() == "Hello, World!\n"
    
    def test_print_hello_world_error_propagation(self):
        """Test print_hello_world propagates HelloWorldError."""
        with pytest.raises(HelloWorldError):
            print_hello_world("")
    
    def test_print_hello_world_type_error_propagation(self):
        """Test print_hello_world propagates TypeError."""
        with pytest.raises(TypeError):
            print_hello_world(123)
    
    def test_print_hello_world_non_writable_stream(self):
        """Test print_hello_world with non-writable stream."""
        mock_stream = MagicMock()
        mock_stream.writable.return_value = False
        
        with pytest.raises(HelloWorldError, match="Output stream is not writable"):
            print_hello_world(file=mock_stream)
    
    def test_print_hello_world_stream_without_writable_method(self):
        """Test print_hello_world with stream without writable method."""
        # Create a mock stream without writable method
        class MockStream:
            def __init__(self):
                self._content = ""
            
            def write(self, text):
                self._content += text
            
            def flush(self):
                pass
            
            def getvalue(self):
                return self._content
        
        output = MockStream()
        print_hello_world(file=output)
        assert output.getvalue() == "Hello, World!\n"
    
    @patch('src.hello_world.core.hello_world')
    def test_print_hello_world_unexpected_error(self, mock_hello_world):
        """Test print_hello_world handles unexpected errors."""
        mock_hello_world.side_effect = RuntimeError("Unexpected error")
        
        with pytest.raises(HelloWorldError, match="Failed to print hello world message"):
            print_hello_world()


class TestBenchmarkHelloWorld:
    """Test cases for benchmark_hello_world functionality."""
    
    def test_benchmark_hello_world_default(self):
        """Test benchmark_hello_world with default iterations."""
        avg_time = benchmark_hello_world()
        assert isinstance(avg_time, float)
        assert avg_time > 0
        assert avg_time < 0.001  # Should be very fast
    
    def test_benchmark_hello_world_custom_iterations(self):
        """Test benchmark_hello_world with custom iterations."""
        avg_time = benchmark_hello_world(100)
        assert isinstance(avg_time, float)
        assert avg_time > 0
    
    def test_benchmark_hello_world_single_iteration(self):
        """Test benchmark_hello_world with single iteration."""
        avg_time = benchmark_hello_world(1)
        assert isinstance(avg_time, float)
        assert avg_time > 0
    
    def test_benchmark_hello_world_invalid_iterations(self):
        """Test benchmark_hello_world with invalid iterations."""
        with pytest.raises(ValueError, match="iterations must be a positive integer"):
            benchmark_hello_world(0)
        
        with pytest.raises(ValueError, match="iterations must be a positive integer"):
            benchmark_hello_world(-1)
        
        with pytest.raises(ValueError, match="iterations must be a positive integer"):
            benchmark_hello_world("100")
    
    @patch('src.hello_world.core.hello_world')
    def test_benchmark_hello_world_function_error(self, mock_hello_world):
        """Test benchmark_hello_world handles function errors."""
        mock_hello_world.side_effect = RuntimeError("Function error")
        
        with pytest.raises(HelloWorldError, match="Benchmarking failed"):
            benchmark_hello_world(10)


class TestMainFunction:
    """Test cases for main function functionality."""
    
    def test_main_success(self, capsys):
        """Test main function successful execution."""
        result = main()
        assert result == 0
        captured = capsys.readouterr()
        assert captured.out == "Hello, World!\n"
    
    @patch('src.hello_world.core.print_hello_world')
    def test_main_keyboard_interrupt(self, mock_print, capsys):
        """Test main function handles KeyboardInterrupt."""
        mock_print.side_effect = KeyboardInterrupt()
        
        result = main()
        assert result == 1
        captured = capsys.readouterr()
        assert "Operation cancelled by user" in captured.err
    
    @patch('src.hello_world.core.print_hello_world')
    def test_main_generic_exception(self, mock_print, capsys):
        """Test main function handles generic exceptions."""
        mock_print.side_effect = RuntimeError("Some error")
        
        result = main()
        assert result == 1
        captured = capsys.readouterr()
        assert "Error: Some error" in captured.err


class TestHelloWorldError:
    """Test cases for HelloWorldError exception class."""
    
    def test_hello_world_error_default_message(self):
        """Test HelloWorldError with default message."""
        error = HelloWorldError()
        assert str(error) == "An error occurred in Hello World module"
        assert error.message == "An error occurred in Hello World module"
    
    def test_hello_world_error_custom_message(self):
        """Test HelloWorldError with custom message."""
        error = HelloWorldError("Custom error message")
        assert str(error) == "Custom error message"
        assert error.message == "Custom error message"


class TestCLIFunctionality:
    """Test cases for CLI functionality."""
    
    def test_create_parser(self):
        """Test CLI parser creation."""
        parser = create_parser()
        assert parser.prog == "hello_world"
        assert "Generate and display customizable greeting messages" in parser.description
    
    def test_cli_default_arguments(self, capsys):
        """Test CLI with default arguments."""
        result = cli_main([])
        assert result == 0
        captured = capsys.readouterr()
        assert captured.out == "Hello, World!\n"
    
    def test_cli_custom_greeting(self, capsys):
        """Test CLI with custom greeting."""
        result = cli_main(["--greeting", "Hi"])
        assert result == 0
        captured = capsys.readouterr()
        assert captured.out == "Hi, World!\n"
    
    def test_cli_custom_target(self, capsys):
        """Test CLI with custom target."""
        result = cli_main(["--target", "Python"])
        assert result == 0
        captured = capsys.readouterr()
        assert captured.out == "Hello, Python!\n"
    
    def test_cli_custom_both(self, capsys):
        """Test CLI with both custom parameters."""
        result = cli_main(["--greeting", "Hi", "--target", "Python"])
        assert result == 0
        captured = capsys.readouterr()
        assert captured.out == "Hi, Python!\n"
    
    def test_cli_quiet_mode(self, capsys):
        """Test CLI quiet mode."""
        result = cli_main(["--quiet"])
        assert result == 0
        captured = capsys.readouterr()
        assert captured.out == ""
    
    def test_cli_benchmark_mode(self, capsys):
        """Test CLI benchmark mode."""
        result = cli_main(["--benchmark", "10"])
        assert result == 0
        captured = capsys.readouterr()
        assert "Running benchmark with 10 iterations" in captured.out
        assert "Average execution time:" in captured.out
    
    def test_cli_benchmark_quiet_mode(self, capsys):
        """Test CLI benchmark with quiet mode."""
        result = cli_main(["--benchmark", "10", "--quiet"])
        assert result == 0
        captured = capsys.readouterr()
        assert captured.out == ""
    
    def test_cli_benchmark_invalid_iterations(self, capsys):
        """Test CLI benchmark with invalid iterations."""
        result = cli_main(["--benchmark", "0"])
        assert result == 1
        captured = capsys.readouterr()
        assert "benchmark iterations must be positive" in captured.err
    
    def test_cli_keyboard_interrupt(self, capsys):
        """Test CLI handles KeyboardInterrupt."""
        with patch('src.hello_world.cli.print_hello_world') as mock_print:
            mock_print.side_effect = KeyboardInterrupt()
            result = cli_main([])
            assert result == 1
            captured = capsys.readouterr()
            assert "Operation cancelled by user" in captured.err
    
    def test_cli_hello_world_error(self, capsys):
        """Test CLI handles HelloWorldError."""
        with patch('src.hello_world.cli.print_hello_world') as mock_print:
            mock_print.side_effect = HelloWorldError("Test error")
            result = cli_main([])
            assert result == 1
            captured = capsys.readouterr()
            assert "Hello World Error: Test error" in captured.err
    
    def test_cli_unexpected_error(self, capsys):
        """Test CLI handles unexpected errors."""
        with patch('src.hello_world.cli.print_hello_world') as mock_print:
            mock_print.side_effect = RuntimeError("Unexpected error")
            result = cli_main([])
            assert result == 1
            captured = capsys.readouterr()
            assert "Unexpected error: Unexpected error" in captured.err
    
    def test_run_benchmark_success(self, capsys):
        """Test run_benchmark function success."""
        result = run_benchmark(10)
        assert result == 0
        captured = capsys.readouterr()
        assert "Running benchmark with 10 iterations" in captured.out
        assert "Performance requirement satisfied" in captured.out
    
    def test_run_benchmark_quiet(self, capsys):
        """Test run_benchmark function with quiet mode."""
        result = run_benchmark(10, quiet=True)
        assert result == 0
        captured = capsys.readouterr()
        assert captured.out == ""
    
    @patch('src.hello_world.cli.benchmark_hello_world')
    def test_run_benchmark_error(self, mock_benchmark, capsys):
        """Test run_benchmark handles errors."""
        mock_benchmark.side_effect = RuntimeError("Benchmark error")
        result = run_benchmark(10)
        assert result == 1
        captured = capsys.readouterr()
        assert "Benchmark failed: Benchmark error" in captured.err


class TestIntegration:
    """Integration tests for the entire module."""
    
    def test_module_import(self):
        """Test that module can be imported correctly."""
        from src.hello_world import hello_world, print_hello_world, HelloWorldError
        assert callable(hello_world)
        assert callable(print_hello_world)
        assert issubclass(HelloWorldError, Exception)
    
    def test_cli_as_module(self):
        """Test running CLI as module."""
        import subprocess
        import sys
        
        # Test basic execution
        result = subprocess.run([
            sys.executable, "-c",
            "from src.hello_world.cli import main; import sys; sys.exit(main())"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert "Hello, World!" in result.stdout
    
    def test_performance_requirement(self):
        """Test that performance requirement is met."""
        # Measure time for 1000 iterations
        start_time = time.perf_counter()
        for _ in range(1000):
            hello_world()
        end_time = time.perf_counter()
        
        total_time = end_time - start_time
        assert total_time < 1.0, f"Performance requirement not met: {total_time:.3f}s > 1.0s"
    
    def test_memory_efficiency(self):
        """Test memory efficiency of the implementation."""
        import gc
        import sys
        
        # Force garbage collection
        gc.collect()
        
        # Get initial memory usage
        initial_objects = len(gc.get_objects())
        
        # Run many iterations
        for _ in range(1000):
            result = hello_world()
            del result
        
        # Force garbage collection again
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Memory should not grow significantly
        object_growth = final_objects - initial_objects
        assert object_growth < 100, f"Memory leak detected: {object_growth} new objects"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_unicode_characters(self):
        """Test handling of unicode characters."""
        result = hello_world("🌍 Hello", "世界")
        assert result == "🌍 Hello, 世界!"
    
    def test_very_long_strings(self):
        """Test handling of very long strings."""
        long_greeting = "Hello" * 1000
        long_target = "World" * 1000
        result = hello_world(long_greeting, long_target)
        assert result == f"{long_greeting}, {long_target}!"
    
    def test_special_characters(self):
        """Test handling of special characters."""
        result = hello_world("Hello@#$%", "W0rld!")
        assert result == "Hello@#$%, W0rld!!"
    
    def test_newlines_and_tabs(self):
        """Test handling of newlines and tabs."""
        result = hello_world("Hello\n", "\tWorld")
        assert result == "Hello, World!"


if __name__ == "__main__":
    """Run tests when executed directly."""
    pytest.main([__file__, "-v", "--cov=src.hello_world", "--cov-report=term-missing"])