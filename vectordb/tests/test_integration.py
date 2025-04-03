import json
import os
from pathlib import Path
from typing import Any, Dict

import pytest
from db.db_manager import DBManager
from process_data import DataProcessor
from processors.html_processor import HTMLProcessor
from processors.json_processor import JSONProcessor
from processors.markdown_processor import MarkdownProcessor

# Test data for different file types
SAMPLE_MD = """# Test Document

This is a test markdown document.

## Section 1

Content for section 1.

## Section 2

Content for section 2."""

SAMPLE_JSON = {
    "title": "Test JSON",
    "content": "This is test JSON content",
    "sections": [
        {"name": "Section 1", "text": "JSON section 1 content"},
        {"name": "Section 2", "text": "JSON section 2 content"},
    ],
}

SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head><title>Test HTML</title></head>
<body>
    <h1>Test Document</h1>
    <p>This is test HTML content.</p>
    <div>
        <h2>Section 1</h2>
        <p>HTML section 1 content</p>
        <h2>Section 2</h2>
        <p>HTML section 2 content</p>
    </div>
</body>
</html>
"""


@pytest.fixture
def test_dir(tmp_path):
    """Create a test directory with sample files."""
    # Create directories
    data_dir = tmp_path / "data"
    db_dir = tmp_path / "db"
    data_dir.mkdir()
    db_dir.mkdir()

    # Create test files
    (data_dir / "test.md").write_text(SAMPLE_MD)
    (data_dir / "test.json").write_text(json.dumps(SAMPLE_JSON))
    (data_dir / "test.html").write_text(SAMPLE_HTML)

    return {"data_dir": str(data_dir), "db_dir": str(db_dir)}


@pytest.fixture
def db_manager(test_dir):
    """Create a DBManager instance."""
    return DBManager(persist_directory=test_dir["db_dir"])


@pytest.fixture
def data_processor(test_dir, db_manager):
    """Create a DataProcessor instance."""
    return DataProcessor(data_dir=test_dir["data_dir"], db_manager=db_manager)


@pytest.mark.integration
def test_full_pipeline(data_processor, test_dir):
    """Test the complete processing pipeline."""
    # Process all files
    data_processor.process_directory(collection_name="test_collection")

    # Query the database
    results = data_processor.db_manager.query(
        collection_name="test_collection", query_texts="test content", n_results=5
    )

    # Check results
    assert isinstance(results, dict)
    assert "documents" in results
    assert "metadatas" in results
    assert len(results["documents"][0]) > 0

    # Check if content from each file type is present
    all_text = " ".join(results["documents"][0])
    assert "test markdown document" in all_text.lower()
    assert "test json content" in all_text.lower()
    assert "test html content" in all_text.lower()


@pytest.mark.integration
def test_metadata_preservation(data_processor, test_dir):
    """Test that metadata is preserved through the pipeline."""
    # Process files
    data_processor.process_directory(collection_name="test_collection")

    # Query with metadata filter
    results = data_processor.db_manager.query(
        collection_name="test_collection", query_texts="section 1", n_results=5
    )

    # Check metadata
    assert "metadatas" in results
    for metadata in results["metadatas"][0]:
        assert "source_file" in metadata
        assert "file_type" in metadata
        assert metadata["file_type"] in [".md", ".json", ".html"]


@pytest.mark.integration
def test_incremental_updates(data_processor, test_dir):
    """Test adding new files incrementally."""
    # Initial processing
    data_processor.process_directory(collection_name="test_collection")

    # Add new file
    new_md = "# New Document\n\nThis is a new test document."
    new_file = Path(test_dir["data_dir"]) / "new.md"
    new_file.write_text(new_md)

    # Process again
    data_processor.process_directory(collection_name="test_collection")

    # Query for new content
    results = data_processor.db_manager.query(
        collection_name="test_collection", query_texts="new test document", n_results=1
    )

    assert "new test document" in results["documents"][0][0].lower()


@pytest.mark.integration
def test_error_handling(data_processor, test_dir):
    """Test error handling in the pipeline."""
    # Create invalid files
    invalid_files = {
        "invalid.json": "{invalid json",
        "invalid.html": "<unclosed>tag",
        "empty.md": "",
    }

    for name, content in invalid_files.items():
        (Path(test_dir["data_dir"]) / name).write_text(content)

    # Process should continue despite errors
    data_processor.process_directory(collection_name="test_collection")

    # Valid files should still be processed
    results = data_processor.db_manager.query(
        collection_name="test_collection", query_texts="test content", n_results=5
    )

    assert len(results["documents"][0]) > 0


@pytest.mark.integration
def test_large_scale_processing(data_processor, test_dir):
    """Test processing a large number of files."""
    # Create many small files
    for i in range(100):
        content = f"# Document {i}\n\nThis is test document {i}."
        file_path = Path(test_dir["data_dir"]) / f"doc_{i}.md"
        file_path.write_text(content)

    # Process all files
    data_processor.process_directory(collection_name="test_collection")

    # Verify processing
    results = data_processor.db_manager.query(
        collection_name="test_collection", query_texts="test document", n_results=100
    )

    assert len(results["documents"][0]) >= 100


@pytest.mark.integration
def test_query_relevance(data_processor, test_dir):
    """Test query result relevance."""
    # Process initial files
    data_processor.process_directory(collection_name="test_collection")

    # Test specific queries
    queries = [
        ("section 1", "section 1 content"),
        ("test document", "test document"),
        ("json content", "json content"),
    ]

    for query, expected in queries:
        results = data_processor.db_manager.query(
            collection_name="test_collection", query_texts=query, n_results=1
        )
        assert expected.lower() in results["documents"][0][0].lower()


@pytest.mark.integration
def test_collection_management(data_processor, test_dir):
    """Test collection management features."""
    # Create multiple collections
    collections = ["collection1", "collection2"]

    for collection in collections:
        data_processor.process_directory(collection_name=collection)

    # Verify collections
    available_collections = data_processor.db_manager.list_collections()

    for collection in collections:
        assert collection in available_collections
