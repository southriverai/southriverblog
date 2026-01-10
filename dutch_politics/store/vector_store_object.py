from typing import Any, List, Optional

from langchain_core.documents import Document

from dutch_politics.components.embedding_model_base import EmbeddingModelBase
from dutch_politics.store.object_store_base import ObjectStoreBase
from dutch_politics.store.vector_store_base import VectorStoreBase


class VectorStoreObject(VectorStoreBase):
    def __init__(
        self,
        collection_name: str,
        object_store: ObjectStoreBase[Document],
        embeddings_model: EmbeddingModelBase,
    ):
        VectorStoreBase.__init__(self, collection_name)
        self.object_store = object_store


    def similarity_search(self, query: str, k: int = 4, **kwargs: Any) -> List[Document]:
        raise NotImplementedError("Not implemented")

    def from_texts(self, texts: List[str], **kwargs: Any) -> None:
        raise NotImplementedError("Not implemented")

    def get_vector_list_by_ids(
        self,
        ids: List[str],
    ) -> List[Optional[List[float]]]:
        vectors: List[Optional[List[float]]] = []
        documents: List[Optional[Document]] = self.object_store.mget(ids)
        for document in documents:
            if document is None:
                vectors.append(None)
            else:
                vectors.append(document.metadata.get("vector", None))
        return vectors

    def add_documents(self, documents: List[Document], vectors: List[List[float]]) -> None:
        entries: List[tuple[str, Document]] = []
        for document, vector in zip(documents, vectors):
            document.metadata["vector"] = vector
            if document.id is None:
                raise ValueError("Document ID is required")
            entries.append((document.id, document))
        self.object_store.mset(entries)
