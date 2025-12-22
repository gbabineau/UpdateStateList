""" Test parse_common_arguments """
import argparse
from unittest.mock import patch, mock_open
import pytest
from update_state_list.parse_common_arguments import parse_common_arguments


@pytest.fixture
def mock_pyproject():
    """Fixture to mock pyproject.toml file."""
    toml_content = b"""[tool.poetry]
version = "1.2.3"
"""
    return toml_content


def test_parse_common_arguments_returns_parser():
    """Test that function returns an ArgumentParser instance."""
    with patch(
        "builtins.open",
        mock_open(read_data=b'[tool.poetry]\nversion = "1.0.0"\n'),
    ):
        parser = parse_common_arguments("test_prog", "Test description")
        assert isinstance(parser, argparse.ArgumentParser)


def test_parse_common_arguments_prog_name():
    """Test that the parser has the correct program name."""
    with patch(
        "builtins.open",
        mock_open(read_data=b'[tool.poetry]\nversion = "1.0.0"\n'),
    ):
        parser = parse_common_arguments("my_script", "Test description")
        assert parser.prog == "my_script"


def test_parse_common_arguments_description():
    """Test that the parser has the correct description."""
    with patch(
        "builtins.open",
        mock_open(read_data=b'[tool.poetry]\nversion = "1.0.0"\n'),
    ):
        parser = parse_common_arguments("test_prog", "My test description")
        assert parser.description == "My test description"


def test_parse_common_arguments_has_version_action():
    """Test that parser has --version argument."""
    with patch(
        "builtins.open",
        mock_open(read_data=b'[tool.poetry]\nversion = "2.0.0"\n'),
    ):
        parser = parse_common_arguments("test_prog", "Test")
        assert any(action.dest == "version" for action in parser._actions)


def test_parse_common_arguments_has_verbose_action():
    """Test that parser has --verbose argument."""
    with patch(
        "builtins.open",
        mock_open(read_data=b'[tool.poetry]\nversion = "1.0.0"\n'),
    ):
        parser = parse_common_arguments("test_prog", "Test")
        assert any(action.dest == "verbose" for action in parser._actions)


def test_parse_common_arguments_default_version():
    """Test default version when pyproject.toml is missing data."""
    with patch("builtins.open", mock_open(read_data=b"[build]\n")):
        parser = parse_common_arguments("test_prog", "Test")
        version_action = next(a for a in parser._actions if a.dest == "version")
        assert "0.0.0" in version_action.version


def test_parse_common_arguments_reads_version():
    """Test that version is correctly read from pyproject.toml."""
    with patch(
        "builtins.open",
        mock_open(read_data=b'[tool.poetry]\nversion = "3.2.1"\n'),
    ):
        parser = parse_common_arguments("test_prog", "Test")
        version_action = next(a for a in parser._actions if a.dest == "version")
        assert "3.2.1" in version_action.version
