from pymongo import MongoClient
from config import MONGO_URI
import datetime
from pymongo import MongoClient, ReturnDocument
from bson.objectid import ObjectId
from typing import Dict, List, Optional, Tuple, Union

from utils.response_models import ErrorResponse


class QueryHelper:
    """
    A utility class for MongoDB operations that provides a simplified interface
    for common database operations with proper error handling and document transformation.

    This class uses the singleton pattern for MongoDB client connection and provides
    static methods for CRUD operations and other database utilities.
    """

    # Initialize MongoDB client and database as class-level attributes.
    try:
        client = MongoClient(MONGO_URI)
        db = client["AI_Story_Board"]
    except Exception as e:
        raise Exception(f"Error initializing MongoDB client: {e}")

    @staticmethod
    def _transform_document(doc: Dict) -> Dict:
        """
        Transform a document by replacing '_id' with 'id' as a string for readability.

        Args:
            doc: The MongoDB document to transform

        Returns:
            The transformed document with '_id' replaced by 'id' as a string
        """
        if not doc:
            return doc
        if "_id" in doc:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
        return doc

    @staticmethod
    def _transform_documents(docs: List[Dict]) -> List[Dict]:
        """
        Apply _transform_document to each document in the list.

        Args:
            docs: List of MongoDB documents to transform

        Returns:
            List of transformed documents
        """
        return [QueryHelper._transform_document(doc) for doc in docs]

    @staticmethod
    def insert_one(collection_name: str, document: Dict) -> Union[Dict, ErrorResponse]:
        """
        Insert a single document into the collection and return the inserted document.

        Args:
            collection_name: Name of the MongoDB collection
            document: Document to insert

        Returns:
            The inserted document with '_id' transformed to 'id', or an ErrorResponse
        """
        try:
            # Add timestamps for document creation
            document["created_on"] = datetime.datetime.utcnow()
            document["last_updated_on"] = datetime.datetime.utcnow()
            result = QueryHelper.db[collection_name].insert_one(document)
            doc = QueryHelper.db[collection_name].find_one({"_id": result.inserted_id})
            return QueryHelper._transform_document(doc)
        except Exception as e:
            return ErrorResponse(
                message=f"Error in insert_one for collection '{collection_name}': {e}",
                code=500,
                errors=[{"detail": str(e)}],
            )

    @staticmethod
    def find_one(collection_name: str, query: Dict) -> Union[Dict, ErrorResponse]:
        """
        Find and return a single document matching the query.

        Args:
            collection_name: Name of the MongoDB collection
            query: Query criteria to match documents

        Returns:
            The matching document with '_id' transformed to 'id', or an ErrorResponse
        """
        try:
            doc = QueryHelper.db[collection_name].find_one(query)
            return QueryHelper._transform_document(doc)
        except Exception as e:
            return ErrorResponse(
                message=f"Error in find_one for collection '{collection_name}': {e}",
                code=500,
                errors=[{"detail": str(e)}],
            )

    @staticmethod
    def find(
        collection_name: str,
        query: Dict,
        skip: int = 0,
        limit: int = 10,
        sort: Optional[List[Tuple[str, int]]] = None,
    ) -> Union[List[Dict], ErrorResponse]:
        """
        Find multiple documents based on the query with pagination and sorting.

        Args:
            collection_name: Name of the MongoDB collection
            query: Query criteria to match documents
            skip: Number of documents to skip (for pagination)
            limit: Maximum number of documents to return
            sort: List of tuples specifying sort fields and directions (1 for ascending, -1 for descending)

        Returns:
            List of matching documents with '_id' transformed to 'id', or an ErrorResponse
        """
        try:
            if sort is None:
                sort = [
                    ("created_on", -1)
                ]  # Default sort by creation date, newest first

            docs = list(
                QueryHelper.db[collection_name]
                .find(query)
                .skip(skip)
                .limit(limit)
                .sort(sort)
            )
            return QueryHelper._transform_documents(docs)
        except Exception as e:
            return ErrorResponse(
                message=f"Error in find for collection '{collection_name}': {e}",
                code=500,
                errors=[{"detail": str(e)}],
            )

    @staticmethod
    def update_one(
        collection_name: str, query: Dict, update: Dict, upsert: bool = False
    ) -> Union[Dict, ErrorResponse]:
        """
        Update a single document matching the query and return the updated document.

        Args:
            collection_name: Name of the MongoDB collection
            query: Query criteria to match the document to update
            update: Update operations to apply
            upsert: If True, create a new document if no match is found

        Returns:
            The updated document with '_id' transformed to 'id', or an ErrorResponse
        """
        try:
            # Add timestamp for document update
            update["last_updated_on"] = datetime.datetime.utcnow()
            updated_document = QueryHelper.db[collection_name].find_one_and_update(
                query,
                {"$set": update},
                return_document=ReturnDocument.AFTER,
                upsert=upsert,
            )
            return QueryHelper._transform_document(updated_document)
        except Exception as e:
            return ErrorResponse(
                message=f"Error in update_one for collection '{collection_name}': {e}",
                code=500,
                errors=[{"detail": str(e)}],
            )

    @staticmethod
    def delete_one(collection_name: str, query: Dict) -> Union[Dict, ErrorResponse]:
        """
        Delete a single document matching the query and return the deletion result.

        Args:
            collection_name: Name of the MongoDB collection
            query: Query criteria to match the document to delete

        Returns:
            Dictionary with deletion count, or an ErrorResponse
        """
        try:
            result = QueryHelper.db[collection_name].delete_one(query)
            return {"deleted_count": result.deleted_count}
        except Exception as e:
            return ErrorResponse(
                message=f"Error in delete_one for collection '{collection_name}': {e}",
                code=500,
                errors=[{"detail": str(e)}],
            )

    @staticmethod
    def count_documents(collection_name: str, query: Dict) -> Union[int, ErrorResponse]:
        """
        Count the number of documents matching the query.

        Args:
            collection_name: Name of the MongoDB collection
            query: Query criteria to match documents

        Returns:
            Count of matching documents, or an ErrorResponse
        """
        try:
            return QueryHelper.db[collection_name].count_documents(query)
        except Exception as e:
            return ErrorResponse(
                message=f"Error in count_documents for collection '{collection_name}': {e}",
                code=500,
                errors=[{"detail": str(e)}],
            )

    @staticmethod
    def aggregate(
        collection_name: str, pipeline: List[Dict]
    ) -> Union[List[Dict], ErrorResponse]:
        """
        Perform aggregation operations using MongoDB's aggregation framework.

        Args:
            collection_name: Name of the MongoDB collection
            pipeline: List of aggregation stages to apply

        Returns:
            List of aggregated documents with '_id' transformed to 'id', or an ErrorResponse
        """
        try:
            docs = list(QueryHelper.db[collection_name].aggregate(pipeline))
            return QueryHelper._transform_documents(docs)
        except Exception as e:
            return ErrorResponse(
                message=f"Error in aggregate for collection '{collection_name}': {e}",
                code=500,
                errors=[{"detail": str(e)}],
            )

    @staticmethod
    def bulk_insert(
        collection_name: str, documents: List[Dict]
    ) -> Union[List[Dict], ErrorResponse]:
        """
        Insert multiple documents into the collection.

        Args:
            collection_name: Name of the MongoDB collection
            documents: List of documents to insert

        Returns:
            List of inserted documents with '_id' transformed to 'id', or an ErrorResponse
        """
        try:
            current_time = datetime.datetime.utcnow()
            for doc in documents:
                doc["created_on"] = current_time
                doc["last_updated_on"] = datetime.datetime.utcnow()
            result = QueryHelper.db[collection_name].insert_many(documents)
            docs = list(
                QueryHelper.db[collection_name].find(
                    {"_id": {"$in": result.inserted_ids}}
                )
            )
            return QueryHelper._transform_documents(docs)
        except Exception as e:
            return ErrorResponse(
                message=f"Error in bulk_insert for collection '{collection_name}': {e}",
                code=500,
                errors=[{"detail": str(e)}],
            )

    @staticmethod
    def update_many(
        collection_name: str, query: Dict, update: Dict
    ) -> Union[List[Dict], ErrorResponse]:
        """
        Update multiple documents matching the query and return the updated documents.

        Args:
            collection_name: Name of the MongoDB collection
            query: Query criteria to match documents to update
            update: Update operations to apply

        Returns:
            List of updated documents with '_id' transformed to 'id', or an ErrorResponse
        """
        try:
            update["last_updated_on"] = datetime.datetime.utcnow()
            QueryHelper.db[collection_name].update_many(query, {"$set": update})
            docs = list(QueryHelper.db[collection_name].find(query))
            return QueryHelper._transform_documents(docs)
        except Exception as e:
            return ErrorResponse(
                message=f"Error in update_many for collection '{collection_name}': {e}",
                code=500,
                errors=[{"detail": str(e)}],
            )

    @staticmethod
    def delete_many(collection_name: str, query: Dict) -> Union[Dict, ErrorResponse]:
        """
        Delete multiple documents matching the query and return the deletion result.

        Args:
            collection_name: Name of the MongoDB collection
            query: Query criteria to match documents to delete

        Returns:
            Dictionary with deletion count, or an ErrorResponse
        """
        try:
            result = QueryHelper.db[collection_name].delete_many(query)
            return {"deleted_count": result.deleted_count}
        except Exception as e:
            return ErrorResponse(
                message=f"Error in delete_many for collection '{collection_name}': {e}",
                code=500,
                errors=[{"detail": str(e)}],
            )

    @staticmethod
    def get_object_id(id: str) -> Union[ObjectId, ErrorResponse]:
        """
        Convert a string ID to MongoDB's ObjectId.

        Args:
            id: String representation of a MongoDB ObjectId

        Returns:
            MongoDB ObjectId object, or an ErrorResponse if conversion fails
        """
        if not id or not isinstance(id, str):
            return ErrorResponse(
                message="Invalid ID format: ID must be a non-empty string",
                code=400,
                errors=[{"detail": "Invalid ID format"}],
            )

        # Check if the ID matches the ObjectId format (24 hex characters)
        if not all(c in "0123456789abcdefABCDEF" for c in id) or len(id) != 24:
            return ErrorResponse(
                message=f"Invalid ObjectId format: '{id}' is not a valid 24-character hex string",
                code=400,
                errors=[{"detail": "Invalid ObjectId format"}],
            )

        try:
            return ObjectId(id)
        except Exception as e:
            return ErrorResponse(
                message=f"Error converting id '{id}' to ObjectId: {e}",
                code=400,
                errors=[{"detail": str(e)}],
            )

    @staticmethod
    def soft_delete_one(
        collection_name: str, query: Dict
    ) -> Union[Dict, ErrorResponse]:
        """
        Soft delete a document by setting its 'is_deleted' flag to True.

        This method doesn't actually remove the document from the database,
        but marks it as deleted for application-level filtering.

        Args:
            collection_name: Name of the MongoDB collection
            query: Query criteria to match the document to soft delete

        Returns:
            The updated document with '_id' transformed to 'id', or an ErrorResponse
        """
        try:
            updated_document = QueryHelper.update_one(
                collection_name, query, {"is_deleted": True}
            )
            return QueryHelper._transform_document(updated_document)
        except Exception as e:
            return ErrorResponse(
                message=f"Error in soft_delete_one for collection '{collection_name}': {e}",
                code=500,
                errors=[{"detail": str(e)}],
            )
