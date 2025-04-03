import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type

from chromadb.api.types import Metadata
from db.db_manager import DBManager
from processors.base_processor import BaseProcessor
from processors.html_processor import HTMLProcessor
from processors.json_processor import JSONProcessor
from processors.markdown_processor import MarkdownProcessor
from processors.pdf_processor import PDFProcessor
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DataProcessor:
    def __init__(self, data_dir: str, db_manager: DBManager):
        """Initialize the data processor.

        Args:
            data_dir (str): Directory containing the data files.
            db_manager (DBManager): Database manager instance.
        """
        self.data_dir = Path(data_dir)
        self.db_manager = db_manager
        self.processors: Dict[str, Type[BaseProcessor]] = {
            ".pdf": PDFProcessor,
            ".json": JSONProcessor,
            ".html": HTMLProcessor,
            ".md": MarkdownProcessor,
            ".markdown": MarkdownProcessor,
        }

    def get_processor(self, file_path: Path) -> Optional[BaseProcessor]:
        """Get the appropriate processor for a file.

        Args:
            file_path (Path): Path to the file.

        Returns:
            Optional[BaseProcessor]: Processor instance if supported, None otherwise.
        """
        suffix = file_path.suffix.lower()
        processor_class = self.processors.get(suffix)

        if processor_class:
            try:
                return processor_class(str(file_path))
            except Exception as e:
                logger.error(f"Error creating processor for {file_path}: {str(e)}")
                return None
        return None

    def process_file(
        self, file_path: Path
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """Process a single file.

        Args:
            file_path (Path): Path to the file.

        Returns:
            Tuple[Optional[str], Optional[Dict]]: Extracted text and metadata.
        """
        processor = self.get_processor(file_path)
        if not processor:
            logger.warning(f"No processor available for {file_path}")
            return None, None

        try:
            text = processor.extract_text()
            metadata = processor.extract_metadata()
            if metadata is None:
                metadata = {}
            metadata["source_file"] = str(file_path)
            metadata["file_type"] = file_path.suffix.lower()
            return text, metadata
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            return None, None

    def process_directory(self, collection_name: str = "neurofitness") -> None:
        """Process all files in the data directory.

        Args:
            collection_name (str): Name of the collection to store documents.
        """
        files = list(self.data_dir.glob("**/*"))
        files = [
            f for f in files if f.is_file() and f.suffix.lower() in self.processors
        ]

        if not files:
            logger.warning(f"No supported files found in {self.data_dir}")
            return

        documents: List[str] = []
        metadatas: List[Metadata] = []
        ids: List[str] = []

        for file_path in tqdm(files, desc="Processing files"):
            text, metadata = self.process_file(file_path)
            if text and metadata:
                documents.append(text)
                metadatas.append(metadata)
                ids.append(f"doc_{len(documents)}")

        if documents:
            logger.info(
                f"Adding {len(documents)} documents to collection {collection_name}"
            )
            self.db_manager.add_documents(
                collection_name=collection_name,
                documents=documents,
                metadatas=metadatas,
                ids=ids,
            )
            logger.info("Documents added successfully")
        else:
            logger.warning("No documents were processed successfully")


def main():
    """Main function to process data and create the vector database."""
    data_dir = "docs/data"
    db_dir = "vectordb/data"

    # Initialize database manager
    db_manager = DBManager(persist_directory=db_dir)

    # Initialize data processor
    processor = DataProcessor(data_dir=data_dir, db_manager=db_manager)

    # Process all files
    processor.process_directory()


if __name__ == "__main__":
    main()
