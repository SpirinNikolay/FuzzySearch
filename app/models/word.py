from sqlalchemy import Column, Integer, String, ForeignKey
from db.database import BaseModel

class Word(BaseModel):
    __tablename__ = "word"

    id = Column(Integer, primary_key=True, autoincrement=True)
    corpus_id = Column(Integer, ForeignKey("corpus.corpus_id"), nullable=False)
    term = Column(String, nullable=False)
