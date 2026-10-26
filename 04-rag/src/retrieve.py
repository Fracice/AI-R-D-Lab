
import hashlib
import json
import math
import sys
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "historical_events.json"
CACHE_PATH = BASE_DIR / "data" / "embeddings_cache.json"

OLLAMA_URL = "http://localhost:11434/api/embed"
EMBED_MODEL = "nomic-embed-text"


def get_embedding(text):
    payload = json.dumps({
        "model": EMBED_MODEL,
        "input": text
    }).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result["embeddings"][0]


def cosine_similarity(vector_a, vector_b):
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    norm_a = math.sqrt(sum(a * a for a in vector_a))
    norm_b = math.sqrt(sum(b * b for b in vector_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def document_text(document):
    return (
        f"{document['title']}\n"
        f"{document['date']}\n"
        f"{document['content']}"
    )


def load_documents():
    with DATA_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def load_or_create_embeddings(documents):
    # Invalida la cache se cambiano i dati o il modello.
    fingerprint_input = json.dumps({
        "model": EMBED_MODEL,
        "documents": documents
    }, ensure_ascii=False, sort_keys=True)

    fingerprint = hashlib.sha256(
        fingerprint_input.encode("utf-8")
    ).hexdigest()

    if CACHE_PATH.exists():
        try:
            with CACHE_PATH.open(encoding="utf-8") as file:
                cache = json.load(file)

            if cache.get("fingerprint") == fingerprint:
                embeddings = cache.get("embeddings", {})
                if all(doc["id"] in embeddings for doc in documents):
                    print("Cache embeddings: utilizzata")
                    return embeddings
        except (json.JSONDecodeError, OSError):
            pass

    print("Cache embeddings: creazione/aggiornamento")

    embeddings = {}
    for index, document in enumerate(documents, start=1):
        embeddings[document["id"]] = get_embedding(
            document_text(document)
        )
        print(f"Embedding generato: {index}/{len(documents)}")

    cache = {
        "fingerprint": fingerprint,
        "model": EMBED_MODEL,
        "embeddings": embeddings
    }

    with CACHE_PATH.open("w", encoding="utf-8") as file:
        json.dump(cache, file, ensure_ascii=False)

    return embeddings


def retrieve(query, top_k=3, min_score=0.30):
    documents = load_documents()
    embeddings = load_or_create_embeddings(documents)
    query_embedding = get_embedding(query)

    scored = []

    for document in documents:
        document_embedding = embeddings[document["id"]]
        score = cosine_similarity(query_embedding, document_embedding)
        scored.append((score, document))

    scored.sort(key=lambda item: item[0], reverse=True)

    return [
        (score, document)
        for score, document in scored
        if score >= min_score
    ][:top_k]


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]).strip()

    if not query:
        query = input("Inserisci una domanda: ").strip()

    try:
        results = retrieve(query)

        if not results:
            print("Nessun documento supera la soglia di similarità.")
            sys.exit(0)

        for score, document in results:
            print(f"\nSimilarità: {score:.3f}")
            print(f"{document['title']} ({document['date']})")
            print(document["content"])
            print(f"Fonte: {document['source']}")

    except Exception as error:
        print(f"Errore durante il recupero: {error}")
