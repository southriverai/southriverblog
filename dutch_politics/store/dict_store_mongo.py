import logging
import re
from typing import Dict, Iterator, List, Optional, Sequence, Tuple, Union

from pymongo import MongoClient
from pymongo.command_cursor import CommandCursor as PymongoCommandCursor

from dutch_politics.store.dict_store_base import DictStoreBase

logger = logging.getLogger(__name__)


class DictStoreMongo(DictStoreBase):
    def __init__(self, collection_name: str, client: MongoClient, database_name: str) -> None:
        super().__init__(collection_name)
        self.client: MongoClient = client
        # self.client.admin.command('ping')
        self.database = self.client[database_name]
        self.collection = self.database[self.collection_name]

    def mset(self, key_value_pairs: Sequence[tuple[str, dict]]) -> None:
        from pymongo import ReplaceOne

        operations = []
        for key, value in key_value_pairs:
            document = {"_id": key, "document": value}
            operations.append(
                ReplaceOne(
                    {"_id": key},  # filter
                    document,  # replacement
                    upsert=True,  # upsert if not found
                )
            )

        if operations:
            self.collection.bulk_write(operations)

    def mget(self, keys: Sequence[str]) -> list[Optional[dict]]:
        if not keys:
            return []

        # Create a mapping of _id to document for efficient lookup
        id_to_doc = {}
        query = {"_id": {"$in": list(keys)}}
        for doc in self.collection.find(query):
            id_to_doc[doc["_id"]] = doc["document"]

        # Return results in the same order as requested keys
        result = []
        for key in keys:
            result.append(id_to_doc.get(key))

        return result

    def mdelete(self, keys: Sequence[str]) -> None:
        ids = list(keys)
        query = {"_id": {"$in": ids}}
        self.collection.delete_many(query)

    def yield_keys(self, *, prefix: Optional[str] = None) -> Union[Iterator[str], Iterator[str]]:
        if prefix is None:
            # Return all keys
            for doc in self.collection.find({}, {"_id": 1}):
                yield doc["_id"]
        else:
            # Return keys with prefix (escape special regex characters)
            escaped_prefix = re.escape(prefix)
            query = {"_id": {"$regex": f"^{escaped_prefix}"}}
            for doc in self.collection.find(query, {"_id": 1}):
                yield doc["_id"]

    def clear(self) -> None:
        """Clear all documents from the collection."""
        self.collection.delete_many({})

    async def asample(self, count: int) -> List[dict]:
        cursor: PymongoCommandCursor = self.collection.aggregate([{"$sample": {"size": count}}])
        list_entry = cursor.to_list(length=count)
        list_doc = []
        for entry in list_entry:
            list_doc.append(entry["document"])
        return list_doc

    def query(
        self,
        query: Dict[str, str],
        order_by: List[Tuple[str, bool]] = [],
        limit: int = 0,
        offset: int = 0,
    ) -> List[dict]:
        query_mod = {}
        for key in query:
            query_mod["document." + key] = query[key]
        order_mod = []
        for field, asc in order_by:
            order_mod.append(("document." + field, 1 if asc else -1))

        cursor = self.collection.find(query_mod)
        # check if cursor is empty
        # if not cursor.alive:
        #     return {}
        if len(order_mod) > 0:
            cursor = cursor.sort(order_mod)
        if limit > 0:
            cursor = cursor.limit(limit)
        if offset > 0:
            cursor = cursor.skip(offset)

        list_document = []
        for document_result in cursor:
            list_document.append(document_result["document"])
        return list_document
