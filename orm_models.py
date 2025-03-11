from sqlalchemy import Column, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class QueryResult(Base):
    __tablename__ = "query_results"
    ucid = Column(String, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    service = Column(String, nullable=False)
    sentiment = Column(Text, nullable=True)
    category = Column(Text, nullable=True)