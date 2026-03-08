import os
import pika
import json
from app.middleware.custom_exceptions import QueueError

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "keanghour")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "Hour@1234")
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/keanghour")


def get_connection():
    """Connect to RabbitMQ using credentials and vhost from .env"""
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host=RABBITMQ_VHOST,
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300,
    )
    try:
        return pika.BlockingConnection(parameters)
    except Exception as e:
        raise QueueError(f"Cannot connect to RabbitMQ: {str(e)}")


def check_queue_exists(channel, queue_name: str) -> bool:
    """Check if a queue exists without creating it"""
    try:
        channel.queue_declare(queue=queue_name, passive=True)
        return True
    except pika.exceptions.ChannelClosedByBroker as e:
        if e.reply_code == 404:
            return False
        raise
    except Exception as e:
        raise QueueError(f"Failed to check queue existence: {str(e)}")


def publish(queue_name: str, message: list):
    """Publish messages to an existing queue"""
    if not queue_name:
        raise QueueError("Queue name cannot be empty")
    if not message or not isinstance(message, list):
        raise QueueError("Message must be a non-empty list of dicts")

    try:
        connection = get_connection()
        channel = connection.channel()

        if not check_queue_exists(channel, queue_name):
            raise QueueError(f"Queue '{queue_name}' does not exist in vhost '{RABBITMQ_VHOST}'")

        for msg in message:
            channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(msg),
                properties=pika.BasicProperties(delivery_mode=2)  # persistent
            )

        connection.close()
    except QueueError:
        raise
    except Exception as e:
        raise QueueError(f"Failed to publish message: {str(e)}")