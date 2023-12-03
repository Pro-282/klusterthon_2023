from openai import OpenAI
import os
# from threading import Lock

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# previous_transcribes = {}
# transcribes_lock = Lock()

def transcribe_audio_to_english(audio_file_name, user_id):
  try:
    with open(audio_file_name, 'rb') as file:
      transcribe = client.audio.translations.create(
      model="whisper-1", 
      file=file,
      response_format="text",
      # prompt=f"Translate this audio to English, this is the translations of the preceding segments of the audio: {previous_transcribes.get(user_id, '')}",
      # prompt=str(previous_transcribes.get(user_id, '')),
      temperature=0
    )
  except Exception as e:
    print("Transcribe audio error: ",e)
  # Return the transcribed text
  return transcribe

def translate_text(text, target_language, user_id, context=True):
  try:
  #   combined_text = text
  #   if context:
  #     with transcribes_lock:
  #       if user_id in previous_transcribes:
  #         combined_text = previous_transcribes[user_id] + " " + text
        
  #    # Update the dictionary within the lock
  #   with transcribes_lock:
  #     previous_transcribes[user_id] = combined_text
  #   print(combined_text)

    response = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "user", "content": f'Translate the following English text to {target_language}: "{text}"'}
      ],
      temperature=0
    )
    response_content = response.choices[0].message.content
  except Exception as e:
    print("Translate text error: ", e)
  return response_content