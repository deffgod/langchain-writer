from pathlib import Path
from typing import Any, Dict

import pytest
from processors.html_processor import HTMLProcessor

# Test data
SAMPLE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="description" content="Test description">
    <meta name="keywords" content="test, html, processor">
    <title>Test Document</title>
    <style>
        .hidden { display: none; }
    </style>
    <script>
        console.log("This should not appear in text");
    </script>
</head>
<body>
    <h1>Main Heading</h1>
    <nav>
        <a href="#section1">Section 1</a>
        <a href="#section2">Section 2</a>
    </nav>

    <div id="section1">
        <h2>Section 1 Heading</h2>
        <p>This is a paragraph with some <strong>bold</strong> and <em>italic</em> text.</p>
        <img src="test.jpg" alt="Test image">
    </div>

    <div id="section2">
        <h2>Section 2 Heading</h2>
        <p>Another paragraph with a <a href="https://example.com">link</a>.</p>
        <ul>
            <li>List item 1</li>
            <li>List item 2</li>
        </ul>
    </div>

    <div class="hidden">
        This content is hidden with CSS.
    </div>
</body>
</html>"""


@pytest.fixture
def temp_html_file(tmp_path):
    """Create a temporary HTML file for testing."""
    file_path = tmp_path / "test.html"
    file_path.write_text(SAMPLE_HTML)
    return str(file_path)


@pytest.fixture
def processor(temp_html_file):
    """Create an HTMLProcessor instance."""
    return HTMLProcessor(temp_html_file)


def test_initialization(temp_html_file):
    """Test processor initialization."""
    processor = HTMLProcessor(temp_html_file)
    assert processor.file_path == temp_html_file
    assert Path(processor.file_path).exists()


def test_extract_text(processor):
    """Test text extraction from HTML."""
    text = processor.extract_text()

    # Check content presence
    assert "Main Heading" in text
    assert "Section 1 Heading" in text
    assert "This is a paragraph" in text
    assert "bold" in text
    assert "italic" in text
    assert "List item 1" in text

    # Check content exclusion
    assert "console.log" not in text
    assert "<script>" not in text
    assert "<style>" not in text
    assert ".hidden" not in text

    # Check formatting
    assert text.count("\n") >= 5  # Multiple lines
    assert isinstance(text, str)


def test_extract_text_with_tags(temp_html_file):
    """Test text extraction with specific HTML tags."""
    processor = HTMLProcessor(file_path=temp_html_file, tags=["h1", "h2"])
    text = processor.extract_text()

    # Should include specified tags
    assert "Main Heading" in text
    assert "Section 1 Heading" in text
    assert "Section 2 Heading" in text

    # Should not include other content
    assert "This is a paragraph" not in text
    assert "List item 1" not in text


def test_extract_metadata(processor):
    """Test metadata extraction from HTML."""
    metadata = processor.extract_metadata()

    # Check basic metadata
    assert isinstance(metadata, dict)
    assert "title" in metadata
    assert "charset" in metadata
    assert "meta_tags" in metadata

    # Check content
    assert metadata["title"] == "Test Document"
    assert metadata["charset"] == "UTF-8"
    assert len(metadata["meta_tags"]) >= 2

    # Check element counts
    assert metadata.get("links", 0) >= 3  # Nav links + example link
    assert metadata.get("images", 0) >= 1
    assert metadata.get("scripts", 0) >= 1
    assert metadata.get("styles", 0) >= 1


def test_invalid_file():
    """Test handling of non-existent file."""
    with pytest.raises(FileNotFoundError):
        HTMLProcessor("nonexistent.html")


def test_invalid_html(tmp_path):
    """Test handling of invalid HTML content."""
    invalid_file = tmp_path / "invalid.html"
    invalid_file.write_text("<unclosed>tag")

    processor = HTMLProcessor(str(invalid_file))
    text = processor.extract_text()
    metadata = processor.extract_metadata()

    # BeautifulSoup should handle invalid HTML gracefully
    assert isinstance(text, str)
    assert isinstance(metadata, dict)


def test_empty_file(tmp_path):
    """Test handling of empty file."""
    empty_file = tmp_path / "empty.html"
    empty_file.write_text("")

    processor = HTMLProcessor(str(empty_file))
    text = processor.extract_text()
    metadata = processor.extract_metadata()

    assert text == ""
    assert isinstance(metadata, dict)
    assert metadata.get("title") == ""


def test_minimal_html(tmp_path):
    """Test handling of minimal HTML."""
    minimal_html = "<p>Test content</p>"
    html_file = tmp_path / "minimal.html"
    html_file.write_text(minimal_html)

    processor = HTMLProcessor(str(html_file))
    text = processor.extract_text()
    metadata = processor.extract_metadata()

    assert "Test content" in text
    assert isinstance(metadata, dict)


def test_large_html(tmp_path):
    """Test handling of large HTML files."""
    large_content = "<div>" + ("<p>Test content</p>" * 1000) + "</div>"
    html_file = tmp_path / "large.html"
    html_file.write_text(large_content)

    processor = HTMLProcessor(str(html_file))
    text = processor.extract_text()
    metadata = processor.extract_metadata()

    assert len(text) > 5000
    assert "Test content" in text
    assert isinstance(metadata, dict)


def test_nested_structure(tmp_path):
    """Test handling of deeply nested HTML structure."""
    nested_html = """
    <div>
        <div>
            <div>
                <div>
                    <p>Deeply nested content</p>
                </div>
            </div>
        </div>
    </div>
    """
    html_file = tmp_path / "nested.html"
    html_file.write_text(nested_html)

    processor = HTMLProcessor(str(html_file))
    text = processor.extract_text()

    assert "Deeply nested content" in text
