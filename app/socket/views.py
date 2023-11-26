from flask import Flask, request,jsonify, Blueprint, current_app
from flask_socketio import emit, send, join_room, disconnect
from app import socketio, db
import jwt
from app.users.models import User
from services.ffmpeg import process_audio
from services.openai import previous_translations, transcribe_audio_to_english, translate_text
import os

socket_blueprint = Blueprint('socket', __name__)

connected_users = {}

callers_and_recipients = {}

@socketio.on("connect")
def handle_connect():
  token = request.args.get('token')
  try:
    data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
  except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
    disconnect()
    return
  
  user_id = data['user_id']
  session_id = request.sid 
  connected_users[user_id] = session_id
  user = User.query.filter((User.id == user_id)).first()

  emit('connected', {'message': f"user {user.username} has connected", 'user_id': user.id}, broadcast=True)

@socketio.on("disconnect")
def disconnected():
  user_id = get_user_id_from_session_id(request.sid)
  connected_users.pop(user_id, None)
  
  user = User.query.filter((User.id == user_id)).first()

  emit("disconnected", {'message': f"user {user.username} has disconnected", 'user_id': user.id}, broadcast=True)

@socketio.on('data')
def handle_message(data):
  emit("data",{'data':data,'id':request.sid},broadcast=True) #? this method is for emitting json doc

@socketio.on('peer_id')
def handle_user_peer(peer_id):
  user_id = get_user_id_from_session_id(request.sid)
  #todo: implement adding the peer_id to the user's db making the is_online true for the user
  user = User.query.filter((User.id == user_id)).first()
  user.peer_id = peer_id
  user.is_online = True
  db.session.commit()
  #todo: and broadcast to everyone that the user's username is online
  emit("user_online", f"{user.username} is online", broadcast=True)

@socketio.on('make_call')
def handle_user_call(recipient_user_id):
  caller_user_id = get_user_id_from_session_id(request.sid)
  caller_user = User.query.filter((User.id == caller_user_id)).first()

  #todo: get callee's session_id so that translated text can be sent to him directly
  recipient_session_id = get_session_id_from_user_id(recipient_user_id)
  #todo: send a translated text to the other caller
  recipient_user = User.query.filter((User.id == recipient_user_id)).first()

  recipient_language = recipient_user.language

  #? store a map of callers to their recipient
  callers_and_recipients[caller_user.id] = recipient_user.id

  #! todo: send a 'calls can start, in text mode' message to the recepient ses_id room


#todo: you need to handle an event from the receipient too to confirm the caller and send a call can start message too
@socketio.on('receive_call')
def handle_receipient_call(caller_user_id):
  #todo: check if their details are in the callers_and_receipient map
  if get_user_id_from_session_id(request.sid) == check_for_caller_and_recipient_id(caller_user_id):
    #todo: if yes send a 'calls can start, in text mode' message to the caller and recipient ses_id room
    pass
  else:
    #todo: if no send an error to the client(to destroy the call and start again)
    pass


#todo: handle an event to receive audio chunks from both callers, send it over to ffmpeg to reencode it 
#todo: send the reencoded audio to openai, along side a prompt of the previously translated texts for context purpose
#todo: and send the full text to the client. that way, we can maintain consistency despite translating chunk by chunk
@socketio.on('audio_chunks')
def handle_audio_chunks(data):
  audio_blob = data
  user_id = get_user_id_from_session_id(request.sid)
  user = User.query.filter((User.id == user_id)).first()

  input_filename, output_filename = process_audio(audio_blob, user_id)
  transcribed_text = transcribe_audio_to_english(output_filename)
  translated_text = translate_text(transcribed_text, )

  translated_text = translate_text(transcribed_text, user.language, previous_translations.get(user_id, ""))

  # Update context for the user
  previous_translations[user_id] = translated_text

  recipient_user_id = find_caller_pair(callers_and_recipients, user_id)

  recipient_session_id = get_session_id_from_user_id(recipient_user_id)  

  # Send translated text back to the other recipient
  emit('translated_text', translate_text, to=recipient_session_id)

  # Clean up audio files
  os.remove(input_filename)
  os.remove(output_filename)


def get_user_id_from_session_id(session_id):
  for user_id, sid in connected_users.items():
    if sid == session_id:
      return user_id
  return None

def get_session_id_from_user_id(User_id):
  for user_id, sid in connected_users.items():
    if user_id == User_id:
      return sid
  return None

def check_for_caller_and_recipient_id(caller_user_id):
  for caller_id, recipient_id in callers_and_recipients.items():
    if caller_id == caller_user_id:
      return recipient_id
  return None

def find_caller_pair(caller_dict, caller_id):
  if caller_id in caller_dict:
    return caller_dict[caller_id]
  else:
    for key, value in caller_dict.items():
      if value == caller_id:
        return key
  return None