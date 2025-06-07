"""Comprehensive tests for Hello World module.

This test suite provides 100% code coverage for the hello_world module,
testing all functions, error conditions, and performance requirements.
"""

import io
import sys
import time
import unittest.mock
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch

import pytest

from src.hello_world.core import (
    hello_world,
    print_hello_world,
    timed_hello_world,
    main
)
from src.hello_world.cli import create_parser, cli_main


class TestHelloWorldCore:
    """Test cases for core Hello World functionality."""
    
    def test_hello_world_returns_correct_string(self):
        """Test that hello_world returns the expected string."""
        result = hello_world()
        assert result == "Hello, World!"
        assert isinstance(result, str)
    
    def test_hello_world_is_deterministic(self):
        """Test that hello_world returns the same result consistently."""
        results = [hello_world() for _ in range(10)]
        assert all(result == "Hello, World!" for result in results)
    
    def test_print_hello_world_output(self):
        """Test that print_hello_world outputs the correct message."""
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            print_hello_world()
        
        output = captured_output.getvalue()
        assert output.strip() == "Hello, World!"
    
    def test_print_hello_world_no_return_value(self):
        """Test that print_hello_world returns None."""
        with redirect_stdout(io.StringIO()):
            result = print_hello_world()
        assert result is None
    
    @patch('sys.stdout.write')
    def test_print_hello_world_output_error_handling(self, mock_write):
        """Test error handling when stdout write fails."""
        # Mock stdout.write to raise an OSError
        mock_write.side_effect = OSError("Mock stdout error")
        
        with patch('sys.stderr.write') as mock_stderr, \
             patch('sys.exit') as mock_exit:
            
            print_hello_world()
            
            # Verify error was written to stderr
            mock_stderr.assert_called_once()
            stderr_call = mock_stderr.call_args[0][0]
            assert "Error writing to stdout" in stderr_call
            
            # Verify sys.exit was called with code 1
            mock_exit.assert_called_once_with(1)
    
    def test_timed_hello_world_returns_tuple(self):
        """Test that timed_hello_world returns a tuple with message and time."""
        result = timed_hello_world()
        assert isinstance(result, tuple)
        assert len(result) == 2
        
        message, duration = result
        assert message == "Hello, World!"
        assert isinstance(duration, float)
        assert duration >= 0
    
    def test_timed_hello_world_performance(self):
        """Test that timed_hello_world completes within 1 second."""
        message, duration = timed_hello_world()
        assert duration < 1.0, f"Execution took {duration}s, exceeding 1s limit"
    
    def test_timed_hello_world_precision(self):
        """Test that timing measurement is reasonably precise."""
        # Run multiple times to check consistency
        durations = []
        for _ in range(5):
            _, duration = timed_hello_world()
            durations.append(duration)
        
        # All durations should be very small and relatively consistent
        assert all(d < 0.1 for d in durations), "Execution times too long"
        
        # Standard deviation should be small (timing is consistent)
        import statistics
        if len(durations) > 1:
            std_dev = statistics.stdev(durations)
            assert std_dev < 0.01, "Timing measurements inconsistent"


class TestMainFunction:
    """Test cases for the main CLI function."""
    
    def test_main_success_exit(self):
        """Test that main exits with code 0 on success."""
        with patch('sys.exit') as mock_exit, \
             redirect_stdout(io.StringIO()):
            main()
            mock_exit.assert_called_once_with(0)
    
    def test_main_output(self):
        """Test that main produces correct output."""
        captured_output = io.StringIO()
        with redirect_stdout(captured_output), \
             patch('sys.exit'):
            main()
        
        output = captured_output.getvalue()
        assert "Hello, World!" in output
    
    def test_main_performance_warning(self):
        """Test warning when execution exceeds 1 second."""
        with patch('src.hello_world.core.timed_hello_world') as mock_timed, \
             patch('sys.stderr.write') as mock_stderr, \
             patch('sys.exit'), \
             redirect_stdout(io.StringIO()):
            
            # Mock a slow execution
            mock_timed.return_value = ("Hello, World!", 1.5)
            
            main()
            
            # Check that warning was written to stderr
            mock_stderr.assert_called()
            stderr_calls = [call[0][0] for call in mock_stderr.call_args_list]
            warning_found = any("Warning: Execution took" in call for call in stderr_calls)
            assert warning_found, "Performance warning not found"
    
    def test_main_keyboard_interrupt(self):
        """Test main handles KeyboardInterrupt gracefully."""
        with patch('src.hello_world.core.timed_hello_world') as mock_timed, \
             patch('sys.stderr.write') as mock_stderr, \
             patch('sys.exit') as mock_exit:
            
            mock_timed.side_effect = KeyboardInterrupt()
            
            main()
            
            # Check that interruption message was written
            mock_stderr.assert_called()
            stderr_call = mock_stderr.call_args[0][0]
            assert "Interrupted by user" in stderr_call
            
            # Check exit code for keyboard interrupt
            mock_exit.assert_called_once_with(130)
    
    def test_main_unexpected_error(self):
        """Test main handles unexpected errors gracefully."""
        with patch('src.hello_world.core.timed_hello_world') as mock_timed, \
             patch('sys.stderr.write') as mock_stderr, \
             patch('sys.exit') as mock_exit:
            
            mock_timed.side_effect = RuntimeError("Unexpected error")
            
            main()
            
            # Check error message
            mock_stderr.assert_called()
            stderr_call = mock_stderr.call_args[0][0]
            assert "Unexpected error" in stderr_call
            
            # Check exit code for general error
            mock_exit.assert_called_once_with(1)


class TestCLI:
    """Test cases for CLI functionality."""
    
    def test_create_parser(self):
        """Test that create_parser returns a configured ArgumentParser."""
        parser = create_parser()
        assert parser.prog == "hello_world"
        assert "Hello, World!" in parser.description
    
    def test_parser_quiet_argument(self):
        """Test that parser handles --quiet argument."""
        parser = create_parser()
        args = parser.parse_args(["--quiet"])
        assert args.quiet is True
        
        args = parser.parse_args([])
        assert args.quiet is False
    
    def test_parser_time_argument(self):
        """Test that parser handles --time argument."""
        parser = create_parser()
        args = parser.parse_args(["--time"])
        assert args.time is True
        
        args = parser.parse_args([])
        assert args.time is False
    
    def test_parser_short_arguments(self):
        """Test that parser handles short argument forms."""
        parser = create_parser()
        
        args = parser.parse_args(["-q"])
        assert args.quiet is True
        
        args = parser.parse_args(["-t"])
        assert args.time is True
    
    def test_cli_main_default_behavior(self):
        """Test default CLI behavior (no arguments)."""
        with patch('sys.argv', ['hello_world']), \
             patch('sys.exit') as mock_exit, \
             redirect_stdout(io.StringIO()) as captured:
            
            cli_main()
            
            output = captured.getvalue()
            assert "Hello, World!" in output
            mock_exit.assert_called_once_with(0)
    
    def test_cli_main_quiet_mode(self):
        """Test CLI quiet mode."""
        with patch('sys.argv', ['hello_world', '--quiet']), \
             patch('sys.exit') as mock_exit, \
             redirect_stdout(io.StringIO()) as captured:
            
            cli_main()
            
            # In quiet mode, nothing should be printed to stdout
            output = captured.getvalue()
            assert output == ""
            mock_exit.assert_called_once_with(0)
    
    def test_cli_main_time_mode(self):
        """Test CLI time measurement mode."""
        with patch('sys.argv', ['hello_world', '--time']), \
             patch('sys.exit') as mock_exit, \
             redirect_stdout(io.StringIO()) as captured_out, \
             redirect_stderr(io.StringIO()) as captured_err:
            
            cli_main()
            
            stdout_output = captured_out.getvalue()
            stderr_output = captured_err.getvalue()
            
            assert "Hello, World!" in stdout_output
            assert "Execution time:" in stderr_output
            assert "seconds" in stderr_output
            mock_exit.assert_called_once_with(0)
    
    def test_cli_main_time_quiet_mode(self):
        """Test CLI with both time and quiet flags."""
        with patch('sys.argv', ['hello_world', '--time', '--quiet']), \
             patch('sys.exit') as mock_exit, \
             redirect_stdout(io.StringIO()) as captured_out, \
             redirect_stderr(io.StringIO()) as captured_err:
            
            cli_main()
            
            stdout_output = captured_out.getvalue()
            stderr_output = captured_err.getvalue()
            
            # Quiet mode: no Hello World output, but timing still to stderr
            assert "Hello, World!" not in stdout_output
            assert "Execution time:" in stderr_output
            mock_exit.assert_called_once_with(0)
    
    def test_cli_main_keyboard_interrupt(self):
        """Test CLI handles KeyboardInterrupt."""
        with patch('sys.argv', ['hello_world']), \
             patch('src.hello_world.cli.print_hello_world') as mock_print, \
             patch('sys.stderr.write') as mock_stderr, \
             patch('sys.exit') as mock_exit:
            
            mock_print.side_effect = KeyboardInterrupt()
            
            cli_main()
            
            mock_stderr.assert_called()
            stderr_call = mock_stderr.call_args[0][0]
            assert "Interrupted by user" in stderr_call
            mock_exit.assert_called_once_with(130)
    
    def test_cli_main_general_error(self):
        """Test CLI handles general exceptions."""
        with patch('sys.argv', ['hello_world']), \
             patch('src.hello_world.cli.print_hello_world') as mock_print, \
             patch('sys.stderr.write') as mock_stderr, \
             patch('sys.exit') as mock_exit:
            
            mock_print.side_effect = RuntimeError("Test error")
            
            cli_main()
            
            mock_stderr.assert_called()
            stderr_call = mock_stderr.call_args[0][0]
            assert "Error: Test error" in stderr_call
            mock_exit.assert_called_once_with(1)


class TestIntegration:
    """Integration tests for the complete Hello World system."""
    
    def test_module_import(self):
        """Test that module can be imported successfully."""
        from src.hello_world import hello_world, print_hello_world
        assert callable(hello_world)
        assert callable(print_hello_world)
    
    def test_module_version(self):
        """Test that module version is accessible."""
        from src.hello_world import __version__
        assert __version__ == "1.0.0"
    
    def test_module_all_exports(self):
        """Test that __all__ contains expected exports."""
        from src.hello_world import __all__
        expected = ["hello_world", "print_hello_world"]
        assert all(item in __all__ for item in expected)
    
    def test_end_to_end_execution(self):
        """Test complete end-to-end execution."""
        # Test importing and running the core functionality
        from src.hello_world.core import hello_world, timed_hello_world
        
        # Basic function call
        message = hello_world()
        assert message == "Hello, World!"
        
        # Timed execution
        timed_message, duration = timed_hello_world()
        assert timed_message == "Hello, World!"
        assert duration < 1.0
        
        # Verify performance constraint is met
        start_time = time.time()
        for _ in range(100):
            hello_world()
        end_time = time.time()
        total_duration = end_time - start_time
        assert total_duration < 1.0, f"100 calls took {total_duration}s"


if __name__ == "__main__":
    pytest.main([__file__])