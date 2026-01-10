import re
import zlib
from typing import Iterator, List, Optional, Sequence, Tuple

from langchain.storage.exceptions import InvalidKeyException
from sqlalchemy.engine.base import Engine

from dutch_politics.store.bytes_store_base import BytesStoreBase


class BytesStorePostgres(BytesStoreBase):
    def __init__(self, collection_name: str, postgres_engine: Engine, object_store_name: str) -> None:
        super().__init__(collection_name)
        self._postgres_engine = postgres_engine
        self._object_store_name = object_store_name

    def _compress(self, data: bytes) -> bytes:
        """Compress data using zlib."""
        return zlib.compress(data)

    def _decompress(self, data: bytes) -> bytes:
        """Decompress data using zlib."""
        return zlib.decompress(data)

    def _validate_key(self, key: str) -> None:
        """Validate the key to ensure it has valid characters."""
        if not re.match(r"^[a-zA-Z0-9_.\-/]+$", key):
            raise InvalidKeyException(f"Invalid characters in key: {key}")

    def _should_use_bulk_request(self, keys: Sequence) -> bool:
        return len(keys) >= 5

    def mget(self, keys: Sequence[str]) -> List[Optional[bytes]]:
        raise NotImplementedError("Not implemented")
        # [self._validate_key(key) for key in keys]
        # if self._should_use_bulk_request(keys):
        #     caches = AppContainer.resource_repository.get_resources(keys)
        # else:
        #     caches = []

        #     for key in keys:
        #         resource = AppContainer.resource_repository.get_resource(key)
        #         caches.append(resource)

        # return [self._decompress(cache.value) for cache in caches]

    def mset(self, key_value_pairs: Sequence[Tuple[str, bytes]]) -> None:
        raise NotImplementedError("Not implemented")

        # compressed_pairs = []

        # for key, value in key_value_pairs:
        #     compressed_pairs.append(
        #         (
        #             key,
        #             self._compress(value),
        #         )
        #     )

        # AppContainer.cache_repository.set_caches(keys_and_values=compressed_pairs)

    def mdelete(self, keys: Sequence[str]) -> None:
        raise NotImplementedError("Not implemented")

        # [self._validate_key(key) for key in keys]

        # AppContainer.cache_repository.delete_caches(keys)

    def yield_keys(self, prefix: Optional[str] = None) -> Iterator[str]:
        raise NotImplementedError("Not implemented")

        # if prefix:
        #     self._validate_key(prefix)

        # for cache in AppContainer.cache_repository.yield_caches(prefix=prefix):
        #     yield cache.key

    async def asample(self, count: int) -> List[bytes]:
        raise NotImplementedError("Not implemented")

        # list_keys = random.sample(list(self.yield_keys()), count)
        # return [self.mget(list_keys)]