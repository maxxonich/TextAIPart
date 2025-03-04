from dotenv import load_dotenv
import os


load_dotenv()

RABBIT_HOST = os.environ.get('RABBIT_HOST')
RABBIT_PORT = os.environ.get('RABBIT_PORT')
RABBIT_USER = os.environ.get('RABBIT_USER')
RABBIT_PASSWORD = os.environ.get('RABBIT_PASSWORD')
COMMENT_HANDLER_QUEUE = os.environ.get('COMMENT_HANDLER_QUEUE')
