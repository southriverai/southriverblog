from typing import Optional

from pinecone import Pinecone

from dutch_politics.components.embedding_model_base import EmbeddingModelBase
from dutch_politics.store.vector_store_base import VectorStoreBase
from dutch_politics.store.vector_store_pinecone import VectorStorePinecone
from dutch_politics.store.vector_store_provider_base import VectorStoreProviderBase


class VectorStoreProviderPinecone(VectorStoreProviderBase):
    def __init__(
        self,
        database_name: str,
        api_key: str,
        cloud: str = "aws",
        region: str = "us-east-1",
    ):
        super().__init__(database_name)
        """
        Initialize Pinecone Vector Store Provider.

        Args:
            api_key: Pinecone API key
            embeddings: Embeddings model to use for vectorization
            cloud: Cloud provider (e.g., 'aws', 'gcp', 'azure')
            region: Cloud region (e.g., 'us-east-1')
        """
        self.api_key = api_key
        self.cloud = cloud
        self.region = region
        self.client = Pinecone(api_key=self.api_key)

    def get_vector_store(
        self,
        collection_name: str,
        embeddings_model: EmbeddingModelBase,
        namespace: Optional[str] = None,
    ) -> VectorStoreBase:
        """
        Get or create a vector store for the given collection name (index name).

        Args:
            collection_name: Name of the Pinecone index to use
            namespace: Optional namespace within the index for data isolation

        Returns:
            VectorStore instance for the specified collection
        """
        # Check if index exists, if not, create it
        existing_indexes = [index.name for index in self.client.list_indexes()]
        # todo REGION may be wrong

        if collection_name not in existing_indexes:
            # Create a new index with default settings
            self.client.create_index(
                name=collection_name,
                dimension=embeddings_model.embedding_dimension,
                metric="cosine",
                spec={"serverless": {"cloud": self.cloud, "region": self.region}},
            )

        # Create and return the vector store
        return VectorStorePinecone(
            collection_name=collection_name,
            embeddings_model=embeddings_model,
            pinecone_api_key=self.api_key,
        )
