from typing import Any, List, Optional

from langchain_core.documents import Document

from dutch_politics.store.vector_store_base import VectorStoreBase


class VectorStoreCache(VectorStoreBase):
    def __init__(
        self,
        collection_name: str,
        vector_store_cache: VectorStoreBase,
        vector_store_backing: VectorStoreBase,
    ):
        super().__init__(collection_name)
        self.vector_stores_cache = vector_store_cache
        self.vector_stores_backing = vector_store_backing

    def similarity_search(self, query: str, k: int = 4, **kwargs: Any) -> List[Document]:
        return self.vector_stores_cache.similarity_search(query, k, **kwargs)

    def from_texts(self, texts: List[str], **kwargs: Any) -> None:
        self.vector_stores_cache.from_texts(texts, **kwargs)
        self.vector_stores_backing.from_texts(texts, **kwargs)

    def get_vector_list_by_ids(
        self,
        ids: List[str],
    ) -> List[Optional[List[float]]]:
        # first try to get the vectors from the cache
        dict_results = {}
        results_cache = self.vector_stores_cache.get_vector_list_by_ids(ids)
        ids_not_found: List[str] = []
        for id, vector in zip(ids, results_cache):
            if vector is None:
                ids_not_found.append(id)
            else:
                dict_results[id] = vector

        # if the vectors are not found in the cache, try to get them from the backing store
        if len(ids_not_found) > 0:
            results_backing: List[Optional[List[float]]] = self.vector_stores_backing.get_vector_list_by_ids(ids_not_found)
            for id, vector in zip(ids_not_found, results_backing):
                if vector is not None:
                    dict_results[id] = vector

        # todo return None for ids that are not found
        list_results: List[Optional[List[float]]] = []
        for id in ids:
            if id in dict_results:
                list_results.append(dict_results[id])
            else:
                list_results.append(None)

        return list_results