from typing import Type, TypeVar

from pydantic import BaseModel

from dutch_politics.store.bytes_store_base import BytesStoreBase
from dutch_politics.store.dict_store_base import DictStoreBase
from dutch_politics.store.object_store_base import ObjectStoreBase
from dutch_politics.store.store_provider_base import StoreProviderBase

T = TypeVar("T", bound=BaseModel)


class StoreProviderInMemory(StoreProviderBase):
    def __init__(self, database_name: str) -> None:
        super().__init__(database_name)

    def _get_bytes_store(self, collection_name: str) -> BytesStoreBase:
        raise NotImplementedError("Not implemented")

    def _get_dict_store(self, collection_name: str) -> DictStoreBase:
        raise NotImplementedError("Not implemented")

    def _get_object_store(
        self, collection_name: str, model_class: Type[T]
    ) -> ObjectStoreBase[T]:
        raise NotImplementedError("Not implemented")
