import spacy
import math
from multiprocessing import Pool
from dynamo.dynamo_manager import DynamoDBManager

nlp = spacy.load("en_core_web_sm")
dynamo_manager = DynamoDBManager("Alchemy")

def process_link(link_text_tuple):
    link, text = link_text_tuple
    if text is not None:
        print(f"Processing text from {link}")
        text = text.replace("\t", " ")
        doc = nlp(text)
        max_chunk_tokens = 300
        chunks = []
        chunk = []
        num_tokens = 0
        for sent in doc.sents:
            sent_tokens = len(sent)
            if num_tokens + sent_tokens > max_chunk_tokens and len(chunk) > 0:
                chunks.append(" ".join(chunk))
                chunk = []
                num_tokens = 0
            chunk.append(sent.text)
            num_tokens += sent_tokens
        if len(chunk) > 0:
            chunks.append(" ".join(chunk))
        # Create items list to be passed to the `put_items` function
        items = []
        for i, chunk_text in enumerate(chunks):
            item = {
                "id": f"{link}_{i+1}",
                "page_url": link,
                "page_text": chunk_text,
            }
            items.append(item)
        print(f"Processed text from {link}")
        return items
    else:
        print(f"Skipping {link} due to empty text")
        return []

def save_text_dynamodb(link_text_tuple):
    num_processes = 4 # Set the number of processes to use
    batch_size = math.ceil(len(link_text_tuple) / num_processes)
    batches = [link_text_tuple[i:i+batch_size] for i in range(0, len(link_text_tuple), batch_size)]
    with Pool(processes=num_processes) as pool:
        results = pool.map(process_link, batches)
    # Combine the results from all batches into a single list of items
    items = [item for sublist in results for item in sublist]
    # Write the items to DynamoDB
    dynamo_manager.put_items(items)
    print(f"Saved all text to DynamoDB")
