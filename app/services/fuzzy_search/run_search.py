from time import time

from sqlalchemy.orm import Session

from schemas.fuzzy_search import RequestModel
from services.fuzzy_search.damerau_levenshtein import compute_damerau_levenshtein
from services.fuzzy_search.bitap_wu_manber import compute_bitap_wu_manber


def execute_search_algorithm(request: RequestModel, db: Session):
    """
    Измеряет время работы выбранного алгоритма поиска и возвращает найденные результаты.
    В зависимости от значения request.algorithm выбирается алгоритм:
      - "damerau" для расчёта расстояния Дамерау-Левенштейна,
      - "bitap" для алгоритма Bitap с модификациями от Wu и Manber.
    При указании неизвестного алгоритма возвращается False.
    """
    start_time = time()
    if request.algorithm == "damerau":
        result = compute_damerau_levenshtein(request.word, request.corpus_id, db)
    elif request.algorithm == "bitap":
        result = compute_bitap_wu_manber(request.word, request.corpus_id, db)
    else:
        result = False
    end_time = time()
    return result, end_time - start_time