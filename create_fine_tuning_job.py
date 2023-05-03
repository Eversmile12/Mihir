import json
import requests
import openai
import os
openai.api_key = os.environ["OPEN_AI"]


def upload_jsonl_file( file_path):
    url = "https://api.openai.com/v1/files"
    headers = {
        "Authorization": f"Bearer {openai.api_key}"
    }
    data = {
        "purpose": "fine-tune",
    }
    with open(file_path, "rb") as file:
        response = requests.post(url, headers=headers,
                                 data=data, files={"file": file})
        response_json = response.json()
        file_id = response_json["id"]
        print(f"File uploaded with ID: {file_id}")
        return file_id


def create_fine_tune_model(id):
    url = "https://api.openai.com/v1/fine-tunes"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }
    data = {
        "training_file": id,
        "model": "curie",
        "batch_size": 512
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.ok:
        print("Fine tune model created successfully")
        return response.json()["id"]
    else:
        raise Exception(f"Failed to create fine tune model: {response.text}")
