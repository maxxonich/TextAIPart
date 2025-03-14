import json
import logging
import requests
from fastapi import HTTPException
from rabbit.rabbitmq import RabbitMQ
from db import engine, SessionLocal
from orm_models import Base, QueryResult
from models import QueryRequest, QueryResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logger.error(f"Ollama server error: {e}")
        raise HTTPException(status_code=500, detail=f"Ollama server error: {e}")

def get_or_create_query_result(db, ucid, service, text):
    """
    If a record with the given ucid and service already exists, return it.
    Otherwise, create a new record with the provided ucid, text, and service.
    """
    record = db.query(QueryResult).filter(
        QueryResult.ucid == ucid, QueryResult.service == service
    ).first()
    if not record:
        # Skip processing if text is empty or contains only whitespace
        if not text or not text.strip():
            logger.warning(f"Empty or whitespace text received for UCID: {ucid} with service: {service}. Skipping processing.")
            return None

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
        db.commit()
    return record

def callback_text_ai(ch, method, properties, body):
    try:
        data = json.loads(body)
        logger.info(f"Received data in callback_text_ai: {data}")
        ucid = data.get('UCID')
        video_id = data.get('VideoId', {})
        file_path = video_id.get('file_name', '')
        logger.info(f"UCID: {ucid}, File Path: {file_path}")
    except Exception as e:
        logger.error(f"Error in callback_text_ai: {e}")

def callback_video_ocr(ch, method, properties, body):
    db = SessionLocal()
    try:
        data = json.loads(body)
        logger.info(f"Received data in callback_video_ocr: {data}")
        ucid = data.get('UCID')
        text = data.get('text', '')
        service = 'video_ocr'
        logger.info(f"Processing UCID: {ucid}, Service: {service}")

        # Skip processing if text is empty or contains only whitespace
        if not text or not text.strip():
            logger.warning(f"Empty or whitespace text received in callback_video_ocr for UCID: {ucid}. Skipping processing.")
            return

        record = get_or_create_query_result(db, ucid, service, text)
        if record is None:
            logger.warning(f"Record not created for UCID: {ucid} in callback_video_ocr due to empty text.")
            return

        message = {
            "UCID": ucid,
            "sentiment": record.sentiment,
            "category": record.category,
            "service": service,
        }
        logger.info(f"Sending message from callback_video_ocr: {message}")
        rabbit = RabbitMQ()
        rabbit.send_to_queue("text_ai_to_analyze", message)
    except Exception as e:
        logger.error(f"Error in callback_video_ocr: {e}")
    finally:
        db.close()

def callback_video_text_extraction(ch, method, properties, body):
    db = SessionLocal()
    try:
        data = json.loads(body)
        logger.info(f"Received data in callback_video_text_extraction: {data}")
        ucid = data.get('UCID')
        text = data.get('text', '')
        service = 'video_text_extraction'
        logger.info(f"Processing UCID: {ucid}, Service: {service}")

        # Skip processing if text is empty or contains only whitespace
        if not text or not text.strip():
            logger.warning(f"Empty or whitespace text received in callback_video_text_extraction for UCID: {ucid}. Skipping processing.")
            return

        record = get_or_create_query_result(db, ucid, service, text)
        if record is None:
            logger.warning(f"Record not created for UCID: {ucid} in callback_video_text_extraction due to empty text.")
            return

        message = {
            "UCID": ucid,
            "sentiment": record.sentiment,
            "category": record.category,
            "service": service,
        }
        logger.info(f"Sending message from callback_video_text_extraction: {message}")
        rabbit = RabbitMQ()
        rabbit.send_to_queue("text_ai_to_analyze", message)
    except Exception as e:
        logger.error(f"Error in callback_video_text_extraction: {e}")
    finally:
        db.close()
