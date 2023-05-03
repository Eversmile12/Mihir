import openai
import os
from get_context import get_context
openai.api_key = os.environ["OPEN_AI"]
system_prompt = "You are a very enthusiastic Alchemy representative named Mihir who loves to help people! Given the following Context section provided from the Alchemy documentation and the Previous messages you've sent, answer the Question using only that information. Output must be in markdown format. If you are unsure and the answer is not explicitly written in the documentation, output must only be {success:false}. Include links to relevant docs pages when possible."
latest_responses = []

while True:
    user_input = input("> ")
    if user_input == "\x1b":  # check for escape key
        break

    context = get_context(user_input)
    prompt = f" \n\n Context sections:\n{context} \n\n Question '''{user_input}'''"
    merged_latest_responses = '\n'.join(latest_responses)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",
            "content": f"Previous messages: {merged_latest_responses}"
         },
        {"role": "user", "content": prompt},
    ]
    # print(messages)
    # print("\n\n")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.3,
    )
    print(response.choices[0]["message"]["content"])
    latest_responses.append(response.choices[0]["message"]["content"])
