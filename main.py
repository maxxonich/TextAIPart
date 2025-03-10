import os
import requests
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from openai import AzureOpenAI

# Database connection and models import
from db import engine, SessionLocal
from orm_models import Base, QueryResult
from models import QueryRequest, QueryResponse

# Load environment variables from .env
load_dotenv()

# Initialize the Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "REPLACE_WITH_YOUR_DEPLOYMENT_NAME")
ollama_url = "http://localhost:11434/api/generate"  # Ollama local API

# Create database tables if they do not exist yet
Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_or_create_query_result(db, query: QueryRequest):
    """
    If a record with the given ID already exists, return it.
    Otherwise, create a new record with the original text.
    """
    record = db.query(QueryResult).filter(QueryResult.id == query.id).first()
    if not record:
        record = QueryResult(id=query.id, original_text=query.text)
        db.add(record)
    return record


def query_azure(prompt: str) -> str:
    """
    Sends a prompt to Azure OpenAI and returns the response.
    """
    try:
        response = client.completions.create(
            model=deployment_name,
            prompt=prompt,
            max_tokens=100,
            temperature=0.7
        )
        return response.choices[0].text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Azure OpenAI error: {e}")


def query_ollama(prompt: str) -> str:
    """
    Sends a prompt to the local Ollama server and returns the response.
    """
    try:
        response = requests.post(ollama_url, json={"model": "llama3.1", "prompt": prompt, "stream": False})
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ollama server error: {e}")


@app.post("/sentiment", response_model=QueryResponse)
def sentiment_endpoint(query: QueryRequest, model: str = "azure"):
    """
    Sentiment analysis. If `model="llama"`, it uses the local Ollama server.
    Otherwise, it defaults to Azure OpenAI.
    """
    prompt = (
        "Please determine the emotional tone of the text (positive, negative, or neutral). "
        "Answer strictly with a single number without any explanations:\n"
        "-1 for negative\n"
        "0 for neutral\n"
        "1 for positive\n\n"
        f"Text:\n{query.text}\n\n"
        "Answer:"
    )

    result_text = query_ollama(prompt) if model == "llama" else query_azure(prompt)

    db = SessionLocal()
    try:
        record = get_or_create_query_result(db, query)
        record.sentiment = result_text
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database save error: {e}")
    finally:
        db.close()

    return QueryResponse(id=query.id, result=result_text)


@app.post("/categories", response_model=QueryResponse)
def categories_endpoint(query: QueryRequest, model: str = "azure"):
    """
    Category classification. If `model="llama"`, it uses the local Ollama server.
    Otherwise, it defaults to Azure OpenAI.
    """
    prompt = (
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
        f"Text:\n{query.text}\n\n"
        "Answer:"
    )

    result_text = query_ollama(prompt) if model == "llama" else query_azure(prompt)

    db = SessionLocal()
    try:
        record = get_or_create_query_result(db, query)
        record.categories = result_text
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database save error: {e}")
    finally:
        db.close()

    return QueryResponse(id=query.id, result=result_text)

