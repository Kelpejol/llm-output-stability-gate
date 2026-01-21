"""
Tests for CLI interface.
"""
import pytest
from click.testing import CliRunner
from uqlm_guard.cli.main import cli
import os


class TestCLI:
    """Tests for CLI commands."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_cli_version(self):
        """Test --version flag."""
        result = self.runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert '1.0.0' in result.output
    
    def test_cli_help(self):
        """Test --help flag."""
        result = self.runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'UQLM-Guard' in result.output
    
    def test_review_help(self):
        """Test review command help."""
        result = self.runner.invoke(cli, ['review', '--help'])
        assert result.exit_code == 0
        assert 'Review a prompt' in result.output
    
    def test_review_no_api_key(self):
        """Test review fails gracefully without API key."""
        # Temporarily remove API key if it exists
        original_key = os.environ.get('OPENAI_API_KEY')
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        result = self.runner.invoke(cli, ['review', 'test prompt'])
        
        # Restore API key
        if original_key:
            os.environ['OPENAI_API_KEY'] = original_key
        
        assert 'OPENAI_API_KEY not found' in result.output
    
    def test_review_invalid_samples(self):
        """Test review with invalid sample count."""
        result = self.runner.invoke(cli, ['review', 'test', '--samples', '1'])
        assert result.exit_code != 0 or 'must be between 2 and 10' in result.output
    
    @pytest.mark.requires_api_key
    def test_review_json_output(self):
        """Test JSON output format."""
        result = self.runner.invoke(cli, [
            'review',
            'What is 2+2?',
            '--samples', '2',
            '--json-output'
        ])
        
        # Should produce valid output
        assert result.exit_code == 0
        # Check if output looks like JSON
        assert '{' in result.output or 'confidence' in result.output.lower()
    
    def test_batch_help(self):
        """Test batch command help."""
        result = self.runner.invoke(cli, ['batch', '--help'])
        assert result.exit_code == 0
        assert 'multiple prompts' in result.output.lower()
    
    def test_batch_nonexistent_file(self):
        """Test batch with nonexistent file."""
        result = self.runner.invoke(cli, ['batch', 'nonexistent.txt'])
        assert result.exit_code != 0
    
    def test_compare_help(self):
        """Test compare command help."""
        result = self.runner.invoke(cli, ['compare', '--help'])
        assert result.exit_code == 0
        assert 'Compare' in result.output
    
    def test_examples_command(self):
        """Test examples command."""
        result = self.runner.invoke(cli, ['examples'])
        assert result.exit_code == 0
        assert 'Example Prompts' in result.output or 'JWT' in result.output


class TestCLIIntegration:
    """Integration tests for CLI (require API key)."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    @pytest.mark.requires_api_key
    @pytest.mark.slow
    def test_review_full_flow(self):
        """Test complete review flow."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, [
                'review',
                'Write a function to add two numbers',
                '--samples', '3',
                '--output', 'result.json'
            ])
            
            assert result.exit_code == 0
            
            # Check output file was created
            import os
            assert os.path.exists('result.json')
    
    @pytest.mark.requires_api_key
    @pytest.mark.slow
    def test_batch_from_file(self):
        """Test batch processing from file."""
        with self.runner.isolated_filesystem():
            # Create test file
            with open('test_prompts.txt', 'w') as f:
                f.write("What is 1+1?\n")
                f.write("What is 2+2?\n")
            
            result = self.runner.invoke(cli, [
                'batch',
                'test_prompts.txt',
                '--samples', '2'
            ])
            
            assert result.exit_code == 0
            assert '2 prompts' in result.output or 'Analyzing' in result.output