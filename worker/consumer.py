# worker/consumer.py
import pika
import os
import json

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "keanghour")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "Hour@1234")
QUEUE_NAME = "test_queue"  # Example
VHOST = f"/{RABBITMQ_USER}"

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
parameters = pika.ConnectionParameters(
    host=RABBITMQ_HOST,
    port=RABBITMQ_PORT,
    virtual_host=VHOST,
    credentials=credentials
)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

def callback(ch, method, properties, body):
    print(f"Received message: {json.loads(body)}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
print(f"Waiting for messages on queue '{QUEUE_NAME}' in vhost '{VHOST}'...")
channel.start_consuming()