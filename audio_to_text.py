import os
import librosa
import soundfile as sf
from openai import OpenAI
from dotenv import load_dotenv
from textclass import textclass
from query import query_info

load_dotenv()
token = os.getenv('LLMFOUNDRY_TOKEN')

def preprocess_audio(speech_path):
    # Load the audio file
    audio, sr = librosa.load(speech_path, sr=16000, mono=True)
    
    # Normalize the audio to -20 dBFS
    rms = librosa.feature.rms(y=audio)[0]
    target_rms = 10 ** (-20 / 20)
    gain = target_rms / (rms.mean() + 1e-6)
    audio = audio * gain
    
    # Trim silence from the beginning and end
    audio, _ = librosa.effects.trim(audio, top_db=40)
    
    # Export the preprocessed audio to a temporary file
    preprocessed_path = "preprocessed_speech.wav"
    sf.write(preprocessed_path, audio, sr)
    
    return preprocessed_path

def audio_to_text( speech_path, prompt, query=''):
    # Preprocess the audio file
    preprocessed_path = preprocess_audio(speech_path)
    
    client = OpenAI(
        # This is the default and can be omitted
        api_key=f'{token}:my-test-project',
        base_url="https://llmfoundry.straive.com/openai/v1/",
    )

    with open(preprocessed_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
    
    # Clean up the temporary preprocessed file
    os.remove(preprocessed_path)
    
    # Analyze the transcription text
    if query:
        analysis = query_info(transcription.text + query)
    else:
        analysis = textclass(transcription.text + prompt)
    return analysis

# print(speech_to_text('speech.mp3'))