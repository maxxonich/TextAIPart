import json


def callback_text_ai(ch, method, properties, body):
    try:
        data = json.loads(body)
        print(data)   # stub
        # TODO:logger.info...
    except Exception as e:
        print(f'error callback_status_change: {e}')
        # TODO: logger.error(f'An error occurred: {e}')
