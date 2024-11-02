from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()
token = os.getenv('LLMFOUNDRY_TOKEN')

# prompt=input()
def query_info(prompt):

    client = OpenAI(
        api_key=token,
        base_url="https://llmfoundry.straive.com/openai/v1/",
    )
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt+"Read all the sentences carefully, and then provide the answer. Just give the answer directly.",
            }
        ],
        model="gpt-4o-mini",
    )
    return  response.choices[0].message.content
