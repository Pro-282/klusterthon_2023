from app import create_app, socketio
from dotenv import load_dotenv
import os

load_dotenv()

app = create_app(os.getenv("SERVER"))  # || 'production', 'testing',

if __name__ == '__main__':
  socketio.run(app, host='0.0.0.0', port=5000, debug=True)  # debug=True should only be used in development!
  #todo: get this values from environmental variables