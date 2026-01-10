import json
from typing import Dict, Iterator, List, Optional, Sequence, Tuple, Union

from dutch_politics.store.bytes_store_base import BytesStoreBase
from dutch_politics.store.dict_store_base import DictStoreBase


class DictStoreBytes(DictStoreBase):
    def __init__(self, store: BytesStoreBase) -> None:
        super().__init__(store.collection_name)
        self._store: BytesStoreBase = store

    def mset(self, key_value_pairs: Sequence[tuple[str, dict]]) -> None:
        key_bytes_pairs: Sequence[tuple[str, bytes]] = [
            (key, json.dumps(value).encode("utf-8")) for key, value in key_value_pairs
        ]
        self._store.mset(key_bytes_pairs)

    def mget(self, keys: Sequence[str]) -> list[Optional[dict]]:
        list_bytes = self._store.mget(keys)
        list_dict: list[Optional[dict]] = []
        for bytes in list_bytes:
            if bytes is None:
                list_dict.append(None)
            else:
                list_dict.append(json.loads(bytes))
        return list_dict

    def mdelete(self, keys: Sequence[str]) -> None:
        for key in keys:
            self._store.mdelete(key)

    def yield_keys(
        self, *, prefix: Optional[str] = None
    ) -> Union[Iterator[str], Iterator[str]]:
        if prefix is None:
            return self._store.yield_keys()
        else:
            return (key for key in self._store.yield_keys() if key.startswith(prefix))

    async def asample(self, count: int) -> List[dict]:
        list_bytes = await self._store.asample(count)
        return [json.loads(bytes.decode("utf-8")) for bytes in list_bytes]

    def query(
        self,
        query: Dict[str, str],
        order_by: List[Tuple[str, bool]] = [],
        limit: int = 0,
        offset: int = 0,
    ) -> List[dict]:
        raise NotImplementedError("Not implemented")
