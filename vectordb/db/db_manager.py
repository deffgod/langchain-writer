import logging
import os
from typing import Any, Dict, List, Optional, Union

import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.api.types import Metadata, QueryResult, WhereDocument
from chromadb.config import Settings


class DBManager:
    def __init__(self, persist_directory: str = "vectordb/data"):
        """Initialize the database manager.

        Args:
            persist_directory (str): Directory to persist the database.
        """
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False, allow_reset=True),
        )

        self.logger = logging.getLogger(__name__)
        self.collections: Dict[str, Collection] = {}

    def create_collection(
        self, name: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Collection:
        """Create a new collection or get existing one.

        Args:
            name (str): Name of the collection.
            metadata (Dict[str, Any], optional): Metadata for the collection.

        Returns:
            Collection: The created or existing collection.
        """
        try:
            collection = self.client.create_collection(
                name=name, metadata=metadata or {}
            )
            self.collections[name] = collection
            self.logger.info(f"Created collection: {name}")
            return collection
        except ValueError:
            collection = self.client.get_collection(name=name)
            self.collections[name] = collection
            self.logger.info(f"Retrieved existing collection: {name}")
            return collection

    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: Optional[List[Metadata]] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        """Add documents to a collection.

        Args:
            collection_name (str): Name of the collection.
            documents (List[str]): List of document texts.
            metadatas (List[Metadata], optional): Metadata for each document.
            ids (List[str], optional): IDs for each document.
        """
        if collection_name not in self.collections:
            self.create_collection(collection_name)

        collection = self.collections[collection_name]

        try:
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids or [f"doc_{i}" for i in range(len(documents))],
            )
            self.logger.info(
                f"Added {len(documents)} documents to collection: {collection_name}"
            )
        except Exception as e:
            self.logger.error(
                f"Error adding documents to collection {collection_name}: {str(e)}"
            )
            raise

    def query(
        self,
        collection_name: str,
        query_texts: Union[str, List[str]],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[WhereDocument] = None,
    ) -> QueryResult:
        """Query documents from a collection.

        Args:
            collection_name (str): Name of the collection.
            query_texts (Union[str, List[str]]): Query text or list of query texts.
            n_results (int): Number of results to return.
            where (Dict[str, Any], optional): Filter conditions for metadata.
            where_document (WhereDocument, optional): Filter conditions for documents.

        Returns:
            QueryResult: Query results containing documents, metadatas, and distances.
        """
        if collection_name not in self.collections:
            raise ValueError(f"Collection {collection_name} does not exist")

        collection = self.collections[collection_name]

        try:
            results = collection.query(
                query_texts=query_texts,
                n_results=n_results,
                where=where,
                where_document=where_document,
            )
            self.logger.info(f"Successfully queried collection: {collection_name}")
            return results
        except Exception as e:
            self.logger.error(f"Error querying collection {collection_name}: {str(e)}")
            raise

    def get_collection(self, name: str) -> Collection:
        """Get a collection by name.

        Args:
            name (str): Name of the collection.

        Returns:
            Collection: The requested collection.
        """
        if name not in self.collections:
            collection = self.client.get_collection(name=name)
            self.collections[name] = collection
            return collection
        return self.collections[name]

    def list_collections(self) -> List[str]:
        """List all collections in the database.

        Returns:
            List[str]: List of collection names.
        """
        return [collection.name for collection in self.client.list_collections()]

    def delete_collection(self, name: str) -> None:
        """Delete a collection.

        Args:
            name (str): Name of the collection to delete.
        """
        try:
            self.client.delete_collection(name=name)
            if name in self.collections:
                del self.collections[name]
            self.logger.info(f"Deleted collection: {name}")
        except ValueError as e:
            self.logger.error(f"Error deleting collection {name}: {str(e)}")
            raise
