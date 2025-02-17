from sqlalchemy import Column, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class QueryResult(Base):
    __tablename__ = "query_results"
    id = Column(String, primary_key=True, index=True)
    original_text = Column(Text, nullable=False)
    sentiment = Column(Text, nullable=True)
    pro_russian_text = Column(Text, nullable=True)
    categories = Column(Text, nullable=True)
