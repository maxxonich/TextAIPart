from rabbit.rabbitmq import RabbitMQ
from rabbit.callbacks import callback_text_ai, callback_video_ocr, callback_video_text_extraction
from config import COMMENT_HANDLER_QUEUE, VIDEO_OCR_TEXT_HANDLER_QUEUE, VIDEO_TEXT_EXTRACTION_QUEUE

import time, pika


def start_consumer():
    """
    The main loop of connecting consumer to RabbitMQ and waiting for messages.
    If the connection is broken, there will be an attempt to reconnect after 5 seconds.
    """
    while True:
        try:
            consumers = [
                (COMMENT_HANDLER_QUEUE, callback_text_ai),
                (VIDEO_OCR_TEXT_HANDLER_QUEUE, callback_video_ocr),
                (VIDEO_TEXT_EXTRACTION_QUEUE, callback_video_text_extraction),
            ]
            rabbit = RabbitMQ()
            rabbit.start_multiple_consumers(consumers)
        except pika.exceptions.AMQPConnectionError:
            print("Error connecting to queue")  # TODO: change print to save log
            time.sleep(5)


if __name__ == '__main__':
    start_consumer()
