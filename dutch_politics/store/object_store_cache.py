from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple, TypeVar

from pydantic import BaseModel

from dutch_politics.store.object_store_base import ObjectStoreBase

T = TypeVar("T", bound=BaseModel)


class ObjectStoreCache(ObjectStoreBase[T]):
    def __init__(
        self,
        object_store_cache: ObjectStoreBase[T],
        object_store_base: ObjectStoreBase[T],
    ) -> None:
        if object_store_cache.collection_name != object_store_base.collection_name:
            raise ValueError("Collection names must match")
        super().__init__(object_store_cache.collection_name)
        self.object_store_cache = object_store_cache
        self.object_store_base = object_store_base

    def mset(self, key_value_pairs: Sequence[tuple[str, T]]) -> None:
        self.object_store_cache.mset(key_value_pairs)
        self.object_store_base.mset(key_value_pairs)

    def mget(self, keys: Sequence[str]) -> List[Optional[T]]:
        results_dict: Dict[str, T] = {}
        # first try to get the results from the cache
        ids_not_found: List[str] = []
        results_cache = self.object_store_cache.mget(keys)
        for key, result_cache in zip(keys, results_cache):
            if result_cache is not None:
                results_dict[key] = result_cache
            else:
                ids_not_found.append(key)

        # then try to get the results from the base
        if len(ids_not_found) > 0:
            results_base = self.object_store_base.mget(ids_not_found)
            for key, result_base in zip(ids_not_found, results_base):
                if result_base is not None:
                    results_dict[key] = result_base

        # then turn it back into a list with the same order as the keys
        results_list: List[Optional[T]] = []
        for key in keys:
            if key in results_dict:
                results_list.append(results_dict[key])
            else:
                results_list.append(None)
        return results_list

    def mdelete(self, keys: Sequence[str]) -> None:
        self.object_store_cache.mdelete(keys)
        self.object_store_base.mdelete(keys)

    def yield_keys(self, *, prefix: Optional[str] = None) -> Iterator[str]:
        return self.object_store_base.yield_keys(prefix=prefix)

    async def asample(self, count: int) -> List[T]:
        # sample the base directly because the cache is not used for sampling
        return await self.object_store_base.asample(count)

    def query(
        self,
        query: Dict[str, Any],
        order_by: List[Tuple[str, bool]] = [],
        limit: int = 0,
        offset: int = 0,
    ) -> List[T]:
        return self.object_store_base.query(query, order_by, limit, offset)

    def validate_all(self, verbose: bool = False) -> int:
        raise NotImplementedError("Not implemented")

    def mvalidate(self, keys: List[str]) -> int:
        raise NotImplementedError("Not implemented")
