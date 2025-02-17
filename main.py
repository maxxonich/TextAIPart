import os
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from openai import AzureOpenAI

# Импорт подключения к БД и моделей
from db import engine, SessionLocal
from orm_models import Base, QueryResult
from models import QueryRequest, QueryResponse

# Загружаем переменные окружения из .env
load_dotenv()

# Инициализация клиента Azure OpenAI
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "REPLACE_WITH_YOUR_DEPLOYMENT_NAME")

# Создаем таблицы в БД, если их ещё нет
Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_or_create_query_result(db, query: QueryRequest):
    """
    Если запись с данным id уже существует, возвращаем её,
    иначе создаем новую запись с исходным текстом.
    """
    record = db.query(QueryResult).filter(QueryResult.id == query.id).first()
    if not record:
        record = QueryResult(id=query.id, original_text=query.text)
        db.add(record)
    else:
        # Если необходимо обновлять исходный текст, можно раскомментировать:
        # record.original_text = query.text
        pass
    return record


@app.post("/sentiment", response_model=QueryResponse)
def sentiment_endpoint(query: QueryRequest):
    prompt = (
        f"Пожалуйста, проанализируй следующий текст и определи его эмоциональную тональность "
        f"(позитивная, негативная или нейтральная):\n\n{query.text}"
    )
    try:
        response = client.completions.create(
            model=deployment_name,
            prompt=prompt,
            max_tokens=50,
            temperature=0.7
        )
        result_text = response.choices[0].text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обращении к Azure OpenAI: {e}")

    db = SessionLocal()
    try:
        record = get_or_create_query_result(db, query)
        record.sentiment = result_text
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при сохранении в базу данных: {e}")
    finally:
        db.close()

    return QueryResponse(id=query.id, result=result_text)


@app.post("/prorussian", response_model=QueryResponse)
def prorussian_endpoint(query: QueryRequest):
    prompt = (
        f"Пожалуйста, проанализируй следующий текст и определи, содержит ли он элементы пророссийской пропаганды:\n\n"
        f"{query.text}"
    )
    try:
        response = client.completions.create(
            model=deployment_name,
            prompt=prompt,
            max_tokens=50,
            temperature=0.7
        )
        result_text = response.choices[0].text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обращении к Azure OpenAI: {e}")

    db = SessionLocal()
    try:
        record = get_or_create_query_result(db, query)
        record.pro_russian_text = result_text
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при сохранении в базу данных: {e}")
    finally:
        db.close()

    return QueryResponse(id=query.id, result=result_text)


@app.post("/categories", response_model=QueryResponse)
def categories_endpoint(query: QueryRequest):
    prompt = (
        f"Пожалуйста, проанализируй следующий текст и выдели основные темы или категории, к которым он относится:\n\n"
        f"{query.text}"
    )
    try:
        response = client.completions.create(
            model=deployment_name,
            prompt=prompt,
            max_tokens=50,
            temperature=0.7
        )
        result_text = response.choices[0].text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обращении к Azure OpenAI: {e}")

    db = SessionLocal()
    try:
        record = get_or_create_query_result(db, query)
        record.categories = result_text
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при сохранении в базу данных: {e}")
    finally:
        db.close()

    return QueryResponse(id=query.id, result=result_text)
