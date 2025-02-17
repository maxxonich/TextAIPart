from pydantic import BaseModel


class QueryRequest(BaseModel):
    id: str
    text: str


class QueryResponse(BaseModel):
    id: str
    result: str
