import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Union

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseProcessor(ABC):
    """Base class for all document processors."""

    def __init__(self, file_path: Union[str, Path]):
        """Initialize the processor with a file path.

        Args:
            file_path: Path to the file to process
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        self.content: Optional[str] = None
        self.metadata: Dict = {
            "source": str(self.file_path),
            "file_name": self.file_path.name,
            "file_type": self.file_path.suffix.lower()[1:],
            "file_size": self.file_path.stat().st_size,
        }

    @abstractmethod
    def extract_text(self) -> str:
        """Extract text content from the file.

        Returns:
            str: Extracted text content
        """
        pass

    @abstractmethod
    def extract_metadata(self) -> Dict:
        """Extract metadata from the file.

        Returns:
            Dict: Extracted metadata
        """
        pass

    def clean_text(self, text: str) -> str:
        """Clean the extracted text.

        Args:
            text: Text to clean

        Returns:
            str: Cleaned text
        """
        # Basic cleaning
        text = text.strip()
        # Remove multiple newlines
        text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
        return text

    def process(self) -> tuple[str, Dict]:
        """Process the file and return cleaned text and metadata.

        Returns:
            tuple[str, Dict]: Tuple of (cleaned_text, metadata)
        """
        try:
            logger.info(f"Processing file: {self.file_path}")

            # Extract text and metadata
            text = self.extract_text()
            additional_metadata = self.extract_metadata()

            # Clean text
            cleaned_text = self.clean_text(text)

            # Update metadata
            self.metadata.update(additional_metadata)
            self.metadata["text_length"] = len(cleaned_text)

            logger.info(f"Successfully processed file: {self.file_path}")
            return cleaned_text, self.metadata

        except Exception as e:
            logger.error(f"Error processing file {self.file_path}: {str(e)}")
            raise

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(file_path='{self.file_path}')"
