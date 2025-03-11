import json
from rabbit.rabbitmq import RabbitMQ


def send_test_message_to_video_exchange(exchange_name='video_event_exchange', message=None):
    message = {
        "ucid": "62818a83bda9ce491d3dc9711d61180343f997d99fa5c437ac84e39325fddc02",
        "videoId": {
            "file_name": "@hatiii/7447942960404040966.mp4"
        }
    } if not message else message
    message_body = json.dumps(message)
    rabbit = RabbitMQ()
    rabbit.send_to_exchange(exchange_name, message)
    print(f"Sent message {message_body} to exchange '{exchange_name}'")


if __name__ == '__main__':
    send_test_message_to_video_exchange()
