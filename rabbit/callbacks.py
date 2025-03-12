import json
from db import engine, SessionLocal
from orm_models import Base, QueryResult
from models import QueryRequest, QueryResponse
import requests

prompt_sentiment = (
    "Please determine the emotional tone of the text (positive, negative, or neutral). "
    "Answer strictly with a single number without any explanations:\n"
    "-1 for negative\n"
    "0 for neutral\n"
    "1 for positive\n\n"
    "Text:\n{}\n\n"
    "Answer:"
)

prompt_category = (
    "Identify which of the following possible categories best fits this text:\n\n"
    "1) Politics\n"
    "2) Technology\n"
    "3) Entertainment\n"
    "4) Sports\n"
    "5) Science\n"
    "6) Health\n"
    "7) Ecology\n"
    "8) Finance\n"
    "9) Cars\n"
    "10) Other\n\n"
    "You can select multiple categories (up to three) if it is really justified. "
    "If you are unsure, select 'Other'.\n\n"
    "Return the result strictly in JSON array format (for example: [\"Technology\"] or [\"Sports\",\"Health\"]). "
    "Do not add any additional text.\n\n"
    "Text:\n{}\n\n"
    "Answer:"
)

ollama_url = "http://40.113.50.250:8080/llama/api/generate"

def query_ollama(prompt: str) -> str:
    """
    Sends a prompt to the local Ollama server and returns the result.
    """
    try:
        response = requests.post(ollama_url, json={"model": "llama3.1", "prompt": prompt, "stream": False})
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ollama server error: {e}")

def get_or_create_query_result(db, ucid, service, text):
    """
    If a record with the given ucid already exists, return it.
    Otherwise, create a new record with the provided ucid, text, and service.
    """
    record = db.query(QueryResult).filter(
        QueryResult.ucid == ucid, QueryResult.service == service
    ).first()
    if not record:
        sentiment = query_ollama(prompt_sentiment.format(text))
        category = query_ollama(prompt_category.format(text))
        record = QueryResult(
            ucid=ucid,
            text=text,
            service=service,
            sentiment=sentiment,
            category=category
        )
        db.add(record)
    return record



def callback_text_ai(ch, method, properties, body):
    try:
        data = json.loads(body)
        print(data)   # stub
        # TODO:logger.info...
        ucid = data['UCID']
        file_path = data['VideoId']['file_name']
        print(ucid, file_path)

    except Exception as e:
        print(f'error callback_text_ai: {e}')
        # TODO: logger.error(f'An error occurred: {e}')


def callback_video_ocr(ch, method, properties, body):
    try:
        db = SessionLocal()
        data = json.loads(body)
        print(data)   # stub
        # TODO:logger.info...
        ucid = data['UCID']
        text = data['text']
        service = 'video_ocr'
        print(ucid, text, service)

        record = get_or_create_query_result(db, ucid, service, text)

        message = {
            "UCID": ucid,
            "sentiment": record.sentiment,
            "category": record.category,
            "service": service,
        }
        print(message)
        message_json = json.dumps(message)
        rabbit = RabbitMQ()
        rabbit.send_to_queue("text_ai_to_analyze", message_json)

    except Exception as e:
        print(f'error callback_video_ocr: {e}')
        # TODO: logger.error(f'An error occurred: {e}')


def callback_video_text_extraction(ch, method, properties, body):
    try:
        db = SessionLocal()
        data = json.loads(body)
        print(data)   # stub
        # TODO:logger.info...
        ucid = data['UCID']
        text = data['text']
        service = 'video_text_extraction'
        print(ucid, text, service)

        record = get_or_create_query_result(db, ucid, service, text)

        message = {
            "UCID": ucid,
            "sentiment": record.sentiment,
            "category": record.category,
            "service": service,
        }
        print(message)
        message_json = json.dumps(message)
        rabbit = RabbitMQ()
        rabbit.send_to_queue("text_ai_to_analyze", message_json)

    except Exception as e:
        print(f'error callback_video_text_extraction: {e}')
        # TODO: logger.error(f'An error occurred: {e}')
