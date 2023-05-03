import requests
import json
from pineconeClient import PineconeClient
from get_text_embeddings import get_text_embeddings
import html
import os

def get_moderation_flagged(input_text, model="text-moderation-latest"):
    url = "https://api.openai.com/v1/moderations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['OPEN_AI']}",
    }
    payload = {
        "input": input_text,
        "model": model
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        raise ValueError(f"Failed to get moderation score: {response.text}")
    flagged = response.json()["results"][0]["flagged"]
    return flagged


def sanitize_input(user_input):
    # remove leading/trailing whitespace
    user_input = user_input.strip()
    # remove potentially harmful characters
    user_input = user_input.replace('<', '&lt;').replace('>', '&gt;')
    user_input = user_input.replace('"', '&quot;').replace("'", '&#39;')
    # escape special characters
    user_input = html.escape(user_input)
    return user_input


def get_context(text):
    text = sanitize_input(text)
    isFlagged = get_moderation_flagged(text)
    if not isFlagged:
        embeddings = get_text_embeddings(text)
        client = PineconeClient()
        top_neighbours = client.query("my-index", embeddings)
        context = ""
        for neighbour in top_neighbours:
            context += "\n" + neighbour["metadata"]["message"]

        return context
    else:
        return
