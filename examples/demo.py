import requests

payload = {
    "prompt": "Explain how Raft leader election works.",
    "min_confidence": 0.65,
    "num_samples": 5,
}

res = requests.post(
    "http://localhost:8000/evaluate",
    json=payload,
)

print(res.json())
