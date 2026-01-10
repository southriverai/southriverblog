import json
from typing import Dict, Iterator, List, Optional, Sequence, Tuple, Union

from dutch_politics.store.bytes_store_disk import BytesStoreDisk
from dutch_politics.store.dict_store_base import DictStoreBase


class DictStoreDisk(DictStoreBase):
    def __init__(self, collection_name: str, path_dir_store: str) -> None:
        super().__init__(collection_name)
        self._bytes_store = BytesStoreDisk(collection_name, path_dir_store)

    def mset(self, key_value_pairs: Sequence[tuple[str, dict]]) -> None:
        key_bytes_pairs = [
            (key, json.dumps(value).encode("utf-8")) for key, value in key_value_pairs
        ]
        self._bytes_store.mset(key_bytes_pairs)

    def mget(self, keys: Sequence[str]) -> list[Optional[dict]]:
        list_blob = self._bytes_store.mget(keys)
        list_dict: list[Optional[dict]] = []
        for blob in list_blob:
            if blob is None:
                list_dict.append(None)
            else:
                list_dict.append(json.loads(blob.decode("utf-8")))
        return list_dict

    def mdelete(self, keys: Sequence[str]) -> None:
        self._bytes_store.mdelete(keys)

    def yield_keys(
        self, *, prefix: Optional[str] = None
    ) -> Union[Iterator[str], Iterator[str]]:
        return self._bytes_store.yield_keys(prefix=prefix)

    async def asample(self, count: int) -> List[dict]:
        list_blob = await self._bytes_store.asample(count)
        return [json.loads(blob.decode("utf-8")) for blob in list_blob]

    def query(
        self,
        query: Dict[str, str],
        order_by: List[Tuple[str, bool]] = [],
        limit: int = 0,
        offset: int = 0,
    ) -> List[dict]:
        raise NotImplementedError("Not implemented")
