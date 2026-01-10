import logging
from typing import Type, TypeVar

from langchain_core.stores import BaseStore
from pydantic import BaseModel
from pymongo import MongoClient

from dutch_politics.store.bytes_store_mongo import BytesStoreMongo
from dutch_politics.store.dict_store_base import DictStoreBase
from dutch_politics.store.dict_store_mongo import DictStoreMongo
from dutch_politics.store.object_store_base import ObjectStoreBase
from dutch_politics.store.object_store_nested import ObjectStoreNested
from dutch_politics.store.store_provider_base import StoreProviderBase

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class StoreProviderMongo(StoreProviderBase):
    def __init__(
        self,
        connection_string: str,
        initialize: bool = True,
    ) -> None:

        self.is_initialized = False
        database_uri = connection_string.split(";")[0]
        database_name = connection_string.split(";")[1].strip()
        super().__init__(database_name)
        self.client = MongoClient(database_uri)
        if initialize:
            self.initialize()

    def initialize(self) -> None:
        self.client.admin.command("ping")
        self.is_initialized = True

    def _get_bytes_store(self, collection_name: str) -> BaseStore[str, bytes]:
        return BytesStoreMongo(collection_name, self.client, self.database_name)

    def _get_dict_store(self, collection_name: str) -> DictStoreBase:
        return DictStoreMongo(collection_name, self.client, self.database_name)

    def _get_object_store(
        self, collection_name: str, model_class: Type[T]
    ) -> ObjectStoreBase[T]:
        return ObjectStoreNested(self.get_dict_store(collection_name), model_class)
