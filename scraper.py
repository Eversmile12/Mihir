
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from multiprocessing import Pool
import csv
from create_training_data import page_text_to_embeddings
from create_fine_tuning_job import create_fine_tune_model, upload_jsonl_file
import datetime
import spacy
nlp = spacy.load("en_core_web_sm")


def findFirstPage(url):

    # Send a request to the URL and get its content
    response = requests.get(url)
    content = response.content

    # Create a BeautifulSoup object from the webpage content
    soup = BeautifulSoup(content, "html.parser")

    # Get the domain of the webpage URL
    domain = urlparse(url).netloc

    # Find all the links in the webpage and extract their href attributes
    links = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if not href:
            # Skip links with empty href attribute
            continue
        # Check if the link is absolute or relative
        if urlparse(href).scheme:
            # Absolute link, no need to modify
            absolute_link = href
        else:
            # Relative link, prepend the domain of the webpage URL
            absolute_link = urljoin(url, href)
        # Check if the link is a duplicate or has already been found
        if absolute_link in links:
            continue
        # Check if the link has the same root domain as the webpage URL
        if urlparse(absolute_link).netloc == domain:
            # Add the absolute link to the list of links
            links.append(absolute_link)
    return links


def scrape_link(link, domain):
    # Send a request to the link and get its content
    response = requests.get(link)
    content = response.content
    # Create a BeautifulSoup object from the content
    soup = BeautifulSoup(content, "html.parser")
    # Find all the links in the webpage and extract their href attributes
    absolute_links = []

    for a in soup.find_all("a"):
        href = a.get("href")
        if not href:
            # Skip links with empty href attribute
            continue
        # Check if the link is absolute or relative
        if urlparse(href).scheme:
            # Absolute link, no need to modify
            absolute_link = href
        else:
            # Relative link, prepend the domain of the webpage URL
            absolute_link = urljoin(link, href)

        # Check if the link has the same root domain as the webpage URL
        if urlparse(absolute_link).netloc == domain:
            # Add the absolute link to the list of links
            absolute_links.append(absolute_link)
    return absolute_links

# Scrape the pages contained in the links in parallel using the Pool class


def multiProcessPages(links, max_pages, url):
    visited = set(links)
    visited_pages = 0
    with Pool() as pool:
        while links and len(visited) < max_pages:
            # Scrape the links in batches of 50
            batch = links[:50]
            links = links[50:]
            visited_pages += 50
            print(f"pages {len(batch)}")
            # Map the scrape_link function to the links in the batch
            results = pool.starmap(
                scrape_link, [(link, url) for link in batch])
            # Flatten the list of lists of absolute links to a list of absolute links
            absolute_links = [link for sublist in results for link in sublist]
            # Remove duplicates and links that have already been visited
            absolute_links = set(absolute_links) - visited
            # Add the absolute links to the list of visited links
            visited |= absolute_links
            print(f"pages {len(visited)}")
            # Add the absolute links to the list of links to scrape next
            links += list(absolute_links)
    return list(visited)[:max_pages]


# def save_links_sorted(links):
#     # Sort the links in alphabetical order
#     sorted_links = sorted(links)
#     # Save all the found absolute links in the same text file
#     with open("links.txt", "w") as file:
#         for link in sorted_links:
#             file.write(link + "\n")


def save_text_csv(links):
    with open("page_text.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Index", "page_url", "page_text"])
        with Pool() as pool:
            results = pool.map(scrape_text, links)
            for link, text in results:
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
                    for i, chunk_text in enumerate(chunks):
                        writer.writerow([i+1, link, chunk_text])
                    print(f"Saved text from {link} to CSV file")
                else:
                    print(f"Skipping {link} due to empty text")


def scrape_text(link):
    print(f"Scraping text from {link}")
    response = requests.get(link)
    content = response.content
    soup = BeautifulSoup(content, "html.parser")

    # Find the body of the page
    body = soup.find("body")
    if body is None:
        return link, None

    # Find the header and footer tags, if they exist, and remove them and their contents
    for tag in body(["header", "footer", "nav"]):
        tag.extract()

    # Extract the remaining text in the body and remove double new lines and random spaces
    text = body.get_text(separator="\n").replace("\n\n", "\n").strip()
    text = ' '.join(text.split())

    return link, text


if __name__ == "__main__":
    links = findFirstPage("https://docs.alchemy.com")
    visited = multiProcessPages(links, 100, "https://docs.alchemy.com")
    save_text_csv(visited)
    page_text_to_embeddings("page_text.csv")
    # id = upload_jsonl_file("training_data.jsonl")
    # id = upload_jsonl_file("training_data.jsonl")
    # fine_tune_model_id = create_fine_tune_model(id)

    # # Store the fine tune model ID and the current date in a CSV file
    # with open("model_ids.csv", "a", newline="", encoding="utf-8") as outfile:
    #     writer = csv.DictWriter(outfile, fieldnames=["date", "id"])
    #     if outfile.tell() == 0:
    #         writer.writeheader()
    #     writer.writerow({"date": datetime.datetime.now().strftime(
    #         "%Y-%m-%d %H:%M:%S"), "id": fine_tune_model_id})
    # print(
    #     f"Fine tune model ID ({fine_tune_model_id}) and date ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) stored in 'model_ids.csv'")
    # create_fine_tuning_job("training_data.jsonlw")
