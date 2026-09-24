import json

from confluent_kafka import Consumer

from .config import get_settings


def main():
    settings = get_settings()

    consumer = Consumer({
        "bootstrap.servers": settings.kafka_bootstrap_servers,
        "group.id": settings.kafka_consumer_group,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
        "broker.address.family": "v4",
    })
    
    consumer.subscribe([settings.kafka_topic])
    
    try:
        while True:
            message = consumer.poll(timeout=1.0)

            if message is None:
                continue

            if message.error():
                raise RuntimeError(f"Kafka error: {message.error()}")

            event = json.loads(message.value().decode("utf-8"))

            print(
                f"Received event {event.get('event_id', 'unknown')}: "
                f"type={event.get('event_type', 'unknown')}, "
                f"partition={message.partition()}, "
                f"offset={message.offset()}",
                flush=True,
            )

            consumer.commit(message=message, asynchronous=False)
    except KeyboardInterrupt:
        print("\nStopping consumer...")
    finally:
        consumer.close()
        
        
if __name__ == "__main__":
    main()        