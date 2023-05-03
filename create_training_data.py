import openai
import csv
import uuid
import multiprocessing as mp
from get_text_embeddings import get_text_embeddings
from pineconeClient import PineconeClient
import os
# Set up OpenAI API credentials
openai.api_key = os.environ['OPEN_AI']
openai.api_base = "https://api.openai.com/v1/"


# def create_training_data(prompt, examples):
#     max_tokens = 3500
#     while max_tokens > 0:
#         try:
#             print(f"Requesting with max_tokens={max_tokens}")
#             response = openai.ChatCompletion.create(
#                 model="gpt-3.5-turbo",
#                 messages=[{"role":"user", "content":prompt}],
#                 temperature=0.4,
#             )
#             print("Request completed")
#             print(response)
#             return response.choices[0].message.content.strip()
#         except openai.error.OpenAIError as e:
#             print(f"OpenAI error: {e}")
#             print("Retry with lower max_tokens")
#             max_tokens -= 200

#     raise Exception("Failed to generate response after multiple retries")


# def extract_json(text):
#     # Initialize an empty list to store parsed JSON objects
#     json_objects = []
#     # Loop through the string, looking for curly braces
#     start_index = 0
#     while True:
#         start_index = text.find("{", start_index)
#         if start_index == -1:
#             break
#         end_index = text.find("}", start_index)
#         if end_index == -1:
#             break
#         # Extract the JSON substring from the text
#         json_string = text[start_index:end_index+1]
#         try:
#             # Attempt to parse the JSON string
#             json_data = json.loads(json_string)

#             # Check if the prompt and completion keys are present in the JSON object
#             if "prompt" in json_data and "completion" in json_data:
#                 prompt = json_data["prompt"] + " \n\n###\n\n"
#                 completion = " " + json_data["completion"] + "###"
#                 json_objects.append(
#                     {"prompt": prompt, "completion": completion})

#         except ValueError:
#             # If the JSON string is invalid, ignore it
#             pass
#         # Move the start index to the next character after the end index
#         start_index = end_index + 1

#     return json_objects


def process_row(row):
    # # Replace any newlines or tabs in the page text with spaces
    # page_text = row["page_text"].replace("\n", " ").replace("\t", " ")
    # prompt = 'Generate one or more strings convertible to JSON containing the training data relative to this page' + \
    #     row["page_url"] + '.\n'
    # prompt += 'The training data must be in the format of: {"prompt": "<prompt_text>", "completion": "<ideal_generated_text>"}\n'
    # prompt += 'Prompt: question or statement related to the page content. Keep it <280 characters and as generic as possible. Must include question marks only 20% of times.\n'
    # prompt += 'Response: provide a specific answer to the prompt in <1000 characters. The completion should include relevant code and reference the appropriate section in the documentation page.'
    # prompt += row["page_text"]
    # examples = [
    #     ["Input:", page_text],
    #     ["Output:", ""]
    # ]
    # if response:
    #     json_data = extract_json(response)
    #     if len(json_data):
    #         return json_data
    embedding = get_text_embeddings(row['page_text'])
    if embedding:
        return embedding, row['page_text']


def page_text_to_embeddings(input_file):
    with open(input_file, "r", newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        pool = mp.Pool(processes=mp.cpu_count())
        vectors_map = pool.map(process_row, reader)
        pool.close()
        pool.join()
        ids_vectors = []
        # training_data = [
        #     json_data for json_list in training_data for json_data in json_list]
        for vector in vectors_map:
            id = str(uuid.uuid4())
           

            ids_vectors.append({"id": id, "values": vector[0],
                                "metadata": {"message": vector[1]}})

        client = PineconeClient()
        client.create_index("my-index")
        response = client.upsert("my-index", ids_vectors)
        print(response)


# Example usage
if __name__ == "__main__":
    page_text_to_embeddings("page_text.csv")
