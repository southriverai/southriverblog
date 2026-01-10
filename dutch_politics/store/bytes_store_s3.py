import logging
from typing import Iterator, List, Optional, Sequence, Tuple, Union

from botocore.exceptions import ClientError

from dutch_politics.store.bytes_store_base import BytesStoreBase

logger = logging.getLogger(__name__)


class BytesStoreS3(BytesStoreBase):
    """S3-based byte store for caching binary data."""

    def __init__(
        self,
        collection_name: str,
        client,
        bucket_name: str,
    ) -> None:
        super().__init__(collection_name)
        """
        Initialize S3 ByteStore.

        Args:
            client: boto3 S3 client
            bucket_name: Name of the S3 bucket
            collection_name: Collection name (used as prefix/folder)
        """
        self.s3_client = client
        self.bucket_name = bucket_name
        self.prefix = collection_name.rstrip("/") + "/" if collection_name else ""

    def _get_key(self, id: str) -> str:
        """Get the full S3 key with prefix."""
        return f"{self.prefix}{id}"


    def mget(self, keys: Sequence[str]) -> List[Optional[bytes]]:
        """Get multiple objects from S3."""
        results = []
        for key in keys:
            try:
                s3_key = self._get_key(key)
                response = self.s3_client.get_object(
                    Bucket=self.bucket_name, Key=s3_key
                )
                results.append(response["Body"].read())
                logger.debug(f"Retrieved object from S3: {s3_key}")
            except ClientError as e:
                if e.response["Error"]["Code"] == "NoSuchKey":
                    logger.debug(f"Object not found in S3: {s3_key}")
                    results.append(None)
                else:
                    logger.error(f"Error retrieving object from S3: {e}")
                    raise
        return results

    def mset(self, key_value_pairs: Sequence[Tuple[str, bytes]]) -> None:
        """Set multiple objects in S3."""
        for key, value in key_value_pairs:
            try:
                s3_key = self._get_key(key)
                self.s3_client.put_object(
                    Bucket=self.bucket_name, Key=s3_key, Body=value
                )
                logger.debug(f"Stored object in S3: {s3_key}")
            except ClientError as e:
                logger.error(f"Error storing object in S3: {e}")
                raise

    def mdelete(self, keys: Sequence[str]) -> None:
        """Delete multiple objects from S3."""
        for key in keys:
            try:
                s3_key = self._get_key(key)
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
                logger.debug(f"Deleted object from S3: {s3_key}")
            except ClientError as e:
                logger.error(f"Error deleting object from S3: {e}")
                raise

    def yield_keys(
        self, *, prefix: Optional[str] = None
    ) -> Union[Iterator[str], Iterator[str]]:
        """Yield all keys in the S3 bucket with the given prefix."""
        try:
            search_prefix = self._get_key(prefix) if prefix else self.prefix
            paginator = self.s3_client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=self.bucket_name, Prefix=search_prefix)

            for page in pages:
                if "Contents" in page:
                    for obj in page["Contents"]:
                        key = obj["Key"]
                        # Remove the prefix to get the ID
                        if key.startswith(self.prefix):
                            id = key[len(self.prefix) :]
                            yield id
        except ClientError as e:
            logger.error(f"Error yielding objects in S3: {e}")
            raise

    async def asample(self, count: int) -> List[bytes]:
        raise NotImplementedError("Not implemented")
