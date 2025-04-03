from pathlib import Path
from typing import Any, Dict

import pytest
from processors.base_processor import BaseProcessor


class TestProcessor(BaseProcessor):
    """Test implementation of BaseProcessor."""

    def extract_text(self) -> str:
        return "Test text"

    def extract_metadata(self) -> Dict[str, Any]:
        return {"test_key": "test_value"}


@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary file for testing."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("Test content")
    return str(file_path)


@pytest.fixture
def processor(temp_file):
    """Create a TestProcessor instance."""
    return TestProcessor(temp_file)


def test_initialization(temp_file):
    """Test processor initialization."""
    processor = TestProcessor(temp_file)
    assert processor.file_path == temp_file
    assert Path(processor.file_path).exists()


def test_initialization_with_nonexistent_file():
    """Test initialization with non-existent file."""
    with pytest.raises(FileNotFoundError):
        TestProcessor("nonexistent.txt")


def test_clean_text():
    """Test text cleaning functionality."""
    processor = TestProcessor("dummy.txt")  # File doesn't need to exist for this test

    # Test whitespace cleaning
    assert processor.clean_text("  test  ") == "test"
    assert processor.clean_text("\n\ntest\n\n") == "test"
    assert processor.clean_text("multiple  spaces") == "multiple spaces"

    # Test multiple newlines
    assert processor.clean_text("line1\n\n\n\nline2") == "line1\n\nline2"

    # Test empty input
    assert processor.clean_text("") == ""
    assert processor.clean_text("   ") == ""
    assert processor.clean_text("\n\n") == ""


def test_metadata_basics(processor, temp_file):
    """Test basic metadata functionality."""
    metadata = processor.extract_metadata()

    assert isinstance(metadata, dict)
    assert "test_key" in metadata
    assert metadata["test_key"] == "test_value"


def test_file_stats(processor, temp_file):
    """Test file statistics in metadata."""
    file_path = Path(temp_file)
    file_stats = {
        "size": file_path.stat().st_size,
        "modified": file_path.stat().st_mtime,
        "created": file_path.stat().st_ctime,
    }

    assert file_stats["size"] > 0
    assert file_stats["modified"] > 0
    assert file_stats["created"] > 0


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Simple text", "Simple text"),
        ("  Padded  text  ", "Padded text"),
        ("Line1\n\n\nLine2", "Line1\n\nLine2"),
        ("\t\tTabbed\t\ttext\t\t", "Tabbed text"),
        ("", ""),
        ("   ", ""),
        ("\n\n\n", ""),
    ],
)
def test_clean_text_variations(text, expected):
    """Test text cleaning with various input patterns."""
    processor = TestProcessor("dummy.txt")
    assert processor.clean_text(text) == expected


def test_process_empty_file(tmp_path):
    """Test processing an empty file."""
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("")

    processor = TestProcessor(str(empty_file))
    text = processor.extract_text()
    metadata = processor.extract_metadata()

    assert text == "Test text"  # From our test implementation
    assert isinstance(metadata, dict)
    assert "test_key" in metadata


def test_process_large_file(tmp_path):
    """Test processing a large file."""
    large_file = tmp_path / "large.txt"
    large_content = "x" * 1_000_000  # 1MB of content
    large_file.write_text(large_content)

    processor = TestProcessor(str(large_file))
    text = processor.extract_text()
    metadata = processor.extract_metadata()

    assert text == "Test text"  # From our test implementation
    assert isinstance(metadata, dict)
    assert "test_key" in metadata
