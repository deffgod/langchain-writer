import argparse
import logging
import os
from pathlib import Path
from typing import Dict, List

from db.db_manager import DBManager
from processors.processor_factory import ProcessorFactory
from tqdm import tqdm

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def process_directory(
    input_dir: str, db_manager: DBManager, batch_size: int = 10
) -> None:
    """Process all supported files in a directory.

    Args:
        input_dir: Directory containing files to process
        db_manager: Database manager instance
        batch_size: Number of documents to process in each batch
    """
    input_path = Path(input_dir)
    if not input_path.exists():
        raise ValueError(f"Directory not found: {input_dir}")

    # Get all files in directory
    files = []
    for ext in ProcessorFactory.supported_extensions():
        files.extend(input_path.glob(f"**/*{ext}"))

    if not files:
        logger.warning(f"No supported files found in {input_dir}")
        return

    logger.info(f"Found {len(files)} files to process")

    # Process files in batches
    current_batch = {"documents": [], "metadatas": [], "ids": []}

    for file_path in tqdm(files, desc="Processing files"):
        try:
            # Get appropriate processor
            processor = ProcessorFactory.get_processor(str(file_path))

            # Extract text and metadata
            text = processor.extract_text()
            metadata = processor.extract_metadata()

            # Add source file info to metadata
            metadata.update(
                {
                    "source_file": str(file_path),
                    "file_type": file_path.suffix.lower(),
                    "relative_path": str(file_path.relative_to(input_path)),
                }
            )

            # Add to current batch
            current_batch["documents"].append(text)
            current_batch["metadatas"].append(metadata)
            current_batch["ids"].append(f"doc_{len(current_batch['documents'])}")

            # Process batch if full
            if len(current_batch["documents"]) >= batch_size:
                db_manager.add_documents(
                    documents=current_batch["documents"],
                    metadatas=current_batch["metadatas"],
                    ids=current_batch["ids"],
                )
                current_batch = {"documents": [], "metadatas": [], "ids": []}

        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            continue

    # Process remaining documents
    if current_batch["documents"]:
        db_manager.add_documents(
            documents=current_batch["documents"],
            metadatas=current_batch["metadatas"],
            ids=current_batch["ids"],
        )

    # Log collection statistics
    stats = db_manager.get_collection_stats()
    logger.info(f"Processed {stats['document_count']} documents successfully")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build vector knowledge base from documents"
    )

    parser.add_argument("input_dir", help="Directory containing documents to process")

    parser.add_argument(
        "--persist-dir",
        default="vectordb_data",
        help="Directory to persist ChromaDB data",
    )

    parser.add_argument(
        "--collection-name",
        default="neurofitness",
        help="Name of the ChromaDB collection",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Number of documents to process in each batch",
    )

    args = parser.parse_args()

    try:
        # Initialize database manager
        db_manager = DBManager(
            persist_directory=args.persist_dir, collection_name=args.collection_name
        )

        # Process directory
        process_directory(
            input_dir=args.input_dir, db_manager=db_manager, batch_size=args.batch_size
        )

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
