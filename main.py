import os
import requests
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from openai import AzureOpenAI

# Import database engine and models
from db import engine, SessionLocal
from orm_models import Base, QueryResult
from models import QueryRequest, QueryResponse  # Assumes QueryRequest includes fields: ucid, text, service

# Load environment variables from .env
load_dotenv()

# Initialize the Azure OpenAI client
#client = AzureOpenAI(
#    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
#    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
#    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
#)

#eployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "REPLACE_WITH_YOUR_DEPLOYMENT_NAME")
ollama_url = "http://40.113.50.250:8080/llama/api/generate"  # Ollama local API
# Create database tables if they do not exist yet
Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_or_create_query_result(db, query: QueryRequest):
    """
    If a record with the given ucid and service already exists, return it.
    Otherwise, create a new record with the provided ucid, text, and service.
    """
    record = db.query(QueryResult).filter(
        QueryResult.ucid == query.ucid,
        QueryResult.service == query.service
    ).first()
    if not record:
        record = QueryResult(ucid=query.ucid, text=query.text, service=query.service)
        db.add(record)
    return record





#def query_azure(prompt: str) -> str:
#    """
#    Sends a prompt to Azure OpenAI and returns the result.
#    """
#    try:
#        response = client.completions.create(
#            model=deployment_name,
#            prompt=prompt,
#            max_tokens=100,
#            temperature=0.7
#        )
#        return response.choices[0].text.strip()
#    except Exception as e:
#        raise HTTPException(status_code=500, detail=f"Azure OpenAI error: {e}")


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


@app.post("/sentiment", response_model=QueryResponse)
def sentiment_endpoint(query: QueryRequest, model: str = "azure"):
    """
    Performs sentiment analysis on the text.
    If the 'model' parameter is set to "llama", the local Ollama server is used,
    otherwise Azure OpenAI is used.
    """
    # Check if the text is empty or contains only whitespace
    if not query.text or not query.text.strip():
        raise HTTPException(status_code=400, detail="Input text is empty or whitespace.")

    prompt = (
        "Please determine the emotional tone of the text (positive, negative, or neutral). "
        "Answer strictly with a single number without any explanations:\n"
        "-1 for negative\n"
        "0 for neutral\n"
        "1 for positive\n\n"
        f"Text:\n{query.text}\n\n"
        "Answer:"
    )

    result_text = query_ollama(prompt)  # if model == "llama" else query_azure(prompt)

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

    return QueryResponse(ucid=query.ucid, result=result_text)


@app.post("/categories", response_model=QueryResponse)
def categories_endpoint(query: QueryRequest, model: str = "azure"):
    """
    Performs category classification on the text.
    If the 'model' parameter is set to "llama", the local Ollama server is used,
    otherwise Azure OpenAI is used.
    """
    # Check if the text is empty or contains only whitespace
    if not query.text or not query.text.strip():
        raise HTTPException(status_code=400, detail="Input text is empty or whitespace.")

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

    result_text = query_ollama(prompt)  # if model == "llama" else query_azure(prompt)

    db = SessionLocal()
    try:
        record = get_or_create_query_result(db, query)
        record.category = result_text
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database save error: {e}")
    finally:
        db.close()

    return QueryResponse(ucid=query.ucid, result=result_text)

