# Python Chatbot with GPT3.5

👋 Hey there! Welcome to this awesome repository, which contains code for spinning up a personal chatbot using GPT3.5 trained on any documentation. And guess what? 90% of the code has been developed using ChatGPT, a large language model trained on the GPT-3.5 architecture! 💻

So, are you ready to create your own personal chatbot and start chatting with it? Here are the steps you need to follow:

## Getting Started

1. Clone the repository:

```
git clone https://github.com/your_username/your_repo.git
```

2. Create a new virtual environment and activate it:

```
python3 -m venv env
source env/bin/activate
```

3. Install the requirements:

```
pip install -r requirements.txt
```

4. In the `scraper.py` file, change the `url` and `page number` variable in the following function (precisely when calling `multiProcessPages` and `findFirstPage`):

```python
if __name__ == "__main__":
    links = findFirstPage("https://your_documentation_website.com")
    visited = multiProcessPages(links, 15, "https://your_documentation_website.com/")
    save_text_csv(visited)
    page_text_to_embeddings("page_text.csv")
```

5. Set up the environment variables for Pinecone and OpenAI. You can find guides on how to get your API keys here: [Pinecone](https://www.pinecone.io/docs/quickstart/) and [OpenAI](https://beta.openai.com/docs/quickstart).

6. Once the two API keys are set, run `scraper.py`:

```
python3 scraper.py
```

7. Wait for the process to complete.

8. Run the `chat.py` file:

```
python3 chat.py
```

9. And voila! You can now start chatting with your personal chatbot and ask it anything you want. It's like having your own personal assistant! 🤖💬

## Badges

[![Placeholder](https://img.shields.io/badge/repository-placeholder-green.svg)](https://github.com/your_username/your_repo)

Hope you enjoy using this repository as much as we enjoyed creating it. Happy chatting! 😄