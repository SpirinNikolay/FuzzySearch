from sqlalchemy.orm import Session

from models.word import Word


def compute_bitap_wu_manber(query: str, corpus_id: int, db: Session):
    """
    Для каждого слова из корпуса с идентификатором corpus_id вычисляет
    приближённое расстояние с использованием бит-параллельного алгоритма Майерса,
    который отражает модификации от Wu и Manber. Результат — список слов с рассчитанным расстоянием.
    """
    results = []
    candidate_entries = db.query(Word).filter(Word.corpus_id == corpus_id).all()
    for entry in candidate_entries:
        candidate_word = entry.term
        distance = myers_edit_distance(query, candidate_word)
        results.append({"word": candidate_word, "distance": distance})
    results.sort(key=lambda x: x["distance"])
    return results


def myers_edit_distance(a: str, b: str) -> int:
    """
    Реализует алгоритм Майерса для вычисления расстояния Левенштейна с использованием
    бит-параллелизма. Данный вариант подходит для сравнительно коротких строк (обычно длина a не превышает разрядность машинного слова).

    Если одна из строк пустая, расстояние равно длине другой.
    """
    if not a:
        return len(b)
    if not b:
        return len(a)

    # Для удобства, если a длиннее, меняем строки местами
    if len(a) > len(b):
        a, b = b, a
    m = len(a)
    n = len(b)

    # Инициализируем маску символов для строки a
    pattern_mask = {}
    for char in set(a):
        pattern_mask[char] = 0
    for i, char in enumerate(a):
        pattern_mask[char] |= 1 << i

    VP = (1 << m) - 1  # "Вертикальный положительный" вектор (все биты = 1)
    VN = 0  # "Вертикальный отрицательный" вектор (все биты = 0)
    score = m

    for char in b:
        PM = pattern_mask.get(char, 0)
        X = PM | VN
        # Вычисляем D0 — битовая маска ошибок для текущей позиции
        D0 = (((X & VP) + VP) ^ VP) | X
        # Определяем биты переноса ошибок
        HP = VN | ~(D0 | VP)
        HN = D0 & VP
        # Корректируем текущее значение расстояния
        if HP & (1 << (m - 1)):
            score += 1
        elif HN & (1 << (m - 1)):
            score -= 1
        # Обновляем векторы VP и VN для следующей итерации
        VP = (HN << 1) | ~(D0 | ((HP << 1) | 1))
        VN = D0 & ((HP << 1) | 1)
    return score
