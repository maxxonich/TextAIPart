import json
from rabbit.rabbitmq import RabbitMQ


def send_test_message_to_video_exchange(exchange_name='video_event_exchange', message=None):
    message = {'text': 'Hello from test!'} if not message else message
    message_body = json.dumps(message)
    rabbit = RabbitMQ()
    rabbit.send_to_exchange(exchange_name, message)
    print(f"Sent message {message_body} to exchange '{exchange_name}'")


if __name__ == '__main__':
    send_test_message_to_video_exchange()
