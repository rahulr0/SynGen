from flask import Flask, request, redirect, url_for, render_template, send_file
from dotenv import load_dotenv
from openai import OpenAI
from io import StringIO
import pandas as pd 
import os
import requests
import re
import json
from image_to_textbase64 import encode_image
from image_to_textbase64 import image_to_textbase64
from video_to_text import video_to_text
from audio_to_text import audio_to_text


app = Flask(__name__)

if os.path.exists('.env'):
    os.remove('.env')

# Allowed file extensions for multimedia uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mp3', 'wav'}
ALLOWED_IMAGES = {'png', 'jpg', 'jpeg'}
ALLOWED_VIDEOS = {'gif', 'mp4'}
ALLOWED_AUDIOS = {'mp3','wav'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGES
def allowed_video(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEOS
def allowed_audio(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIOS



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        api_key = request.form.get('api_key')
        if api_key:
            env_file = '.env'
            
            # Check if the .env file exists
            if os.path.exists(env_file):
                # Read the existing contents of the .env file
                with open(env_file, 'r') as f:
                    lines = f.readlines()
                
                # Replace the existing token if it exists
                with open(env_file, 'w') as f:
                    token_found = False
                    for line in lines:
                        if line.startswith('LLMFOUNDRY_TOKEN='):
                            f.write(f'LLMFOUNDRY_TOKEN={api_key}\n')
                            token_found = True
                        else:
                            f.write(line)
                    # If the token was not found, append it
                    if not token_found:
                        f.write(f'LLMFOUNDRY_TOKEN={api_key}\n')
            else:
                # If the file does not exist, create it and write the token
                with open(env_file, 'w') as f:
                    f.write(f'LLMFOUNDRY_TOKEN={api_key}\n')
            
            # Reload the environment variables
            load_dotenv()  # Reload the .env file to get the new token
            token = os.getenv('LLMFOUNDRY_TOKEN')

            
        # Handle CSV download
        if 'download' in request.form:
            return send_file(
                'result.csv',
                mimetype='text/csv',
                download_name='result.csv',
                as_attachment=True
            )

        # Check if multimedia file is uploaded
        file = request.files.get('fileUpload')
        query = request.form.get('media_prompt')

        
        if file and allowed_file(file.filename):
            file_type = request.form.get('media_type')
            category_input = request.form.get('category_option')
            
            
            # Process the file, either with user-defined categories or letting the API categorize it
            if category_input == "user_categories":
                user_categories = request.form.get('categories')
                prompt = f"Please categorize this {file_type} file into the following categories: {user_categories}. Just give the one category name."
            else:
                prompt = f"Please categorize this {file_type} file based on its content. Just give the one category name"


            #----------------------------image--------------------------------
            if allowed_image(file.filename):
                # Save the file
                file_path = os.path.join('static', 'images', file.filename)
                file.save(file_path)

                content = image_to_textbase64(encode_image(file_path),prompt)

                # For demonstration, we'll print the API's response
                print(content)
                
                if query:
                    information = image_to_textbase64(encode_image(file_path),query)
                    print(information)
                    return render_template('result.html', result=content, image = file.filename, query=information)

                return render_template('result.html', result=content, image = file.filename)

            #----------------------------video--------------------------------
            if allowed_video(file.filename):
                # Usage
                file_path = os.path.join('static','videos', file.filename)
                file.save(file_path)

                if category_input == "user_categories":
                    user_categories = request.form.get('categories')
                    prompt = f"Please categorize this {file_type} file into the following categories: {user_categories}. Just give the one category name."
                else:
                    prompt = f"Please give a 25 word description of the frame."

                category = video_to_text(file_path, prompt)

                print(f"The video category is: {category}")
                
                if file.filename[-3:]=='gif':
                    if query:
                        information = video_to_text(file_path, prompt, query)
                        print(information)
                        return render_template('result.html', result=category, gif = file.filename, query=information)
                    return render_template('result.html', result=category, gif = file.filename)

                if query:
                    information = video_to_text(file_path, prompt, query)
                    print(information)
                    return render_template('result.html', result=category, video = file.filename, query=information)
                return render_template('result.html', result=category, video = file.filename)


            #----------------------------audio--------------------------------
            if allowed_audio(file.filename):
                file_path = os.path.join('static', 'audios', file.filename)
                file.save(file_path)

                audio_file = file.filename
                category = audio_to_text(file_path, prompt)

                print(f"The audio category is: {category}")

                if query:
                    information = audio_to_text(file_path, prompt, query)
                    print(information)
                    return render_template('result.html', result=category, audio = file.filename, query=information)

                return render_template('result.html', result=category, audio = file.filename)


        #--------------------------text--------------------------
        # Handle user input (text prompt)
        user_input = request.form.get('textarea')

        # Handle user input for text data and convert it to CSV
        if user_input:
            client = OpenAI(
                api_key=f'{token}:my-test-project',
                base_url="https://llmfoundry.straive.com/openai/v1/",
            )
                
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": user_input + " The response should only be in JSON format, which can be easily converted to a CSV file."}],
                model="gpt-4o-mini",
            )
                
            response = chat_completion
            content = response.choices[0].message.content

            print(content)

            # Extract JSON from the API response
            json_str = re.search(r'```json(.*?)```', content, re.DOTALL).group(1).strip()
            data = json.loads(json_str)

            # Convert JSON to CSV and save it
            df = pd.DataFrame(data)
            df.to_csv('result.csv', index=False)
            table_html = df.to_html(classes='table table-striped')

            if 'view' in request.form:
                return render_template('table.html', table_html=table_html)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
