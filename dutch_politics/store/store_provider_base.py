import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Type, TypeVar

from pydantic import BaseModel

from dutch_politics.store.bytes_store_base import BytesStoreBase
from dutch_politics.store.dict_store_base import DictStoreBase
from dutch_politics.store.object_store_base import ObjectStoreBase

T = TypeVar("T", bound=BaseModel)

logger = logging.getLogger(__name__)


class StoreProviderBase(ABC):
    def __init__(self, database_name: str) -> None:
        self.database_name = database_name
        self._bytes_collection_names = []
        self._dict_collection_names = []
        self._object_collections: Dict[str, ObjectStoreBase] = {}

    def get_bytes_store(self, collection_name: str) -> BytesStoreBase:
        self._bytes_collection_names.append(collection_name)
        return self._get_bytes_store(collection_name)

    @abstractmethod
    def _get_bytes_store(self, collection_name: str) -> BytesStoreBase:
        raise NotImplementedError("Not implemented")

    def get_dict_store(self, collection_name: str) -> DictStoreBase:
        self._dict_collection_names.append(collection_name)
        return self._get_dict_store(collection_name)

    @abstractmethod
    def _get_dict_store(self, collection_name: str) -> DictStoreBase:
        raise NotImplementedError("Not implemented")

    def get_object_store(
        self, collection_name: str, model_class: Type[T]
    ) -> ObjectStoreBase[T]:
        object_store = self._get_object_store(collection_name, model_class)
        self._object_collections[collection_name] = object_store
        return object_store

    @abstractmethod
    def _get_object_store(
        self, collection_name: str, model_class: Type[T]
    ) -> ObjectStoreBase[T]:
        raise NotImplementedError("Not implemented")

    def get_collection_names(self) -> List[str]:
        collection_names = []
        collection_names.extend(self._bytes_collection_names)
        collection_names.extend(self._dict_collection_names)
        collection_names.extend(list(self._object_collections.keys()))
        return collection_names

    def validate_collection(self, collection_name: str) -> None:
        self._object_collections[collection_name].validate_all()

    def validate_all(self) -> None:
        for collection_name in self._object_collections.keys():
            logger.info(f"Validating collection {collection_name}...")
            self.validate_collection(collection_name)
