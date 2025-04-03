import logging
from typing import Dict

import PyPDF2

from .base_processor import BaseProcessor

logger = logging.getLogger(__name__)


class PDFProcessor(BaseProcessor):
    """Processor for PDF files."""

    def extract_text(self) -> str:
        """Extract text from PDF file.

        Returns:
            str: Extracted text content
        """
        try:
            with open(self.file_path, "rb") as file:
                # Create PDF reader object
                reader = PyPDF2.PdfReader(file)

                # Extract text from all pages
                text = []
                total_pages = len(reader.pages)

                logger.info(f"Extracting text from PDF with {total_pages} pages")

                for page_num in range(total_pages):
                    page = reader.pages[page_num]
                    text.append(page.extract_text())

                # Store page count in metadata
                self.metadata["page_count"] = total_pages

                return "\n\n".join(text)

        except Exception as e:
            logger.error(f"Error extracting text from PDF {self.file_path}: {str(e)}")
            raise

    def extract_metadata(self) -> Dict:
        """Extract metadata from PDF file.

        Returns:
            Dict: Extracted metadata
        """
        try:
            with open(self.file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                metadata = {}

                # Extract document info if available
                if reader.metadata:
                    metadata.update(
                        {
                            "title": reader.metadata.get("/Title", ""),
                            "author": reader.metadata.get("/Author", ""),
                            "subject": reader.metadata.get("/Subject", ""),
                            "creator": reader.metadata.get("/Creator", ""),
                            "producer": reader.metadata.get("/Producer", ""),
                            "creation_date": reader.metadata.get("/CreationDate", ""),
                            "modification_date": reader.metadata.get("/ModDate", ""),
                        }
                    )

                # Clean up metadata by removing empty values
                return {k: v for k, v in metadata.items() if v}
        except Exception as e:
            logger.error(
                f"Error extracting metadata from PDF {self.file_path}: {str(e)}"
            )
            raise
