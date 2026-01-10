import logging
from typing import Type, TypeVar

from pydantic import BaseModel

from dutch_politics.store.bytes_store_base import BytesStoreBase
from dutch_politics.store.dict_store_base import DictStoreBase
from dutch_politics.store.dict_store_cache import DictStoreCache
from dutch_politics.store.object_store_base import ObjectStoreBase
from dutch_politics.store.object_store_cache import ObjectStoreCache
from dutch_politics.store.store_provider_base import StoreProviderBase

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class StoreProviderCache(StoreProviderBase):
    def __init__(
        self,
        database_name: str,
        store_provider_cache: StoreProviderBase,
        store_provider_base: StoreProviderBase,
    ) -> None:
        super().__init__(database_name)
        self.store_provider_cache = store_provider_cache
        self.store_provider_base = store_provider_base

    def _get_bytes_store(self, collection_name: str) -> BytesStoreBase:
        raise NotImplementedError("Not implemented")

    def _get_dict_store(self, collection_name: str) -> DictStoreBase:
        dict_store_cache = self.store_provider_cache.get_dict_store(collection_name)
        dict_store_base = self.store_provider_base.get_dict_store(collection_name)
        return DictStoreCache(dict_store_cache, dict_store_base)

    def _get_object_store(
        self, collection_name: str, model_class: Type[T]
    ) -> ObjectStoreBase[T]:
        object_store_cache = self.store_provider_cache.get_object_store(
            collection_name, model_class
        )
        object_store_base = self.store_provider_base.get_object_store(
            collection_name, model_class
        )
        return ObjectStoreCache(object_store_cache, object_store_base)
