
from langchain_core.documents import Document

from dutch_politics.components.embedding_model_base import EmbeddingModelBase
from dutch_politics.store.store_provider_sqlite import StoreProviderSqlite
from dutch_politics.store.vector_store_base import VectorStoreBase
from dutch_politics.store.vector_store_object import VectorStoreObject
from dutch_politics.store.vector_store_provider_base import \
    VectorStoreProviderBase


class VectorStoreProviderSqlite(VectorStoreProviderBase):
    def __init__(
        self,
        database_name: str,
        path_dir_database: str,
    ) -> None:
        super().__init__(database_name)
        self.store_provider = StoreProviderSqlite(database_name, path_dir_database)

    def get_vector_store(
        self,
        collection_name: str,
        embeddings_model: EmbeddingModelBase,
    ) -> VectorStoreBase:
        object_store = self.store_provider.get_object_store(collection_name, Document)
        return VectorStoreObject(collection_name, object_store, embeddings_model)
