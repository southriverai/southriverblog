

from dutch_politics.components.embedding_model_base import EmbeddingModelBase
from dutch_politics.store.vector_store_base import VectorStoreBase
from dutch_politics.store.vector_store_cache import VectorStoreCache
from dutch_politics.store.vector_store_provider_base import \
    VectorStoreProviderBase


class VectorStoreProviderCache(VectorStoreProviderBase):
    def __init__(
        self,
        database_name: str,
        vector_store_providers_base: VectorStoreProviderBase,
        vector_store_providers_cache: VectorStoreProviderBase,
    ):
        super().__init__(database_name)
        self.vector_store_providers_base = vector_store_providers_base
        self.vector_store_providers_cache = vector_store_providers_cache

    def get_vector_store(
        self, collection_name: str,
        embeddings_model: EmbeddingModelBase,
    ) -> VectorStoreBase:
        vector_store_base = self.vector_store_providers_base.get_vector_store(collection_name, embeddings_model)
        vector_store_cache = self.vector_store_providers_cache.get_vector_store(collection_name, embeddings_model)
        return VectorStoreCache(collection_name, vector_store_cache, vector_store_base)
