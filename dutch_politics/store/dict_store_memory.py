import random
from typing import Dict, Iterator, List, Optional, Sequence, Union

from dutch_politics.store.dict_store_base import DictStoreBase


class DictStoreMemory(DictStoreBase):
    def __init__(self, collection_name: str) -> None:
        super().__init__(collection_name)
        self._dict: Dict[str, dict] = {}

    def mset(self, key_value_pairs: Sequence[tuple[str, dict]]) -> None:
        self._dict.update(key_value_pairs)

    def mget(self, keys: Sequence[str]) -> list[Optional[dict]]:
        return [self._dict[key] for key in keys]

    def mdelete(self, keys: Sequence[str]) -> None:
        for key in keys:
            self._dict.pop(key)

    def yield_keys(
        self, *, prefix: Optional[str] = None
    ) -> Union[Iterator[str], Iterator[str]]:
        if prefix is None:
            return iter(self._dict.keys())
        else:
            return (key for key in self._dict.keys() if key.startswith(prefix))

    async def asample(self, count: int) -> List[dict]:
        return random.sample(list(self._dict.values()), count)
