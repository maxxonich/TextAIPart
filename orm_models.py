from sqlalchemy import Column, String, Text, DateTime, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class QueryResult(Base):
    __tablename__ = "query_results"
    ucid = Column(String, nullable=False)
    service = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    sentiment = Column(Text, nullable=True)
    category = Column(Text, nullable=True)
    ts = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        PrimaryKeyConstraint("ucid", "service"),
    )
