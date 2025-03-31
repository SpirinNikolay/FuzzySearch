import redis
import json

# Подключение к Redis

r = redis.Redis(host='localhost', port=6379, db=0)

def load_corpus(corpus):
    json_data = json.dumps(corpus)
    r.set(corpus["id"], json_data)

def get_corpus(corpus_id):
    stored_data = r.get(corpus_id)
    if stored_data:
        data_loaded = json.loads(stored_data)
        print(data_loaded)


def get_all_corpuses():
    corpuses = []
    # Получаем все ключи из Redis, предполагая, что все ключи соответствуют корпусам.
    for key in r.keys('*'):
        stored_data = r.get(key)
        if stored_data:
            data_loaded = json.loads(stored_data)
            # Добавляем только необходимые поля в результирующий список
            corpuses.append({
                "id": data_loaded.get("id"),
                "name": data_loaded.get("corpus_name")
            })
    return corpuses

if __name__ == '__main__':
    corpus = {
        "id": 1,
        "corpus_name": "example_corpus",
        "text": "This is a sample text for the corpus."
    }
    try:
        load_corpus(corpus)
        get_corpus(1)
    except Exception as e:
        print(e)
    finally:
        r.close()
