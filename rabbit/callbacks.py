import json


def callback_text_ai(ch, method, properties, body):
    try:
        data = json.loads(body)
        print(data)   # stub
        # TODO:logger.info...
        ucid = data['ucid']
        file_path = data['videoId']['file_name']
        print(ucid, file_path)
    except Exception as e:
        print(f'error callback_status_change: {e}')
        # TODO: logger.error(f'An error occurred: {e}')


def callback_video_ocr(ch, method, properties, body):
    try:
        data = json.loads(body)
        print(data)   # stub
        # TODO:logger.info...
        ucid = data['ucid']
        text = data['text']
        service = 'video_ocr'
        print(ucid, text)
    except Exception as e:
        print(f'error callback_status_change: {e}')
        # TODO: logger.error(f'An error occurred: {e}')


def callback_video_text_extraction(ch, method, properties, body):
    try:
        data = json.loads(body)
        print(data)   # stub
        # TODO:logger.info...
        ucid = data['ucid']
        text = data['text']
        service = 'video_text_extraction'
        print(ucid, text)
    except Exception as e:
        print(f'error callback_status_change: {e}')
        # TODO: logger.error(f'An error occurred: {e}')
