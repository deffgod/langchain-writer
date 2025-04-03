import json
from pathlib import Path
from typing import Any, Dict

import pytest
from processors.json_processor import JSONProcessor

# Test data
SAMPLE_JSON = {
    "title": "Test Document",
    "description": "This is a test document",
    "metadata": {"author": "Test Author", "date": "2024-02-20"},
    "sections": [
        {"heading": "Section 1", "content": "This is the content of section 1"},
        {
            "heading": "Section 2",
            "content": "This is the content of section 2",
            "subsections": [
                {"heading": "Subsection 2.1", "content": "This is a subsection"}
            ],
        },
    ],
    "tags": ["test", "example", "json"],
}


@pytest.fixture
def temp_json_file(tmp_path):
    """Create a temporary JSON file for testing."""
    file_path = tmp_path / "test.json"
    file_path.write_text(json.dumps(SAMPLE_JSON, indent=2))
    return str(file_path)


@pytest.fixture
def processor(temp_json_file):
    """Create a JSONProcessor instance."""
    return JSONProcessor(temp_json_file)


def test_initialization(temp_json_file):
    """Test processor initialization."""
    processor = JSONProcessor(temp_json_file)
    assert processor.file_path == temp_json_file
    assert Path(processor.file_path).exists()


def test_extract_text(processor):
    """Test text extraction from JSON."""
    text = processor.extract_text()

    # Check content presence
    assert "Test Document" in text
    assert "This is a test document" in text
    assert "Section 1" in text
    assert "This is the content of section 1" in text
    assert "Subsection 2.1" in text

    # Check formatting
    assert text.count("\n") >= 5  # Multiple lines
    assert isinstance(text, str)


def test_extract_text_with_fields(temp_json_file):
    """Test text extraction with specific fields."""
    processor = JSONProcessor(
        file_path=temp_json_file, text_fields=["description", "content"]
    )
    text = processor.extract_text()

    # Should include specified fields
    assert "This is a test document" in text
    assert "This is the content of section 1" in text

    # Should not include other fields
    assert "Test Document" not in text
    assert "Test Author" not in text


def test_extract_metadata(processor):
    """Test metadata extraction from JSON."""
    metadata = processor.extract_metadata()

    # Check basic metadata
    assert isinstance(metadata, dict)
    assert "structure_depth" in metadata
    assert "total_fields" in metadata
    assert "keys" in metadata

    # Check content
    assert metadata["structure_depth"] >= 3  # Our sample has 3 levels
    assert metadata["total_fields"] >= 10
    assert "title" in metadata["keys"]
    assert "sections" in metadata["keys"]


def test_invalid_file():
    """Test handling of non-existent file."""
    with pytest.raises(FileNotFoundError):
        JSONProcessor("nonexistent.json")


def test_invalid_json(tmp_path):
    """Test handling of invalid JSON content."""
    invalid_file = tmp_path / "invalid.json"
    invalid_file.write_text("{invalid json")

    with pytest.raises(json.JSONDecodeError):
        processor = JSONProcessor(str(invalid_file))
        processor.extract_text()


def test_empty_file(tmp_path):
    """Test handling of empty file."""
    empty_file = tmp_path / "empty.json"
    empty_file.write_text("")

    with pytest.raises(json.JSONDecodeError):
        processor = JSONProcessor(str(empty_file))
        processor.extract_text()


def test_empty_json(tmp_path):
    """Test handling of empty JSON object."""
    empty_json = tmp_path / "empty.json"
    empty_json.write_text("{}")

    processor = JSONProcessor(str(empty_json))
    text = processor.extract_text()
    metadata = processor.extract_metadata()

    assert text == ""
    assert isinstance(metadata, dict)
    assert metadata["structure_depth"] == 1
    assert metadata["total_fields"] == 0


def test_nested_arrays(tmp_path):
    """Test handling of nested arrays."""
    nested_json = {"array": [[1, 2, 3], [4, 5, 6], {"nested": ["a", "b", "c"]}]}

    json_file = tmp_path / "nested.json"
    json_file.write_text(json.dumps(nested_json))

    processor = JSONProcessor(str(json_file))
    text = processor.extract_text()
    metadata = processor.extract_metadata()

    assert "1" in text
    assert "a" in text
    assert metadata["structure_depth"] >= 3


def test_large_json(tmp_path):
    """Test handling of large JSON files."""
    large_json = {"items": [{"id": i, "value": f"test{i}"} for i in range(1000)]}

    json_file = tmp_path / "large.json"
    json_file.write_text(json.dumps(large_json))

    processor = JSONProcessor(str(json_file))
    text = processor.extract_text()
    metadata = processor.extract_metadata()

    assert len(text) > 5000
    assert metadata["total_fields"] > 2000  # 1000 items * 2 fields each
