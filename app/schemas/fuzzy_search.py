from pydantic import BaseModel

class RequestModel(BaseModel):
    word: str
    algorithm: str
    corpus_id: int