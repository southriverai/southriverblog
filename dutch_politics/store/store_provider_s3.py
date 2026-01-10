import collections
import logging
from typing import List, Type, TypeVar

# fix for collections in boto3 because of moves and six._thread and the old pytz version
collections.Callable = collections.abc.Callable  # type: ignore

import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel

from dutch_politics.store.bytes_store_base import BytesStoreBase
from dutch_politics.store.bytes_store_s3 import BytesStoreS3
from dutch_politics.store.dict_store_base import DictStoreBase
from dutch_politics.store.dict_store_bytes import DictStoreBytes
from dutch_politics.store.object_store_base import ObjectStoreBase
from dutch_politics.store.object_store_nested import ObjectStoreNested
from dutch_politics.store.store_provider_base import StoreProviderBase

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class StoreProviderS3(StoreProviderBase):
    def __init__(
        self,
        database_name: str,
        s3_bucket_connection_string: str,
        initialize: bool = True,
    ) -> None:
    
        self.is_initialized = False
        aws_access_key_id = s3_bucket_connection_string.split(";")[0]
        aws_secret_access_key = s3_bucket_connection_string.split(";")[1]
        region_name = s3_bucket_connection_string.split(";")[2]
        bucket_name = s3_bucket_connection_string.split(";")[3]
        # Convert bucket name to S3-compliant format (lowercase, no underscores)
        bucket_name = bucket_name.lower().replace("_", "-")
        self.bucket_name = bucket_name
        if (
            aws_access_key_id is None
            or aws_secret_access_key is None
            or region_name is None
            or bucket_name is None
        ):
            raise ValueError(
                "Invalid S3 bucket connection string: " + s3_bucket_connection_string
            )
        self.region_name = region_name
        self.client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )
        super().__init__(self.bucket_name)
        print(self.bucket_name)
        if initialize:
            self.initialize()

    def initialize(self) -> None:
        self._ensure_bucket_exists()
        self.is_initialized = True


    def list_bucket_names(self) -> List[str]:
        return [obj["Name"] for obj in self.client.list_buckets()["Buckets"]]

    # def list_collection_names(self) -> List[str]:
    #     return [obj["Key"].split("/")[1] for obj in self.client.list_objects(Bucket=self.bucket_name)["Contents"]]

    def _ensure_bucket_exists(self) -> None:
        # return  # TODO this is a temporary fix to avoid creating the bucket
        """Create the S3 bucket if it doesn't exist."""
        try:
            # Check if bucket exists by trying to get its location
            self.client.head_bucket(Bucket=self.database_name)
            logger.info(f"S3 bucket '{self.database_name}' exists")
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            # head_bucket returns "404" or "NoSuchBucket" when bucket doesn't exist
            if error_code in ["404", "NoSuchBucket"]:
                # Bucket doesn't exist, create it
                logger.info(
                    f"S3 bucket '{self.database_name}' does not exist. Creating in region '{self.region_name}'..."
                )
                try:
                    # Create bucket with LocationConstraint
                    self.client.create_bucket(
                        Bucket=self.database_name,
                        CreateBucketConfiguration={
                            "LocationConstraint": self.region_name
                        },
                    )
                    logger.info(
                        f"Successfully created S3 bucket '{self.database_name}' in region '{self.region_name}'"
                    )
                except ClientError as create_error:
                    logger.error(f"Failed to create S3 bucket: {create_error}")
                    raise
            else:
                # Some other error occurred
                logger.error(f"Error checking S3 bucket: {e}")
                raise

    def _get_bytes_store(self, collection_name: str) -> BytesStoreBase:
        if not self.is_initialized:
            self.initialize()
        print(f"{self.bucket_name}/{collection_name}")
        return BytesStoreS3(collection_name, self.client, self.bucket_name)

    def _get_dict_store(self, collection_name: str) -> DictStoreBase:
        if not self.is_initialized:
            self.initialize()
        return DictStoreBytes(
            BytesStoreS3(collection_name, self.client, self.bucket_name)
        )

    def _get_object_store(
        self, collection_name: str, model_class: Type[T]
    ) -> ObjectStoreBase[T]:
        return ObjectStoreNested(self.get_dict_store(collection_name), model_class)
