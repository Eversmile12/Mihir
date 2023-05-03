import requests
import json
import os

def get_text_embeddings(text):
    url = "https://api.openai.com/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {os.environ['OPEN_AI']}",
        "Content-Type": "application/json"
    }
    payload = {
        "input": text,
        "model": "text-embedding-ada-002"
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        raise ValueError(f"Failed to get embeddings for text: {response.text}")
    embeddings = response.json()["data"][0]["embedding"]
    return embeddings
