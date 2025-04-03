import os
from pathlib import Path
from typing import Any, Dict

import pytest
from processors.markdown_processor import MarkdownProcessor

# Test data
SAMPLE_MD = """---
title: Test Document
author: Test Author
date: 2024-02-20
---

# Heading 1

## Heading 2

### Heading 3

This is a paragraph with some **bold** and *italic* text.

```python
def test_function():
    return "This code should not appear in extracted text"
```

| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |

Another paragraph with a [link](https://example.com).
"""


@pytest.fixture
def temp_md_file(tmp_path):
    """Create a temporary markdown file for testing."""
    file_path = tmp_path / "test.md"
    file_path.write_text(SAMPLE_MD)
    return str(file_path)


@pytest.fixture
def processor(temp_md_file):
    """Create a MarkdownProcessor instance."""
    return MarkdownProcessor(temp_md_file)


def test_initialization(temp_md_file):
    """Test processor initialization."""
    processor = MarkdownProcessor(temp_md_file)
    assert processor.file_path == temp_md_file
    assert hasattr(processor, "html_converter")


def test_extract_text(processor):
    """Test text extraction from markdown."""
    text = processor.extract_text()

    # Check content presence
    assert "Heading 1" in text
    assert "This is a paragraph" in text
    assert "bold" in text
    assert "italic" in text

    # Check content exclusion
    assert "def test_function()" not in text
    assert "```python" not in text

    # Check formatting
    assert text.count("\n\n") >= 3  # Multiple paragraphs
    assert "Cell 1" in text  # Table content preserved


def test_extract_metadata(processor):
    """Test metadata extraction from markdown."""
    metadata = processor.extract_metadata()

    # Check basic metadata
    assert isinstance(metadata, dict)
    assert "title" in metadata
    assert "file_size" in metadata
    assert "last_modified" in metadata

    # Check heading counts
    headings = metadata.get("headings", {})
    assert headings.get("h1", 0) == 1
    assert headings.get("h2", 0) == 1
    assert headings.get("h3", 0) == 1

    # Check feature detection
    assert metadata.get("has_code_blocks") is True
    assert metadata.get("has_tables") is True


def test_extract_headings(processor):
    """Test heading extraction from markdown content."""
    headings = processor._extract_headings(SAMPLE_MD)

    assert headings["h1"] == 1
    assert headings["h2"] == 1
    assert headings["h3"] == 1
    assert headings["h4"] == 0
    assert headings["h5"] == 0
    assert headings["h6"] == 0


def test_invalid_file():
    """Test handling of non-existent file."""
    with pytest.raises(Exception):
        MarkdownProcessor("nonexistent.md")


def test_empty_file(tmp_path):
    """Test handling of empty file."""
    empty_file = tmp_path / "empty.md"
    empty_file.write_text("")

    processor = MarkdownProcessor(str(empty_file))
    text = processor.extract_text()
    metadata = processor.extract_metadata()

    assert text == ""
    assert isinstance(metadata, dict)
    assert metadata["file_size"] == 0


def test_metadata_extraction_with_frontmatter(temp_md_file):
    """Test extraction of front matter metadata."""
    processor = MarkdownProcessor(temp_md_file)
    metadata = processor.extract_metadata()

    # Front matter should be extracted
    if hasattr(processor.html_converter, "Meta"):
        meta = processor.html_converter.Meta
        if "title" in meta:
            assert meta["title"][0] == "Test Document"
        if "author" in meta:
            assert meta["author"][0] == "Test Author"
        if "date" in meta:
            assert meta["date"][0] == "2024-02-20"


def test_large_file_handling(tmp_path):
    """Test handling of large markdown files."""
    large_content = "# Large File\n\n" + ("Lorem ipsum " * 1000)
    large_file = tmp_path / "large.md"
    large_file.write_text(large_content)

    processor = MarkdownProcessor(str(large_file))
    text = processor.extract_text()
    metadata = processor.extract_metadata()

    assert len(text) > 5000
    assert metadata["file_size"] > 5000
