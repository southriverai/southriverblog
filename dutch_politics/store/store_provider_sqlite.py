import logging
import os
from typing import Type, TypeVar

from langchain_core.stores import BaseStore
from pydantic import BaseModel

from dutch_politics.store.bytes_store_base import BytesStoreBase
from dutch_politics.store.bytes_store_sqlite import BytesStoreSqlite
from dutch_politics.store.dict_store_base import DictStoreBase
from dutch_politics.store.dict_store_sqlite import DictStoreSqlite
from dutch_politics.store.object_store_nested import ObjectStoreNested
from dutch_politics.store.store_provider_base import StoreProviderBase

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class StoreProviderSqlite(StoreProviderBase):
    def __init__(
        self,
        database_name: str,
        path_dir_database: str
    ) -> None:
        super().__init__(database_name)
        self.path_dir_database = path_dir_database

    def _get_bytes_store(self, collection_name: str) -> BytesStoreBase:
        path_file_database = os.path.join(
            self.path_dir_database, self.database_name, collection_name + ".db"
        )
        return BytesStoreSqlite(collection_name, path_file_database)

    def _get_dict_store(self, collection_name: str) -> DictStoreBase:
        path_file_database = os.path.join(
            self.path_dir_database, self.database_name, collection_name + ".db"
        )
        return DictStoreSqlite(collection_name, path_file_database)

    def _get_object_store(self, collection_name: str, model_class: Type[T]) -> BaseStore[str, T]:
        dict_store = self._get_dict_store(collection_name)
        return ObjectStoreNested(dict_store, model_class)  # type: ignore
