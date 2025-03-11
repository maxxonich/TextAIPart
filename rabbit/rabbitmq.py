import pika
import json
from config import RABBIT_HOST, RABBIT_PORT, RABBIT_USER, RABBIT_PASSWORD


class RabbitMQ:
    """A class to encapsulate RabbitMQ operations with a persistent connection."""
    QUEUE_DECLARE_ARGS = {
        'x-message-ttl': 43200000  # Message Time to Live (TTL) in milliseconds (12 hour)
    }

    def __init__(self):
        """Initialize and create a persistent RabbitMQ connection."""
        self.connection = None
        self.create_connection()

    def create_connection(self):
        """Create a RabbitMQ connection using pika."""
        if not self.connection or self.connection.is_closed:
            print(f'{RABBIT_HOST=} {RABBIT_PORT=} {RABBIT_USER=} {RABBIT_PASSWORD=}')
            parameters = pika.ConnectionParameters(
                host=RABBIT_HOST,
                port=RABBIT_PORT,
                credentials=pika.PlainCredentials(RABBIT_USER, RABBIT_PASSWORD),
                heartbeat=600,
                blocked_connection_timeout=300
            )
            self.connection = pika.BlockingConnection(parameters)

    def send_to_queue(self, queue_name, params):
        """Send a message to a specified RabbitMQ queue."""
        try:
            self.create_connection()  # Ensure connection is alive
            channel = self.connection.channel()
            channel.queue_declare(queue=queue_name, durable=True, arguments=self.QUEUE_DECLARE_ARGS)
            message = json.dumps(params)
            channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=message,
                properties=pika.BasicProperties(delivery_mode=2)
            )
            print(f"Sent {message} to queue {queue_name}")  # TODO: change print to save log
        finally:
            if channel.is_open:
                channel.close()

    def send_to_exchange(self, exchange_name, params):
        """Send a message to a specified RabbitMQ exchange."""
        try:
            self.create_connection()  # Ensure connection is alive
            channel = self.connection.channel()
            channel.exchange_declare(exchange=exchange_name, exchange_type='fanout', durable=True)
            message = json.dumps(params)
            channel.basic_publish(
                exchange=exchange_name,
                routing_key='',
                body=message,
                properties=pika.BasicProperties(delivery_mode=2)
            )
            print(f"Sent {message} to exchange {exchange_name}")  # TODO: change print to save log
        finally:
            if channel.is_open:
                channel.close()

    def start_consumer(self, queue_name, callback):
        """Start a RabbitMQ consumer on a specific queue."""
        self.create_connection()  # Ensure connection is alive
        channel = self.connection.channel()
        channel.queue_declare(queue=queue_name, durable=True, arguments=self.QUEUE_DECLARE_ARGS)
        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        print(f"Starting consumer for queue {queue_name}")  # TODO: change print to save log
        channel.start_consuming()

    def start_multiple_consumers(self, consumers):
        """
        consumers: список кортежей (queue_name, callback)
        Регистрирует несколько очередей и запускает start_consuming() один раз.
        """
        self.create_connection()
        channel = self.connection.channel()
        for queue_name, callback in consumers:
            channel.queue_declare(queue=queue_name, durable=True, arguments=self.QUEUE_DECLARE_ARGS)
            channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
            print(f"Starting consumer for queue {queue_name}")
        channel.start_consuming()

    def close_connection(self):
        """Safely close the RabbitMQ connection."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print("Connection closed")  # TODO: change print to save log
