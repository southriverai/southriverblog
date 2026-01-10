import json
import random
from typing import Iterator, List, Optional, Sequence, Union

from sqlalchemy.engine.base import Engine

from dutch_politics.store.bytes_store_postgres import BytesStorePostgres
from dutch_politics.store.dict_store_base import DictStoreBase


class DictStorePostgres(DictStoreBase):
    def __init__(self, collection_name: str, postgres_engine: Engine, object_store_name: str) -> None:
        super().__init__(collection_name)
        self._bytes_store: BytesStorePostgres = BytesStorePostgres(
            collection_name, postgres_engine, object_store_name,
            )

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
        list_blob = self._bytes_store.mget(
            random.sample(list(self._bytes_store.yield_keys()), count)
        )
        return [
            json.loads(blob.decode("utf-8")) for blob in list_blob if blob is not None
        ]
