import json
import time
import urllib.error
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3:8b"


def chat(messages, temperature=0):
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature},
        "think": False,
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    start_time = time.perf_counter()

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(
            "Could not connect to Ollama. Make sure Ollama is running."
        ) from exc

    elapsed = time.perf_counter() - start_time
    print(f"[Ollama response time: {elapsed:.2f} seconds]")

    return result["message"]["content"].strip()


if __name__ == "__main__":
    answer = chat([
        {
            "role": "user",
            "content": "Reply with exactly: Multi-Agent Systems ready",
        }
    ])
    print(answer)