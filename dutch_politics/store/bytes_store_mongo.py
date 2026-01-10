from typing import Iterator, List, Optional, Sequence, Tuple

from pymongo import MongoClient

from dutch_politics.store.bytes_store_base import BytesStoreBase
from dutch_politics.store.dict_store_mongo import DictStoreMongo


class BytesStoreMongo(BytesStoreBase):
    def __init__(
        self, collection_name: str, client: MongoClient, database_name: str
    ) -> None:
        super().__init__(collection_name)
        self.dict_store = DictStoreMongo(collection_name, client, database_name)

    def mget(self, keys: Sequence[str]) -> List[Optional[bytes]]:
        raise NotImplementedError("Not implemented")

    def mset(self, key_value_pairs: Sequence[Tuple[str, bytes]]) -> None:
        raise NotImplementedError("Not implemented")

    def mdelete(self, keys: Sequence[str]) -> None:
        raise NotImplementedError("Not implemented")

    def yield_keys(self, prefix: Optional[str] = None) -> Iterator[str]:
        raise NotImplementedError("Not implemented")

    async def asample(self, count: int) -> List[bytes]:
        raise NotImplementedError("Not implemented")
