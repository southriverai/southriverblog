import logging
from typing import Dict, Iterator, List, Optional, Sequence, Tuple, Type, TypeVar, Union

from pydantic import BaseModel

from dutch_politics.store.dict_store_base import DictStoreBase
from dutch_politics.store.object_store_base import ObjectStoreBase

T = TypeVar("T", bound=BaseModel)

logger = logging.getLogger(__name__)


class ObjectStoreNested(ObjectStoreBase[T]):
    def __init__(self, store: DictStoreBase, model_class: Type[T]) -> None:
        super().__init__(store.collection_name)
        self.store = store
        self.model_class = model_class

    def _dict_to_object(self, document: dict) -> T:
        return self.model_class(**document)  # type: ignore

    def mset(self, key_value_pairs: Sequence[tuple[str, T]]) -> None:
        key_dict_pairs: Sequence[tuple[str, dict]] = [
            (id, object.model_dump()) for id, object in key_value_pairs
        ]
        self.store.mset(key_dict_pairs)

    def mget(self, keys: Sequence[str]) -> list[Optional[T]]:
        list_dict = self.store.mget(keys)
        list_object: list[Optional[T]] = []
        for dict in list_dict:
            if dict is None:
                list_object.append(None)
            else:
                list_object.append(self._dict_to_object(dict))
        return list_object

    def mdelete(self, keys: Sequence[str]) -> None:
        self.store.mdelete(keys)

    def yield_keys(
        self, *, prefix: Optional[str] = None
    ) -> Union[Iterator[str], Iterator[str]]:
        return self.store.yield_keys(prefix=prefix)

    async def asample(self, count: int) -> List[T]:
        list_dict = await self.store.asample(count)
        list_object: List[T] = []
        for dict in list_dict:
            list_object.append(self._dict_to_object(dict))
        return list_object

    def query(
        self,
        query: Dict[str, str],
        order_by: List[Tuple[str, bool]] = [],
        limit: int = 0,
        offset: int = 0,
    ) -> List[T]:
        list_dict = self.store.query(query, order_by, limit, offset)
        list_object: List[T] = []
        for dict in list_dict:
            list_object.append(self._dict_to_object(dict))
        return list_object

    def mvalidate(self, keys: List[str]) -> int:
        dict_entries = self.store.mget(keys)
        object_entries_changed = []
        count_reformatted = 0
        for key, dict_entry in zip(keys, dict_entries):
            if dict_entry is None:
                continue
            object_entry_changed = self._dict_to_object(dict_entry)
            entry_dict_dump = object_entry_changed.model_dump()
            if entry_dict_dump != dict_entry:
                object_entries_changed.append((key, object_entry_changed))
                count_reformatted += 1
        self.mset(object_entries_changed)
        return count_reformatted

    def validate_all(self, batch_size: int = 1000) -> int:
        logger.info(f"Validating all entries in {self.store.collection_name}...")
        count_reformatted = 0
        logger.info("Retrieving keys...")
        keys = list(self.yield_keys())
        logger.info(f"Validating {len(keys)} entries...")
        from tqdm import trange

        for i in trange(0, len(keys), batch_size, desc="Validating batches"):
            keys_batch = keys[i : i + batch_size]
            count_reformatted += self.mvalidate(keys_batch)
        logger.info(f"Reformatted {count_reformatted} entries...")
        return count_reformatted
