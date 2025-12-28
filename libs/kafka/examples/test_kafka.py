"""Quick sanity check for the `libs/kafka` client tools.

Usage (from repo root, with an environment where `kafka` is importable):

    python libs/kafka/examples/test_kafka.py
"""

import asyncio

from kafka.cli_tools import KafkaClITools


async def quick_test():
    tools = KafkaClITools()

    ***REMOVED*** List topics
    topics = await tools.list_topics()
    print(f"✅ Connected to Kafka! Topics: {topics}")

    ***REMOVED*** Send test event
    await tools.send_test_event(topic="user.events", event_data={"test": "Hello from Kafka!"})
    print("✅ Test event sent!")

    ***REMOVED*** Read it back
    events = await tools.consume_events("user.events", count=1, from_beginning=True)
    print(f"✅ Received: {events[0]['value']}")


asyncio.run(quick_test())
