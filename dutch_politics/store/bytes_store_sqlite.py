import os
import re
import sqlite3
import zlib
from contextlib import contextmanager
from typing import Iterator, List, Optional, Sequence, Tuple

from langchain.storage.exceptions import InvalidKeyException

from dutch_politics.store.bytes_store_base import BytesStoreBase


class BytesStoreSqlite(BytesStoreBase):
    def __init__(self, collection_name: str, path_file_database: str) -> None:
        super().__init__(collection_name)
        self.path_file_database = path_file_database
        # Ensure parent directory exists
        abs_path = os.path.abspath(self.path_file_database)
        parent_dir = os.path.dirname(abs_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the SQLite database."""
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS store (
                    key TEXT PRIMARY KEY,
                    value BLOB
                )
            """
            )
            conn.commit()

    @contextmanager
    def _get_connection(self):
        """Get a database connection with proper cleanup."""
        conn = sqlite3.connect(self.path_file_database)
        try:
            yield conn
        finally:
            conn.close()

    def _compress(self, data: bytes) -> bytes:
        """Compress data using zlib."""
        return zlib.compress(data)

    def _decompress(self, data: bytes) -> bytes:
        """Decompress data using zlib."""
        return zlib.decompress(data)

    def _validate_key(self, key: str) -> None:
        """Validate the key to ensure it has valid characters."""
        if not re.match(r"^[a-zA-Z0-9_.\-/]+$", key):
            raise InvalidKeyException(f"Invalid characters in key: {key}")

    def mget(self, keys: Sequence[str]) -> List[Optional[bytes]]:
        """Get the values associated with the given keys.

        Args:
            keys: A sequence of keys.

        Returns:
            A sequence of optional values associated with the keys.
            If a key is not found, the corresponding value will be None.
        """
        values: List[Optional[bytes]] = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for key in keys:
                self._validate_key(key)
                cursor.execute("SELECT value FROM store WHERE key=?", (key,))
                row = cursor.fetchone()
                if row:
                    values.append(self._decompress(row[0]))
                else:
                    values.append(None)
        return values

    def mset(self, key_value_pairs: Sequence[Tuple[str, bytes]]) -> None:
        """Set the values for the given keys.

        Args:
            key_value_pairs: A sequence of key-value pairs.

        Returns:
            None
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for key, value in key_value_pairs:
                self._validate_key(key)
                compressed_value = self._compress(value)
                cursor.execute(
                    "REPLACE INTO store (key, value) VALUES (?, ?)",
                    (key, compressed_value),
                )
            conn.commit()

    def mdelete(self, keys: Sequence[str]) -> None:
        """Delete the given keys and their associated values.

        Args:
            keys (Sequence[str]): A sequence of keys to delete.

        Returns:
            None
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for key in keys:
                self._validate_key(key)
                cursor.execute("DELETE FROM store WHERE key=?", (key,))
            conn.commit()

    def yield_keys(self, prefix: Optional[str] = None) -> Iterator[str]:
        """Get an iterator over keys that match the given prefix.

        Args:
            prefix (Optional[str]): The prefix to match.

        Returns:
            Iterator[str]: An iterator over keys that match the given prefix.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if prefix:
                self._validate_key(prefix)
                cursor.execute(
                    "SELECT key FROM store WHERE key LIKE ?", (f"{prefix}%",)
                )
            else:
                cursor.execute("SELECT key FROM store")
            for row in cursor:
                yield row[0]

    def clear(self) -> None:
        """Clear all data from the store."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM store")
            conn.commit()

    async def asample(self, count: int) -> List[bytes]:
        """Sample a given number of items from the store.

        Args:
            count (int): The number of items to sample.

        Returns:
            List[bytes]: A list of sampled items.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM store ORDER BY RANDOM() LIMIT ?", (count,))
            rows = cursor.fetchall()
            return [self._decompress(row[0]) for row in rows]
