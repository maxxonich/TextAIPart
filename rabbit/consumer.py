from rabbit.rabbitmq import RabbitMQ
from rabbit.callbacks import callback_text_ai

import time, pika


def start_consumer():
    """
    The main loop of connecting consumer to RabbitMQ and waiting for messages.
    If the connection is broken, there will be an attempt to reconnect after 5 seconds.
    """
    while True:
        try:
            rabbit = RabbitMQ()
            rabbit.start_consumer('core_file_status', callback_text_ai)
        except pika.exceptions.AMQPConnectionError:
            print("Error connecting to queue")  # TODO: change print to save log
            time.sleep(5)


if __name__ == '__main__':
    start_consumer()
