from abc import abstractmethod
from typing import (
    Any,
    Dict,
    Generic,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
)

from fastapi import HTTPException
from langchain_core.stores import BaseStore
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class ObjectStoreBase(Generic[T], BaseStore[str, T]):
    def __init__(self, collection_name: str) -> None:
        self.collection_name = collection_name

    @abstractmethod
    def mset(self, key_value_pairs: Sequence[tuple[str, T]]) -> None:
        pass

    def set(self, key: str, value: T) -> None:
        self.mset([(key, value)])

    @abstractmethod
    def mget(self, keys: Sequence[str]) -> List[Optional[T]]:
        pass

    def get_raise(self, key: str) -> T:
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
    async def asample(self, count: int) -> List[T]:
        pass

    @abstractmethod
    def query(
        self,
        query: Dict[str, Any],
        order_by: List[Tuple[str, bool]] = [],
        limit: int = 0,
        offset: int = 0,
    ) -> List[T]:
        pass

    @abstractmethod
    def validate_all(self, verbose: bool = False) -> int:
        pass

    @abstractmethod
    def mvalidate(self, keys: List[str]) -> int:
        pass
