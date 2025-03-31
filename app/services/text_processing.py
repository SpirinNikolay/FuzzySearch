import re
from typing import Any, Generator

from sqlalchemy.orm import Session

from models.corpus import Corpus
from models.word import Word
from schemas.corpus import CorpusInput


def split_text(text: str) -> Generator[str, Any, None]:
    """
    Разбивает текст на слова, удаляя знаки препинания.
    Возвращает генератор, который выдаёт слова в нижнем регистре.
    """
    pattern = re.compile(r'\b\w+\b', re.UNICODE)
    return (match.group().lower() for match in pattern.finditer(text))


def create_corpus_entry(db: Session, corpus_data: CorpusInput):
    """
    Создает новую запись корпуса с заданным именем.
    """
    new_entry = Corpus(name=corpus_data.corpus_name)
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry


def store_words(db: Session, corpus_id: int, text: str):
    """
    Делит текст на слова и сохраняет каждое слово, связанное с указанным корпусом.
    """
    tokens = split_text(text)
    for token in tokens:
        if token:
            word_record = Word(corpus_id=corpus_id, term=token)
            db.add(word_record)
    db.commit()
