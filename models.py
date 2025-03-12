from pydantic import BaseModel


class QueryRequest(BaseModel):
    ucid: str
    text: str
    service: str


class QueryResponse(BaseModel):
    ucid: str
    result: str
