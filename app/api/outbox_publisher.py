"""Publish up to 100 pending events, then exit. Run one worker for this lab.

Delivery is at least once: a crash after Kafka confirms but before the database
commit can cause a repeat. Consumers must deduplicate using event_id.
"""

import json
from datetime import datetime, timezone

from confluent_kafka import Producer
from sqlalchemy import select

from .config import get_settings


def send_event(producer, topic, event):
    """Return only after the delivery callback confirms success."""
    results = []

    def on_delivery(error, message):
        results.append((error, message))

    value = {
        "event_id": str(event.event_id),
        "appointment_id": event.appointment_id,
        "event_type": event.event_type,
        "created_at": event.created_at.isoformat(),
        "payload": event.payload,
    }
    producer.produce(
        topic,
        key=str(event.appointment_id),
        value=json.dumps(value),
        on_delivery=on_delivery,
    )
    remaining = producer.flush(timeout=35)
    if remaining or not results:
        raise RuntimeError("Kafka delivery was not confirmed; event remains pending")
    error, message = results[0]
    if error is not None:
        raise RuntimeError(f"Kafka delivery failed: {error}")
    return message.partition(), message.offset()


def publish_next(session_factory, producer, topic):
    # Lazy import keeps database setup out of the Kafka-only delivery helper.
    from .db_models import OutboxEvent

    with session_factory() as session:
        with session.begin():
            event = session.scalars(
                select(OutboxEvent)
                .where(OutboxEvent.published_at.is_(None))
                .order_by(OutboxEvent.created_at, OutboxEvent.event_id)
                .limit(1)
                .with_for_update()
            ).first()
            if event is None:
                return False

            partition, offset = send_event(producer, topic, event)
            # Never mark an event published merely because produce() queued it.
            event.published_at = datetime.now(timezone.utc)
            event_id = str(event.event_id)

        # Report success only after the PostgreSQL transaction commits.
        print(f"Published event {event_id}: partition={partition}, offset={offset}")
        return True


def main():
    from .database import SessionLocal

    settings = get_settings()
    producer = Producer({
        "bootstrap.servers": settings.kafka_bootstrap_servers,
        # Local Docker ports are bound to IPv4 (127.0.0.1), not IPv6 (::1).
        "broker.address.family": "v4",
        "client.id": "medical-outbox-publisher",
        "acks": "all",
        "enable.idempotence": True,
        "message.timeout.ms": 30000,
        # Match the Java console producer's keyed partitioning method.
        "partitioner": "murmur2_random",
    })
    count = 0
    try:
        while count < 100 and publish_next(SessionLocal, producer, settings.kafka_topic):
            count += 1
    except Exception:
        # Stop on an unconfirmed event instead of moving on to later events.
        print("Publisher stopped. Uncommitted events remain pending; retries may duplicate delivery.")
        raise
    print(f"Published {count} event(s).")


if __name__ == "__main__":
    main()
