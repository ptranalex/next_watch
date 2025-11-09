"""Schema Registry client for managing Avro schemas."""

import json
from typing import Any

import httpx
import structlog

from kafka.config import KafkaConfig
from kafka.schemas.avro_schemas import AVRO_SCHEMAS

logger = structlog.get_logger(__name__)


class SchemaRegistryClient:
    """Async client for Confluent Schema Registry.

    Features:
    - Register and retrieve Avro schemas
    - Check schema compatibility
    - Cache schemas to reduce Registry calls
    - Automatic registration of all event schemas

    Example:
        >>> config = KafkaConfig()
        >>> client = SchemaRegistryClient(config)
        >>> await client.start()
        >>>
        >>> ***REMOVED*** Register a schema
        >>> schema_id = await client.register_schema("user.activity-value", schema_dict)
        >>>
        >>> ***REMOVED*** Get latest schema
        >>> schema = await client.get_latest_schema("user.activity-value")
        >>>
        >>> await client.close()
    """

    def __init__(self, config: KafkaConfig):
        """Initialize Schema Registry client.

        Args:
            config: Kafka configuration containing Schema Registry URL
        """
        self.config = config
        self.base_url = (config.schema_registry_url or "").rstrip("/")
        self._client: httpx.AsyncClient | None = None
        self._schema_cache: dict[int, dict[str, Any]] = {}
        self._subject_cache: dict[str, int] = {}
        self.logger = logger.bind(component="schema_registry")

    async def start(self) -> None:
        """Start the Schema Registry client."""
        if self._client:
            self.logger.warning("Schema Registry client already started")
            return

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.config.schema_registry_timeout,
            headers={"Content-Type": "application/vnd.schemaregistry.v1+json"},
        )
        self.logger.info("Schema Registry client started", url=self.base_url)

    async def close(self) -> None:
        """Close the Schema Registry client."""
        if self._client:
            await self._client.aclose()
            self._client = None
            self.logger.info("Schema Registry client closed")

    async def register_schema(self, subject: str, schema: dict[str, Any]) -> int:
        """Register a schema with the Schema Registry.

        Args:
            subject: Subject name (e.g., "user.activity-value")
            schema: Avro schema as dictionary

        Returns:
            Schema ID assigned by the Registry

        Raises:
            httpx.HTTPStatusError: If registration fails
        """
        if not self._client:
            raise RuntimeError("Schema Registry client not started")

        ***REMOVED*** Check cache first
        cache_key = f"{subject}:{json.dumps(schema, sort_keys=True)}"
        if cache_key in self._subject_cache:
            return self._subject_cache[cache_key]

        payload = {"schema": json.dumps(schema)}

        try:
            response = await self._client.post(
                f"/subjects/{subject}/versions",
                json=payload,
            )
            response.raise_for_status()

            data = response.json()
            schema_id = data["id"]

            ***REMOVED*** Cache the schema
            self._schema_cache[schema_id] = schema
            self._subject_cache[cache_key] = schema_id

            self.logger.info(
                "Schema registered",
                subject=subject,
                schema_id=schema_id,
                schema_name=schema.get("name"),
            )

            return schema_id

        except httpx.HTTPStatusError as e:
            self.logger.error(
                "Failed to register schema",
                subject=subject,
                status_code=e.response.status_code,
                error=e.response.text,
            )
            raise

    async def get_schema(self, schema_id: int) -> dict[str, Any]:
        """Get a schema by ID.

        Args:
            schema_id: Schema ID

        Returns:
            Avro schema as dictionary

        Raises:
            httpx.HTTPStatusError: If schema not found
        """
        if not self._client:
            raise RuntimeError("Schema Registry client not started")

        ***REMOVED*** Check cache first
        if schema_id in self._schema_cache:
            return self._schema_cache[schema_id]

        try:
            response = await self._client.get(f"/schemas/ids/{schema_id}")
            response.raise_for_status()

            data = response.json()
            schema = json.loads(data["schema"])

            ***REMOVED*** Cache the schema
            self._schema_cache[schema_id] = schema

            return schema

        except httpx.HTTPStatusError as e:
            self.logger.error(
                "Failed to get schema",
                schema_id=schema_id,
                status_code=e.response.status_code,
                error=e.response.text,
            )
            raise

    async def get_latest_schema(self, subject: str) -> dict[str, Any]:
        """Get the latest version of a schema for a subject.

        Args:
            subject: Subject name

        Returns:
            Avro schema as dictionary

        Raises:
            httpx.HTTPStatusError: If subject not found
        """
        if not self._client:
            raise RuntimeError("Schema Registry client not started")

        try:
            response = await self._client.get(f"/subjects/{subject}/versions/latest")
            response.raise_for_status()

            data = response.json()
            schema = json.loads(data["schema"])
            schema_id = data["id"]

            ***REMOVED*** Cache the schema
            self._schema_cache[schema_id] = schema

            return schema

        except httpx.HTTPStatusError as e:
            self.logger.error(
                "Failed to get latest schema",
                subject=subject,
                status_code=e.response.status_code,
                error=e.response.text,
            )
            raise

    async def check_compatibility(self, subject: str, schema: dict[str, Any]) -> bool:
        """Check if a schema is compatible with the latest version.

        Args:
            subject: Subject name
            schema: Avro schema to check

        Returns:
            True if compatible, False otherwise
        """
        if not self._client:
            raise RuntimeError("Schema Registry client not started")

        if not self.config.check_schema_compatibility:
            return True

        payload = {"schema": json.dumps(schema)}

        try:
            response = await self._client.post(
                f"/compatibility/subjects/{subject}/versions/latest",
                json=payload,
            )
            response.raise_for_status()

            data = response.json()
            is_compatible = data.get("is_compatible", False)

            self.logger.info(
                "Schema compatibility checked",
                subject=subject,
                compatible=is_compatible,
            )

            return is_compatible

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                ***REMOVED*** No existing version, so this is the first - compatible by definition
                return True

            self.logger.error(
                "Failed to check compatibility",
                subject=subject,
                status_code=e.response.status_code,
                error=e.response.text,
            )
            return False

    async def register_all_event_schemas(self) -> dict[str, int]:
        """Register all event schemas defined in AVRO_SCHEMAS.

        Returns:
            Dictionary mapping event types to schema IDs

        Raises:
            RuntimeError: If auto-registration is disabled
        """
        if not self.config.auto_register_schemas:
            raise RuntimeError("Auto-registration of schemas is disabled")

        schema_ids = {}

        for event_type, schema in AVRO_SCHEMAS.items():
            ***REMOVED*** Use -value suffix for value schemas (Confluent convention)
            subject = f"{event_type}-value"

            try:
                ***REMOVED*** Check compatibility before registering
                if await self.check_compatibility(subject, schema):
                    schema_id = await self.register_schema(subject, schema)
                    schema_ids[event_type] = schema_id
                else:
                    self.logger.warning(
                        "Schema incompatible with existing version, skipping registration",
                        event_type=event_type,
                        subject=subject,
                    )

            except Exception as e:
                self.logger.error(
                    "Failed to register schema for event type",
                    event_type=event_type,
                    error=str(e),
                    exc_info=True,
                )
                ***REMOVED*** Continue with other schemas

        self.logger.info(
            "Registered event schemas",
            count=len(schema_ids),
            event_types=list(schema_ids.keys()),
        )

        return schema_ids

    async def list_subjects(self) -> list[str]:
        """List all registered subjects.

        Returns:
            List of subject names
        """
        if not self._client:
            raise RuntimeError("Schema Registry client not started")

        try:
            response = await self._client.get("/subjects")
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            self.logger.error(
                "Failed to list subjects",
                status_code=e.response.status_code,
                error=e.response.text,
            )
            raise

    async def delete_subject(self, subject: str) -> list[int]:
        """Delete a subject and all its versions.

        Args:
            subject: Subject name to delete

        Returns:
            List of deleted version numbers

        Warning:
            This is a destructive operation. Use with caution.
        """
        if not self._client:
            raise RuntimeError("Schema Registry client not started")

        try:
            response = await self._client.delete(f"/subjects/{subject}")
            response.raise_for_status()

            versions = response.json()

            self.logger.warning(
                "Subject deleted",
                subject=subject,
                versions_deleted=len(versions),
            )

            return versions

        except httpx.HTTPStatusError as e:
            self.logger.error(
                "Failed to delete subject",
                subject=subject,
                status_code=e.response.status_code,
                error=e.response.text,
            )
            raise
