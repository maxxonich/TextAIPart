from sqlalchemy import Column, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class QueryResult(Base):
    __tablename__ = "query_results"
    id = Column(String, primary_key=True, index=True)
    original_text = Column(Text, nullable=False)
    sentiment_audio = Column(Text, nullable=True)
    sentiment_ocr = Column(Text, nullable=True)
    sentiment_comments = Column(Text, nullable=True)
    categories_audio = Column(Text, nullable=True)
    categories_ocr = Column(Text, nullable=True)