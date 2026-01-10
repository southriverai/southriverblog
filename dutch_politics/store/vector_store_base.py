from typing import List, Optional

from langchain_core.vectorstores import VectorStore


class VectorStoreBase(VectorStore):
    def __init__(
        self,
        collection_name: str,
    ):
        self.collection_name = collection_name

    def get_vector_list_by_ids(
        self,
        ids: List[str],
    ) -> List[Optional[List[float]]]:
        raise NotImplementedError("Not implemented")
