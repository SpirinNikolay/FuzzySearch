from pydantic import BaseModel
from pydantic import BaseModel, Field
from typing import List

class CorpusResponse(BaseModel):
    id: int = Field(..., alias="corpus_id")
    name: str = Field(..., alias="corpus_name")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class CorpusesResponse(BaseModel):
    corpuses: List[CorpusResponse]

class CorpusInput(BaseModel):
    corpus_name: str
    text: str