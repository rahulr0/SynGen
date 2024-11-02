from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()
token = os.getenv('LLMFOUNDRY_TOKEN')

# prompt=input()
def textclass(prompt):

    client = OpenAI(
        api_key=token,
        base_url="https://llmfoundry.straive.com/openai/v1/",
    )
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "given classification of frames of video as string seperated by space tell me the category of the video. just give the category: \n" + prompt,
            }
        ],
        model="gpt-4o-mini",
    )
    return  response.choices[0].message.content

# print(textclass(''))
# a=textclass(prompt)
# print(a)