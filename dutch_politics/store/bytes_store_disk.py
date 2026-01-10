import os
import random
from typing import Iterator, List, Optional, Sequence, Union

from dutch_politics.store.bytes_store_base import BytesStoreBase


class BytesStoreDisk(BytesStoreBase):
    def __init__(self, collection_name: str, path_dir_store: str) -> None:
        super().__init__(collection_name)
        self.path_dir_store = path_dir_store
        if not os.path.exists(self.path_dir_store):
            os.makedirs(self.path_dir_store)

    def _path_file(self, id: str) -> str:
        return os.path.join(self.path_dir_store, id)

    def set(self, id: str, blob: bytes) -> None:
        path_file = self._path_file(id)
        with open(path_file, "wb") as f:
            f.write(blob)

    def get(self, id: str) -> Optional[bytes]:
        path_file = self._path_file(id)
        if not os.path.exists(path_file):
            return None
        with open(path_file, "rb") as f:
            return f.read()

    def delete(self, id: str) -> None:
        path_file = self._path_file(id)
        if os.path.exists(path_file):
            os.remove(path_file)

    def mget(self, keys: Sequence[str]) -> list[Optional[bytes]]:
        return [self.get(key) for key in keys]

    def mset(self, key_value_pairs: Sequence[tuple[str, bytes]]) -> None:
        for key, value in key_value_pairs:
            self.set(key, value)

    def mdelete(self, keys: Sequence[str]) -> None:
        for key in keys:
            self.delete(key)

    def list_ids(self, *, prefix: Optional[str] = None) -> List[str]:
        list_ids = os.listdir(self.path_dir_store)
        if prefix is None:
            return list_ids
        return [id for id in list_ids if id.startswith(prefix)]

    def yield_keys(
        self, *, prefix: Optional[str] = None
    ) -> Union[Iterator[str], Iterator[str]]:
        list_ids = os.listdir(self.path_dir_store)
        for id in list_ids:
            if prefix is None or id.startswith(prefix):
                yield id

    async def asample(self, count: int) -> List[bytes]:
        list_ids = os.listdir(self.path_dir_store)
        return [self.get_raise(id) for id in random.sample(list_ids, count)]
