from typing import List, Optional

from langchain_pinecone import PineconeVectorStore

from dutch_politics.components.embedding_model_base import EmbeddingModelBase
from dutch_politics.store.vector_store_base import VectorStoreBase


class VectorStorePinecone(VectorStoreBase, PineconeVectorStore):
    def __init__(
        self,
        collection_name: str,
        embeddings_model: EmbeddingModelBase,
        pinecone_api_key: str,
    ):
        # todo this is a hack to get the vector store to work
        PineconeVectorStore.__init__(
            self,
            index_name=collection_name,
            embedding=embeddings_model,
            pinecone_api_key=pinecone_api_key,
        )
        VectorStoreBase.__init__(self, collection_name)
        self.embeddings_model = embeddings_model

    def get_vector_list_by_ids(
        self,
        ids: List[str],
    ) -> List[Optional[List[float]]]:
        index = self.index  # type: ignore
        response = index.fetch(ids=ids)  # type: ignore
        return [vector.values for vector in response.vectors.values()]
