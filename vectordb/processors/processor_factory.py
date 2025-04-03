import logging
from pathlib import Path
from typing import Type

from .base_processor import BaseProcessor
from .html_processor import HTMLProcessor
from .json_processor import JSONProcessor
from .pdf_processor import PDFProcessor
from .text_processor import TextProcessor

logger = logging.getLogger(__name__)


class ProcessorFactory:
    """Factory class for creating appropriate file processors."""

    _processors = {
        ".txt": TextProcessor,
        ".md": TextProcessor,
        ".pdf": PDFProcessor,
        ".json": JSONProcessor,
        ".html": HTMLProcessor,
        ".htm": HTMLProcessor,
    }

    @classmethod
    def get_processor(cls, file_path: str) -> BaseProcessor:
        """Get appropriate processor for the file type.

        Args:
            file_path: Path to the file

        Returns:
            BaseProcessor: Appropriate processor instance

        Raises:
            ValueError: If no processor found for file type
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()

        processor_class = cls._processors.get(extension)

        if not processor_class:
            supported = ", ".join(cls._processors.keys())
            logger.error(
                f"No processor found for {extension}. Supported types: {supported}"
            )
            raise ValueError(f"Unsupported file type: {extension}")

        logger.info(f"Using {processor_class.__name__} for {file_path}")
        return processor_class(str(file_path))

    @classmethod
    def register_processor(cls, extension: str, processor: Type[BaseProcessor]) -> None:
        """Register a new processor for a file extension.

        Args:
            extension: File extension (with dot)
            processor: Processor class to handle the extension
        """
        if not extension.startswith("."):
            extension = f".{extension}"

        extension = extension.lower()
        cls._processors[extension] = processor
        logger.info(f"Registered {processor.__name__} for {extension} files")

    @classmethod
    def supported_extensions(cls) -> list[str]:
        """Get list of supported file extensions.

        Returns:
            list[str]: List of supported extensions
        """
        return list(cls._processors.keys())
