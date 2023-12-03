import ffmpeg
import uuid

def process_audio(audio_blob, user_id):
  # Create unique filenames
  input_filename = f"{user_id}_{uuid.uuid4()}.webm"

  with open(input_filename, 'wb') as file:
    file.write(audio_blob)

  return input_filename