import base64
import requests
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('LLMFOUNDRY_TOKEN')

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def image_to_textbase64(base64_image,prompt):
  
    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
    }

    payload = {
    "model": "gpt-4o-mini",
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": prompt
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
            }
        ]
        }
    ],
    "max_tokens": 300
    }

    response = requests.post("https://llmfoundry.straive.com/openai/v1/chat/completions", headers=headers, json=payload)

    
    data=response.json()
    # category=data.choices[0].message.content
    return (data['choices'][0]['message']['content'])



# def image_to_textbase(image):
#    base64_image = encode_image(image)
#    return image_to_textbase(base64_image)


# image_path = f"adidas.jpg"
# base64_image = encode_image(image_path)
# print(image_to_textbase64(base64_image,'Please categorize this file based on its content. Just give the one category name'))
