import argparse
import logging
from typing import Any, Dict, List, Optional

from chromadb.api.types import QueryResult
from db.db_manager import DBManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def format_results(results: QueryResult) -> str:
    """Format query results for display.

    Args:
        results (QueryResult): Query results from ChromaDB.

    Returns:
        str: Formatted results string.
    """
    output = []

    # Check if results exist and have documents
    if not isinstance(results, dict):
        return "Invalid results format"

    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])
    distances = results.get("distances", [])

    if not documents or not isinstance(documents, list) or len(documents) == 0:
        return "No results found"

    docs = documents[0] if isinstance(documents[0], list) else []
    metas = metadatas[0] if isinstance(metadatas, list) and len(metadatas) > 0 else []
    dists = distances[0] if isinstance(distances, list) and len(distances) > 0 else []

    if not docs:
        return "No document content found"

    for i, (doc, metadata, distance) in enumerate(zip(docs, metas, dists)):
        output.append(f"\nResult {i + 1} (Distance: {distance:.4f})")
        output.append(f"Source: {metadata.get('source_file', 'Unknown')}")
        output.append(f"Type: {metadata.get('file_type', 'Unknown')}")
        output.append("\nContent Preview:")
        # Show first 200 characters of the document
        preview = doc[:200] + "..." if len(doc) > 200 else doc
        output.append(preview)
        output.append("-" * 80)

    return "\n".join(output)


def query_database(
    query: str,
    collection_name: str = "neurofitness",
    n_results: int = 5,
    db_dir: str = "vectordb/data",
) -> None:
    """Query the vector database.

    Args:
        query (str): Query text.
        collection_name (str): Name of the collection to query.
        n_results (int): Number of results to return.
        db_dir (str): Directory containing the vector database.
    """
    try:
        # Initialize database manager
        db_manager = DBManager(persist_directory=db_dir)

        # Get collection
        collection_names = db_manager.list_collections()
        if not collection_names:
            logger.error("No collections found in the database")
            return

        if collection_name not in collection_names:
            logger.error(
                f"Collection '{collection_name}' not found. Available collections: {collection_names}"
            )
            return

        # Query the collection
        logger.info(f"Querying collection '{collection_name}' with: {query}")
        results = db_manager.query(
            collection_name=collection_name, query_texts=query, n_results=n_results
        )

        # Format and display results
        formatted_results = format_results(results)
        print(formatted_results)

    except Exception as e:
        logger.error(f"Error querying database: {str(e)}")


def main():
    """Main function to handle command-line interface."""
    parser = argparse.ArgumentParser(description="Query the vector database")
    parser.add_argument("query", help="Query text")
    parser.add_argument(
        "--collection",
        "-c",
        default="neurofitness",
        help="Name of the collection to query",
    )
    parser.add_argument(
        "--results", "-n", type=int, default=5, help="Number of results to return"
    )
    parser.add_argument(
        "--db-dir",
        "-d",
        default="vectordb/data",
        help="Directory containing the vector database",
    )

    args = parser.parse_args()
    query_database(
        query=args.query,
        collection_name=args.collection,
        n_results=args.results,
        db_dir=args.db_dir,
    )


if __name__ == "__main__":
    main()
