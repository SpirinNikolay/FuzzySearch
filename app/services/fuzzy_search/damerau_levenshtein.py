from sqlalchemy.orm import Session

from models.word import Word


def compute_damerau_levenshtein(query: str, corpus_id: int, db: Session):
    """
    Для каждого слова из корпуса с идентификатором corpus_id вычисляет расстояние
    Дамерау–Левенштейна относительно строки query и возвращает список результатов,
    где каждый элемент — словарь с ключами "word" и "distance".
    """
    results = []
    # Извлекаем все слова, принадлежащие заданному корпусу
    candidate_entries = db.query(Word).filter(Word.corpus_id == corpus_id).all()
    for entry in candidate_entries:
        candidate_word = entry.term
        distance = damerau_levenshtein_distance(query, candidate_word)
        results.append({"word": candidate_word, "distance": distance})
    results.sort(key=lambda x: x["distance"])
    return results


def damerau_levenshtein_distance(s1: str, s2: str) -> int:
    """
    Вычисляет расстояние Дамерау–Левенштейна между строками s1 и s2.
    Это расширение классического расстояния Левенштейна с учётом транспозиций.
    """
    len1, len2 = len(s1), len(s2)
    # Инициализация матрицы размером (len1+1) x (len2+1)
    d = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    for i in range(len1 + 1):
        d[i][0] = i
    for j in range(len2 + 1):
        d[0][j] = j

    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            d[i][j] = min(
                d[i - 1][j] + 1,  # удаление
                d[i][j - 1] + 1,  # вставка
                d[i - 1][j - 1] + cost  # замена
            )
            if i > 1 and j > 1 and s1[i - 1] == s2[j - 2] and s1[i - 2] == s2[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + cost)  # транспозиция
    return d[len1][len2]
