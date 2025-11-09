"""Kafka configuration management."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaConfig(BaseSettings):
    """Configuration for Kafka producer and consumer.

    All settings can be configured via environment variables with KAFKA_ prefix.
    """

    model_config = SettingsConfigDict(
        env_prefix="KAFKA_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    ***REMOVED*** Broker Configuration
    bootstrap_servers: str = Field(
        default="kafka:9092", description="Kafka bootstrap servers (comma-separated)"
    )
    security_protocol: str = Field(
        default="PLAINTEXT",
        description="Security protocol (PLAINTEXT, SSL, SASL_PLAINTEXT, SASL_SSL)",
    )

    ***REMOVED*** Producer Configuration
    producer_acks: int = Field(
        default=1, description="Number of acknowledgments (0, 1, or -1 for all)"
    )
    producer_compression_type: str = Field(
        default="snappy", description="Compression type (none, gzip, snappy, lz4, zstd)"
    )
    producer_max_request_size: int = Field(
        default=1048576, description="Maximum size of a request in bytes (1MB)"
    )
    producer_retries: int = Field(default=3, description="Number of retries for failed sends")
    producer_retry_backoff_ms: int = Field(
        default=100, description="Backoff time between retries in milliseconds"
    )
    producer_request_timeout_ms: int = Field(
        default=30000, description="Request timeout in milliseconds"
    )
    producer_linger_ms: int = Field(
        default=10, description="Time to wait before sending batch in milliseconds"
    )
    producer_batch_size: int = Field(default=16384, description="Batch size in bytes")

    ***REMOVED*** Consumer Configuration
    consumer_group_id_prefix: str = Field(
        default="next-watch", description="Prefix for consumer group IDs"
    )
    consumer_auto_offset_reset: str = Field(
        default="earliest", description="Auto offset reset (earliest, latest, none)"
    )
    consumer_enable_auto_commit: bool = Field(
        default=True, description="Enable automatic offset commits"
    )
    consumer_auto_commit_interval_ms: int = Field(
        default=5000, description="Auto commit interval in milliseconds"
    )
    consumer_max_poll_records: int = Field(
        default=500, description="Maximum number of records per poll"
    )
    consumer_max_poll_interval_ms: int = Field(
        default=300000, description="Maximum time between polls in milliseconds"
    )
    consumer_session_timeout_ms: int = Field(
        default=10000, description="Consumer session timeout in milliseconds"
    )
    consumer_heartbeat_interval_ms: int = Field(
        default=3000, description="Heartbeat interval in milliseconds"
    )

    ***REMOVED*** Schema Registry Configuration
    schema_registry_url: str | None = Field(
        default="http://schema-registry:8081",
        description="Schema Registry URL",
        validation_alias="KAFKA_SCHEMA_REGISTRY_URL",
    )
    schema_registry_timeout: int = Field(
        default=30,
        description="Schema Registry request timeout in seconds",
        validation_alias="KAFKA_SCHEMA_REGISTRY_TIMEOUT",
    )
    enable_schema_registry: bool = Field(
        default=False,
        description="Enable Schema Registry integration",
        validation_alias="KAFKA_ENABLE_SCHEMA_REGISTRY",
    )
    check_schema_compatibility: bool = Field(
        default=True,
        description="Check schema compatibility before registration",
        validation_alias="KAFKA_CHECK_SCHEMA_COMPATIBILITY",
    )
    auto_register_schemas: bool = Field(
        default=True,
        description="Automatically register schemas on startup",
        validation_alias="KAFKA_AUTO_REGISTER_SCHEMAS",
    )

    ***REMOVED*** Serialization Configuration
    serialization_format: str = Field(
        default="json",
        description="Message serialization format: json or avro",
        validation_alias="KAFKA_SERIALIZATION_FORMAT",
    )

    ***REMOVED*** Feature Flags
    enable_producer: bool = Field(
        default=True,
        description="Enable Kafka event production",
        validation_alias="ENABLE_KAFKA_PRODUCER",
    )
    enable_consumer: bool = Field(
        default=True,
        description="Enable Kafka event consumption",
        validation_alias="ENABLE_KAFKA_CONSUMER",
    )

    ***REMOVED*** Tracing Configuration
    enable_tracing: bool = Field(default=True, description="Enable OpenTelemetry tracing")

    ***REMOVED*** Dead Letter Queue Configuration
    dlq_topic: str = Field(default="dlq.events", description="Dead letter queue topic name")
    dlq_max_retries: int = Field(default=3, description="Maximum retries before sending to DLQ")

    ***REMOVED*** Topic Configuration
    default_partitions: int = Field(
        default=8, description="Default number of partitions for new topics"
    )
    default_replication_factor: int = Field(
        default=1, description="Default replication factor for new topics"
    )

    @property
    def bootstrap_servers_list(self) -> list[str]:
        """Get bootstrap servers as a list."""
        return [s.strip() for s in self.bootstrap_servers.split(",")]

    @property
    def producer_config(self) -> dict[str, object]:
        """Get producer configuration dictionary for aiokafka."""
        return {
            "bootstrap_servers": self.bootstrap_servers_list,
            "security_protocol": self.security_protocol,
            "acks": self.producer_acks,
            "compression_type": self.producer_compression_type,
            "max_request_size": self.producer_max_request_size,
            "retries": self.producer_retries,
            "retry_backoff_ms": self.producer_retry_backoff_ms,
            "request_timeout_ms": self.producer_request_timeout_ms,
            "linger_ms": self.producer_linger_ms,
            "batch_size": self.producer_batch_size,
        }

    def consumer_config(self, group_id: str) -> dict[str, object]:
        """Get consumer configuration dictionary for aiokafka.

        Args:
            group_id: Consumer group ID (will be prefixed with consumer_group_id_prefix)

        Returns:
            Consumer configuration dictionary
        """
        full_group_id = f"{self.consumer_group_id_prefix}-{group_id}"

        return {
            "bootstrap_servers": self.bootstrap_servers_list,
            "security_protocol": self.security_protocol,
            "group_id": full_group_id,
            "auto_offset_reset": self.consumer_auto_offset_reset,
            "enable_auto_commit": self.consumer_enable_auto_commit,
            "auto_commit_interval_ms": self.consumer_auto_commit_interval_ms,
            "max_poll_records": self.consumer_max_poll_records,
            "max_poll_interval_ms": self.consumer_max_poll_interval_ms,
            "session_timeout_ms": self.consumer_session_timeout_ms,
            "heartbeat_interval_ms": self.consumer_heartbeat_interval_ms,
        }

    def __repr__(self) -> str:
        """String representation hiding sensitive data."""
        return (
            f"KafkaConfig("
            f"bootstrap_servers={self.bootstrap_servers}, "
            f"security_protocol={self.security_protocol}, "
            f"enable_producer={self.enable_producer}, "
            f"enable_consumer={self.enable_consumer}"
            f")"
        )
