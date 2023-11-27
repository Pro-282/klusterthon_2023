from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

previous_translations = {}

def transcribe_audio_to_english(audio_file_name, user_id):
  audio_file = open(audio_file_name)
  transcript = client.audio.translations.create(
    model="whisper-1", 
    file=audio_file,
    response_format="text",
    prompt=f"this is the transcript of the preceding segment of audio: {previous_translations.get(user_id, '')}",
    temperature=0
  )
  print(transcript)
  # Return the transcribed text
  return transcript

def translate_text(text, target_language, user_id, context=True):
  if context:
    previous_text = previous_translations[user_id]
    # Combine context with new text
    combined_text = previous_text + " " + text
  
  response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "user", "content": f'Translate the following English text to {target_language}: "{combined_text}"'}
    ],
    temperature=0
  )
  return str(response['choices'][0]['message']['content'])