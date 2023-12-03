from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

previous_transcribes = {}

def transcribe_audio_to_english(audio_file_name, user_id):
  with open(audio_file_name, 'rb') as file:
    transcribe = client.audio.translations.create(
    model="whisper-1", 
    file=file,
    response_format="text",
    # prompt=f"Translate this audio to English, this is the translations of the preceding segments of the audio: {previous_transcribes.get(user_id, '')}",
    prompt=str(previous_transcribes.get(user_id, '')),
    temperature=0
  )
  # Return the transcribed text
  return transcribe

def translate_text(text, target_language, user_id, context=True):
  if context:
    if user_id in previous_transcribes:
      previous_text = previous_transcribes[user_id]
      # Combine context with new text
      combined_text = previous_text + " " + text
    else:
      combined_text = text
      
  print(combined_text)
  response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "user", "content": f'Translate the following English text to {target_language}: "{combined_text}"'}
    ],
    temperature=0
  )
  response_content = response.choices[0].message.content
  return response_content