import ffmpeg
import uuid

def process_audio(audio_blob, user_id):
  # Create unique filenames
  input_filename = f"{user_id}_{uuid.uuid4()}.webm"
  output_filename = f"{user_id}_{uuid.uuid4()}.webm"

  # Write the audio blob to a file
  with open(input_filename, 'wb') as file:
    file.write(audio_blob)

  # Re-encode audio using ffmpeg
  ffmpeg.input(input_filename).output(output_filename).run(loglevel='info')

  return input_filename, output_filename