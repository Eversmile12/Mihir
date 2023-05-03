import requests
import os

# Set your OpenAI API key as an environment variable
openai_api_key = os.environ['OPEN_AI']

# Set the API endpoint URL
url = 'https://api.openai.com/v1/fine-tunes'

# Set the headers, including the authorization token
headers = {
    'Authorization': f'Bearer {openai_api_key}',
}

# Make the API request and print the response to the console
response = requests.get(url, headers=headers)
print(response.json())
