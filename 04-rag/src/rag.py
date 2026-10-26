import json
import sys
import urllib.request
from pathlib import Path

from retrieve import retrieve

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3:8b"


def ask_qwen(question, documents):
    context = "\n\n".join(
        f"Titolo: {doc['title']}\n"
        f"Data: {doc['date']}\n"
        f"Informazioni: {doc['content']}\n"
        f"Fonte: {doc['source']}"
        for _, doc in documents
    )

    if not context:
        context = "Nessun documento pertinente è stato recuperato."

    messages = [
        {
            "role": "system",
            "content": (
                "Rispondi in italiano. Usa le informazioni nei documenti "
                "forniti per rispondere a domande fattuali. "
                "Non inventare fatti o fonti. Se i documenti non bastano, "
                "dichiara esplicitamente che le informazioni sono insufficienti. "
                "Distingui le informazioni dei documenti dalle tue conoscenze."
            )
        },
        {
            "role": "user",
            "content": (
                f"Documenti recuperati:\n{context}\n\n"
                f"Domanda: {question}"
            )
        }
    ]

    payload = json.dumps({
        "model": MODEL,
        "messages": messages,
        "stream": False
    }).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result["message"]["content"]


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]).strip()

    if not question:
        question = input("Domanda: ").strip()

    documents = retrieve(question)

    print("\n=== DOCUMENTI RECUPERATI ===")
    if documents:
        for score, doc in documents:
            print(f"\n[{score}] {doc['title']} ({doc['date']})")
            print(doc["content"])
            print(f"Fonte: {doc['source']}")
    else:
        print("Nessun documento pertinente trovato.")

    print("\n=== RISPOSTA DI QWEN CON RAG ===")
    try:
        print(ask_qwen(question, documents))
    except Exception as error:
        print(f"Errore durante la chiamata a Ollama: {error}")
