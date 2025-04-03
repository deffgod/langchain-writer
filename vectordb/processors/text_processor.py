import logging
from typing import Dict

from .base_processor import BaseProcessor

logger = logging.getLogger(__name__)


class TextProcessor(BaseProcessor):
    """Processor for text files."""

    def extract_text(self) -> str:
        """Extract text from text file.

        Returns:
            str: Extracted text content
        """
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                return file.read()

        except UnicodeDecodeError:
            # Try different encodings if UTF-8 fails
            encodings = ["latin-1", "cp1251", "iso-8859-1"]
            for encoding in encodings:
                try:
                    with open(self.file_path, "r", encoding=encoding) as file:
                        logger.info(f"Successfully read file with {encoding} encoding")
                        return file.read()
                except UnicodeDecodeError:
                    continue

            logger.error(
                f"Failed to read file {self.file_path} with any known encoding"
            )
            raise

        except Exception as e:
            logger.error(f"Error reading text file {self.file_path}: {str(e)}")
            raise

    def extract_metadata(self) -> Dict:
        """Extract metadata from text file.

        Returns:
            Dict: Extracted metadata
        """
        try:
            # Read first few lines to analyze content
            with open(self.file_path, "r", encoding="utf-8") as file:
                first_lines = [next(file) for _ in range(10) if next(file, None)]

            metadata = {
                "line_count": sum(
                    1 for _ in open(self.file_path, "r", encoding="utf-8")
                ),
                "has_header": self._detect_header(first_lines),
                "average_line_length": self._get_average_line_length(first_lines),
                "detected_format": self._detect_format(first_lines),
            }

            return metadata

        except Exception as e:
            logger.error(
                f"Error extracting metadata from text file {self.file_path}: {str(e)}"
            )
            raise

    def _detect_header(self, first_lines: list[str]) -> bool:
        """Detect if the file has a header.

        Args:
            first_lines: First few lines of the file

        Returns:
            bool: True if header detected
        """
        if not first_lines:
            return False

        # Check if first line looks like a header
        first_line = first_lines[0].strip()

        # Common header indicators
        header_indicators = [
            first_line.startswith("#"),
            first_line.isupper()
            and not any(line.isupper() for line in first_lines[1:]),
            first_line.endswith(":"),
            "title" in first_line.lower() or "header" in first_line.lower(),
        ]

        return any(header_indicators)

    def _get_average_line_length(self, lines: list[str]) -> float:
        """Calculate average line length.

        Args:
            lines: List of lines to analyze

        Returns:
            float: Average line length
        """
        if not lines:
            return 0.0

        total_length = sum(len(line.strip()) for line in lines)
        return round(total_length / len(lines), 2)

    def _detect_format(self, lines: list[str]) -> str:
        """Try to detect the text format.

        Args:
            lines: First few lines to analyze

        Returns:
            str: Detected format
        """
        if not lines:
            return "unknown"

        # Check for Markdown
        markdown_indicators = ["#", "##", "-", "*", "```", "===", "---"]
        if any(line.strip().startswith(tuple(markdown_indicators)) for line in lines):
            return "markdown"

        # Check for CSV
        if all("," in line for line in lines[:3]):
            return "csv"

        # Check for code
        code_indicators = [
            "def ",
            "class ",
            "function",
            "import ",
            "from ",
            "var ",
            "const ",
            "let ",
            "public ",
            "private ",
            "#include",
        ]
        if any(any(ind in line for ind in code_indicators) for line in lines):
            return "code"

        return "plain_text"
