import json
import logging
from typing import Any, Dict

from .base_processor import BaseProcessor

logger = logging.getLogger(__name__)


class JSONProcessor(BaseProcessor):
    """Processor for JSON files."""

    def __init__(self, file_path: str, text_fields: list[str] = None):
        """Initialize JSON processor.

        Args:
            file_path: Path to JSON file
            text_fields: List of fields to extract as text (if None, all string fields will be extracted)
        """
        super().__init__(file_path)
        self.text_fields = text_fields
        self.data: Dict[str, Any] = {}

    def _load_json(self) -> None:
        """Load JSON data from file."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                self.data = json.load(file)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file {self.file_path}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error reading JSON file {self.file_path}: {str(e)}")
            raise

    def _extract_text_from_dict(
        self, data: Dict[str, Any], path: str = ""
    ) -> list[str]:
        """Recursively extract text from dictionary.

        Args:
            data: Dictionary to extract text from
            path: Current path in the JSON structure

        Returns:
            list[str]: List of extracted text strings
        """
        texts = []

        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key

            if isinstance(value, dict):
                texts.extend(self._extract_text_from_dict(value, current_path))
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        texts.extend(
                            self._extract_text_from_dict(item, f"{current_path}[{i}]")
                        )
                    elif isinstance(item, str) and (
                        not self.text_fields or key in self.text_fields
                    ):
                        texts.append(f"{current_path}[{i}]: {item}")
            elif isinstance(value, str) and (
                not self.text_fields or key in self.text_fields
            ):
                texts.append(f"{current_path}: {value}")

        return texts

    def extract_text(self) -> str:
        """Extract text content from JSON file.

        Returns:
            str: Extracted text content
        """
        if not self.data:
            self._load_json()

        try:
            # Extract text from JSON structure
            texts = self._extract_text_from_dict(self.data)

            # Join all extracted texts
            return "\n".join(texts)

        except Exception as e:
            logger.error(f"Error extracting text from JSON {self.file_path}: {str(e)}")
            raise

    def extract_metadata(self) -> Dict:
        """Extract metadata from JSON file.

        Returns:
            Dict: Extracted metadata
        """
        if not self.data:
            self._load_json()

        try:
            metadata = {
                "json_keys": list(self.data.keys()),
                "structure_depth": self._get_structure_depth(self.data),
                "total_fields": self._count_fields(self.data),
            }

            if isinstance(self.data, list):
                metadata["array_length"] = len(self.data)

            return metadata

        except Exception as e:
            logger.error(
                f"Error extracting metadata from JSON {self.file_path}: {str(e)}"
            )
            raise

    def _get_structure_depth(self, obj: Any, current_depth: int = 1) -> int:
        """Get the maximum depth of the JSON structure.

        Args:
            obj: Current object to analyze
            current_depth: Current depth in the structure

        Returns:
            int: Maximum depth
        """
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(
                self._get_structure_depth(value, current_depth + 1)
                for value in obj.values()
            )
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(
                self._get_structure_depth(item, current_depth + 1) for item in obj
            )
        return current_depth

    def _count_fields(self, obj: Any) -> int:
        """Count total number of fields in the JSON structure.

        Args:
            obj: Object to count fields in

        Returns:
            int: Total number of fields
        """
        count = 0
        if isinstance(obj, dict):
            count += len(obj)
            for value in obj.values():
                count += self._count_fields(value)
        elif isinstance(obj, list):
            for item in obj:
                count += self._count_fields(item)
        return count
