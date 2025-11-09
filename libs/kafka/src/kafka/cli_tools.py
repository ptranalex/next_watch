"""CLI tools for Kafka management."""

import asyncio
import json

import structlog
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.admin import AIOKafkaAdminClient, NewTopic

from kafka.config import KafkaConfig

logger = structlog.get_logger(__name__)


class KafkaClITools:
    """CLI tools for Kafka topic and consumer management."""

    def __init__(self, config: KafkaConfig | None = None):
        """Initialize CLI tools."""
        self.config = config or KafkaConfig()

    async def list_topics(self) -> list[str]:
        """List all Kafka topics."""
        admin_client = AIOKafkaAdminClient(bootstrap_servers=self.config.bootstrap_servers_list)

        try:
            await admin_client.start()
            topics = await admin_client.list_topics()
            return sorted(topics)
        finally:
            await admin_client.close()

    async def create_topic(
        self,
        name: str,
        partitions: int = 8,
        replication_factor: int = 1,
    ) -> None:
        """Create a new Kafka topic."""
        admin_client = AIOKafkaAdminClient(bootstrap_servers=self.config.bootstrap_servers_list)

        try:
            await admin_client.start()

            topic = NewTopic(
                name=name, num_partitions=partitions, replication_factor=replication_factor
            )

            await admin_client.create_topics([topic])
            logger.info(
                "Topic created",
                name=name,
                partitions=partitions,
                replication_factor=replication_factor,
            )
        finally:
            await admin_client.close()

    async def describe_topic(self, name: str) -> dict:
        """Get detailed information about a topic."""
        admin_client = AIOKafkaAdminClient(bootstrap_servers=self.config.bootstrap_servers_list)

        try:
            await admin_client.start()
            metadata = await admin_client.describe_topics([name])
            return metadata
        finally:
            await admin_client.close()

    async def get_consumer_lag(self, group_id: str) -> dict:
        """Get consumer lag for a consumer group."""
        admin_client = AIOKafkaAdminClient(bootstrap_servers=self.config.bootstrap_servers_list)

        try:
            await admin_client.start()
            ***REMOVED*** Get consumer group offsets
            offsets = await admin_client.list_consumer_group_offsets(group_id)
            return offsets
        finally:
            await admin_client.close()

    async def send_test_event(
        self,
        topic: str,
        event_data: dict,
        key: str | None = None,
    ) -> None:
        """Send a test event to a topic."""
        producer = AIOKafkaProducer(
            **self.config.producer_config,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
        )

        try:
            await producer.start()
            await producer.send(topic=topic, value=event_data, key=key)
            logger.info("Test event sent", topic=topic, key=key)
        finally:
            await producer.stop()

    async def consume_events(
        self,
        topic: str,
        count: int = 10,
        from_beginning: bool = True,
    ) -> list[dict]:
        """Consume events from a topic for testing."""
        consumer_config = self.config.consumer_config("cli-test")
        if from_beginning:
            consumer_config["auto_offset_reset"] = "earliest"

        consumer = AIOKafkaConsumer(
            topic,
            **consumer_config,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        )

        events = []
        try:
            await consumer.start()

            async for message in consumer:
                events.append(
                    {
                        "offset": message.offset,
                        "key": message.key.decode("utf-8") if message.key else None,
                        "value": message.value,
                        "timestamp": message.timestamp,
                    }
                )

                if len(events) >= count:
                    break

        finally:
            await consumer.stop()

        return events

    async def reset_consumer_group(
        self,
        group_id: str,
        topic: str,
        offset: str = "earliest",
    ) -> None:
        """Reset consumer group offset for a topic."""
        admin_client = AIOKafkaAdminClient(bootstrap_servers=self.config.bootstrap_servers_list)

        try:
            await admin_client.start()
            ***REMOVED*** Implementation depends on specific reset strategy
            logger.info(
                "Resetting consumer group",
                group_id=group_id,
                topic=topic,
                offset=offset,
            )
            ***REMOVED*** Note: Full implementation would use admin_client.alter_consumer_group_offsets
        finally:
            await admin_client.close()


async def main() -> None:
    """Example CLI usage."""
    tools = KafkaClITools()

    ***REMOVED*** List topics
    topics = await tools.list_topics()
    print(f"Topics: {topics}")

    ***REMOVED*** Describe a topic
    if topics:
        info = await tools.describe_topic(topics[0])
        print(f"Topic info: {json.dumps(info, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())
