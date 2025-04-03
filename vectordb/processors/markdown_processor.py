import logging
from pathlib import Path
from typing import Any, Dict, Optional

import markdown
from bs4 import BeautifulSoup

from .base_processor import BaseProcessor

logger = logging.getLogger(__name__)


class MarkdownProcessor(BaseProcessor):
    """Processor for Markdown files."""

    def __init__(self, file_path: str):
        """Initialize the markdown processor.

        Args:
            file_path (str): Path to the markdown file.
        """
        super().__init__(file_path)
        self.html_converter = markdown.Markdown(
            extensions=["meta", "tables", "fenced_code", "toc", "attr_list"]
        )

    def extract_text(self) -> str:
        """Extract text content from markdown file.

        Returns:
            str: Extracted text content.
        """
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                markdown_content = f.read()

            # Convert markdown to HTML
            html_content = self.html_converter.convert(markdown_content)

            # Parse HTML to extract clean text
            soup = BeautifulSoup(html_content, "html.parser")

            # Remove code blocks to avoid including code examples
            for code in soup.find_all("code"):
                code.decompose()

            # Extract text content
            text = soup.get_text(separator="\n\n")

            return self.clean_text(text)

        except Exception as e:
            logger.error(f"Error extracting text from markdown file: {str(e)}")
            raise

    def extract_metadata(self) -> Dict[str, Any]:
        """Extract metadata from markdown file.

        Returns:
            Dict[str, Any]: Extracted metadata.
        """
        try:
            metadata: Dict[str, Any] = {}

            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Reset the converter to clear any previous metadata
            self.html_converter.reset()

            # Convert markdown to extract metadata
            self.html_converter.convert(content)

            # Get metadata if available
            if hasattr(self.html_converter, "Meta"):
                for key, value in self.html_converter.Meta.items():
                    metadata[key] = value[0] if len(value) == 1 else value

            # Add basic file stats
            file_path = Path(self.file_path)
            metadata.update(
                {
                    "title": file_path.stem,
                    "file_size": file_path.stat().st_size,
                    "last_modified": file_path.stat().st_mtime,
                    "headings": self._extract_headings(content),
                    "has_code_blocks": "```" in content,
                    "has_tables": "|" in content and "-|-" in content,
                }
            )

            return metadata

        except Exception as e:
            logger.error(f"Error extracting metadata from markdown file: {str(e)}")
            raise

    def _extract_headings(self, content: str) -> Dict[str, int]:
        """Extract heading statistics from markdown content.

        Args:
            content (str): Markdown content.

        Returns:
            Dict[str, int]: Count of headings by level.
        """
        headings = {f"h{i}": 0 for i in range(1, 7)}

        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("#"):
                level = len(line) - len(line.lstrip("#"))
                if level < 7:  # Only count valid heading levels
                    headings[f"h{level}"] += 1

        return headings
