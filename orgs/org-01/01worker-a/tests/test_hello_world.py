"""Comprehensive tests for the Hello World module.

This module provides 100% test coverage for the hello_world module,
including normal cases, edge cases, and error handling scenarios.
"""

import io
import sys
import pytest
from unittest.mock import patch, MagicMock

from src.hello_world.core import (
    hello_world,
    print_hello_world, 
    timed_hello_world,
    main
)
from src.hello_world.cli import create_parser, cli_main


class TestHelloWorldCore:
    """Test cases for core hello_world functionality."""
    
    def test_hello_world_returns_correct_string(self):
        """Test that hello_world returns the expected string."""
        result = hello_world()
        assert result == "Hello, World!"
        assert isinstance(result, str)
    
    def test_hello_world_consistent_output(self):
        """Test that hello_world returns consistent output across multiple calls."""
        results = [hello_world() for _ in range(10)]
        assert all(result == "Hello, World!" for result in results)
    
    def test_print_hello_world_default_output(self, capsys):
        """Test print_hello_world with default stdout."""
        print_hello_world()
        captured = capsys.readouterr()
        assert captured.out == "Hello, World!\n"
        assert captured.err == ""
    
    def test_print_hello_world_custom_stream(self):
        """Test print_hello_world with custom output stream."""
        output_stream = io.StringIO()
        print_hello_world(output_stream)
        output_stream.seek(0)
        assert output_stream.read() == "Hello, World!\n"
    
    def test_print_hello_world_io_error_handling(self):
        """Test print_hello_world handles I/O errors gracefully."""
        mock_stream = MagicMock()
        mock_stream.write.side_effect = OSError("Mock I/O error")
        
        with pytest.raises(RuntimeError) as exc_info:
            print_hello_world(mock_stream)
        
        assert "Failed to output Hello World" in str(exc_info.value)
        assert "Mock I/O error" in str(exc_info.value)
    
    def test_timed_hello_world_returns_tuple(self):
        """Test that timed_hello_world returns correct tuple format."""
        result, exec_time = timed_hello_world()
        
        assert isinstance(result, str)
        assert isinstance(exec_time, float)
        assert result == "Hello, World!"
        assert exec_time >= 0
    
    def test_timed_hello_world_performance_requirement(self):
        """Test that execution time is under 1 second."""
        result, exec_time = timed_hello_world()
        
        assert exec_time < 1.0, f"Execution time {exec_time}s exceeds 1s limit"
        assert result == "Hello, World!"
    
    def test_timed_hello_world_multiple_calls(self):
        """Test that timed_hello_world works correctly across multiple calls."""
        results = []
        times = []
        
        for _ in range(5):
            result, exec_time = timed_hello_world()
            results.append(result)
            times.append(exec_time)
        
        assert all(result == "Hello, World!" for result in results)
        assert all(time < 1.0 for time in times)
        assert all(time >= 0 for time in times)


class TestMainFunction:
    """Test cases for the main function."""
    
    def test_main_normal_execution(self, capsys):
        """Test main function normal execution."""
        main()
        captured = capsys.readouterr()
        
        assert "Hello, World!" in captured.out
        assert captured.err == ""
    
    @patch('src.hello_world.core.timed_hello_world')
    def test_main_performance_warning(self, mock_timed, capsys):
        """Test main function shows warning for slow execution."""
        mock_timed.return_value = ("Hello, World!", 1.5)
        
        main()
        captured = capsys.readouterr()
        
        assert "Hello, World!" in captured.out
        assert "Warning: Execution took 1.5000s (exceeds 1s limit)" in captured.err
    
    @patch('src.hello_world.core.timed_hello_world')
    def test_main_exception_handling(self, mock_timed, capsys):
        """Test main function handles exceptions gracefully."""
        mock_timed.side_effect = Exception("Test exception")
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error: Test exception" in captured.err


class TestCLI:
    """Test cases for the CLI functionality."""
    
    def test_create_parser(self):
        """Test that create_parser returns a properly configured parser."""
        parser = create_parser()
        
        assert parser.description
        assert "Hello World CLI" in parser.description
    
    def test_cli_main_default_behavior(self, capsys):
        """Test CLI main with default arguments."""
        exit_code = cli_main([])
        captured = capsys.readouterr()
        
        assert exit_code == 0
        assert "Hello, World!" in captured.out
    
    def test_cli_main_quiet_mode(self, capsys):
        """Test CLI main with quiet flag."""
        exit_code = cli_main(["--quiet"])
        captured = capsys.readouterr()
        
        assert exit_code == 0
        assert captured.out == ""
        assert captured.err == ""
    
    def test_cli_main_time_mode(self, capsys):
        """Test CLI main with time flag."""
        exit_code = cli_main(["--time"])
        captured = capsys.readouterr()
        
        assert exit_code == 0
        assert "Hello, World!" in captured.out
        assert "Execution time:" in captured.err
    
    def test_cli_main_quiet_and_time_mode(self, capsys):
        """Test CLI main with both quiet and time flags."""
        exit_code = cli_main(["--quiet", "--time"])
        captured = capsys.readouterr()
        
        assert exit_code == 0
        assert captured.out == ""
        assert "Execution time:" in captured.err
    
    def test_cli_main_version(self, capsys):
        """Test CLI main with version flag."""
        with pytest.raises(SystemExit) as exc_info:
            cli_main(["--version"])
        
        # argparse exits with code 0 for --version
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "Hello World CLI 1.0.0" in captured.out
    
    def test_cli_main_help(self, capsys):
        """Test CLI main with help flag."""
        with pytest.raises(SystemExit) as exc_info:
            cli_main(["--help"])
        
        # argparse exits with code 0 for --help
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "Hello World CLI" in captured.out
        assert "usage:" in captured.out
    
    @patch('src.hello_world.cli.timed_hello_world')
    def test_cli_main_exception_handling(self, mock_timed, capsys):
        """Test CLI main handles exceptions and returns error code."""
        mock_timed.side_effect = Exception("CLI test exception")
        
        exit_code = cli_main(["--time"])
        captured = capsys.readouterr()
        
        assert exit_code == 1
        assert "Error: CLI test exception" in captured.err


class TestModuleIntegration:
    """Integration tests for the complete module."""
    
    def test_module_imports(self):
        """Test that all expected functions can be imported."""
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
        
        expected_exports = ["hello_world", "print_hello_world"]
        assert all(export in __all__ for export in expected_exports)
    
    def test_direct_module_execution(self, capsys):
        """Test running the module directly via python -m."""
        import subprocess
        import sys
        
        # Run the module as a script
        result = subprocess.run(
            [sys.executable, "-c", "from src.hello_world.core import main; main()"],
            capture_output=True,
            text=True,
            cwd="/media/thithilab/volume/kaggle_agent/orgs/org-01/01worker-a"
        )
        
        assert result.returncode == 0
        assert "Hello, World!" in result.stdout


class TestErrorHandling:
    """Test cases for error handling scenarios."""
    
    def test_print_hello_world_with_none_stream(self, capsys):
        """Test print_hello_world with None stream defaults to stdout."""
        print_hello_world(None)
        captured = capsys.readouterr()
        
        assert captured.out == "Hello, World!\n"
    
    def test_robust_error_handling(self):
        """Test that functions are robust against various error conditions."""
        # Test that basic functions don't raise unexpected exceptions
        try:
            result = hello_world()
            assert result == "Hello, World!"
            
            result, time_taken = timed_hello_world()
            assert result == "Hello, World!"
            assert isinstance(time_taken, float)
            
        except Exception as e:
            pytest.fail(f"Unexpected exception raised: {e}")


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([__file__, "-v", "--cov=src.hello_world", "--cov-report=term-missing"])