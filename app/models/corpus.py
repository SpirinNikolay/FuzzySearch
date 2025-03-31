from sqlalchemy import Column, Integer, String
from db.database import BaseModel

class Corpus(BaseModel):
    __tablename__ = "corpus"

    corpus_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
