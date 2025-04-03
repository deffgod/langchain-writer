import argparse
import logging
from pprint import pprint
from typing import Dict, List

from db.db_manager import DBManager

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def format_results(results: Dict) -> List[Dict]:
    """Format query results for display.

    Args:
        results: Raw query results from ChromaDB

    Returns:
        List[Dict]: Formatted results
    """
    formatted = []

    for i in range(len(results["documents"][0])):
        result = {
            "document": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i],
        }
        formatted.append(result)

    return formatted


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Query the vector knowledge base")

    parser.add_argument("query", help="Query text")

    parser.add_argument(
        "--persist-dir",
        default="vectordb_data",
        help="Directory containing ChromaDB data",
    )

    parser.add_argument(
        "--collection-name",
        default="neurofitness",
        help="Name of the ChromaDB collection",
    )

    parser.add_argument(
        "--n-results", type=int, default=5, help="Number of results to return"
    )

    parser.add_argument("--file-type", help="Filter by file type (e.g., .txt, .pdf)")

    args = parser.parse_args()

    try:
        # Initialize database manager
        db_manager = DBManager(
            persist_directory=args.persist_dir, collection_name=args.collection_name
        )

        # Prepare metadata filter
        where = {}
        if args.file_type:
            where["file_type"] = args.file_type

        # Query collection
        results = db_manager.query(
            query_text=args.query,
            n_results=args.n_results,
            where=where if where else None,
        )

        # Format and display results
        formatted_results = format_results(results)

        print(f"\nFound {len(formatted_results)} results for query: {args.query}\n")

        for i, result in enumerate(formatted_results, 1):
            print(f"Result {i}:")
            print(f"Source: {result['metadata']['source_file']}")
            print(f"Similarity: {1 - result['distance']:.4f}")
            print("\nContent:")
            print("-" * 80)
            print(
                result["document"][:500] + "..."
                if len(result["document"]) > 500
                else result["document"]
            )
            print("-" * 80)
            print()

        # Get collection stats
        stats = db_manager.get_collection_stats()
        print(f"\nTotal documents in collection: {stats['document_count']}")

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
