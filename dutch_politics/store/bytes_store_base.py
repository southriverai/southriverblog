from abc import abstractmethod
from typing import Iterator, List, Optional, Sequence

from fastapi import HTTPException
from langchain_core.stores import BaseStore


class BytesStoreBase(BaseStore[str, bytes]):
    def __init__(self, collection_name: str) -> None:
        self.collection_name = collection_name
        pass

    @abstractmethod
    def mset(self, key_value_pairs: Sequence[tuple[str, bytes]]) -> None:
        pass

    def set(self, key: str, value: bytes) -> None:
        self.mset([(key, value)])

    @abstractmethod
    def mget(self, keys: Sequence[str]) -> List[Optional[bytes]]:
        pass

    def get_raise(self, key: str) -> bytes:
        value = self.mget([key])[0]
        if value is None:
            raise HTTPException(status_code=404, detail=f"Key {key} not found in store")
        return value

    @abstractmethod
    def mdelete(self, keys: Sequence[str]) -> None:
        pass

    @abstractmethod
    def yield_keys(self, *, prefix: Optional[str] = None) -> Iterator[str]:
        pass

    @abstractmethod
    async def asample(self, count: int) -> List[bytes]:
        pass
