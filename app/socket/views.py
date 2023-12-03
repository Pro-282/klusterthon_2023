from flask import Flask, request,jsonify, Blueprint, current_app
from flask_socketio import emit, send, join_room, disconnect
from app import socketio, db
import jwt
from app.users.models import User
from services.ffmpeg import process_audio
from services.openai import previous_transcribes, transcribe_audio_to_english, translate_text
import os, threading

socket_blueprint = Blueprint('socket', __name__)

connected_users = {}

callers_and_recipients = {}

@socketio.on("connect")
def handle_connect():
  token = request.args.get('token')
  try:
    data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
  except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
    emit('disconnected', 'Token expired, Login again.', to=request.sid)
    disconnect()
    return
  
  user_id = data['user_id']
  session_id = request.sid 
  connected_users[user_id] = session_id
  user = User.query.filter((User.id == user_id)).first()

  emit('connected', {'message': f"{user.username} has connected!", 'user_id': str(user.id)}, to=request.sid)

# @socketio.on("disconnect")
# def disconnected():
#   user_id = get_user_id_from_session_id(request.sid)
#   user = User.query.filter((User.id == user_id)).first()
  
#   user.is_online = False
#   user.peer_id = ""
#   db.session.commit()

#   connected_users.pop(user_id, None)

#   emit("disconnected", {'message': f"{user.username} has disconnected!", 'user_id': str(user.id)}, to=request.sid)

#   emit("user_online", {'message': f"{user.username} is offline", 'user_id': str(user.id)})

@socketio.on('peer_id')
def handle_user_peer(peer_id):
  user_id = get_user_id_from_session_id(request.sid)
  # adding the peer_id to the user's db making the is_online true for the user
  user = User.query.filter((User.id == user_id)).first()
  if peer_id != "":
    user.peer_id = peer_id
    user.is_online = True
    db.session.commit()

    user_data = {
    'id': str(user.id),
    'username': user.username,
    'email': user.email,
    'phone_number': user.phone_number,
    'profile_pic': user.profile_pic,
    'peer_id': user.peer_id,
    'is_online': user.is_online,
    'language': user.language
    }

    emit("user_online", {'message': f"{user.username} is online", 'user_data': user_data}, broadcast=True)
  else:
    emit("error", "Your peer_id wasn't supplied. You might want to refresh your page.", to=request.sid)


@socketio.on('user_offline')
def handle_user_offline():
  pass


# @socketio.on('make_call')
# def handle_user_call(recipient_user_id):
#   caller_user_id = get_user_id_from_session_id(request.sid)
#   caller_user = User.query.filter((User.id == caller_user_id)).first()

#   recipient_session_id = get_session_id_from_user_id(recipient_user_id)
#   recipient_user = User.query.filter((User.id == recipient_user_id)).first()
#   recipient_language = recipient_user.language

#   # store a map of callers to their recipient
#   callers_and_recipients[caller_user.id] = recipient_user.id

  
#   #todo: to caller
#   emit("call_begin")

#   #todo: to recipient
#   #! todo: send a 'calls can start, in text mode' message to the recepient ses_id room
#   emit("call_begin", {'message': 'call translation in text mode'}, to=request.sid)


# #todo: you need to handle an event from the receipient too to confirm the caller and send a call can start message too
# @socketio.on('receive_call')
# def handle_receipient_call(caller_user_id):
#   #todo: check if their details are in the callers_and_receipient map
#   if get_user_id_from_session_id(request.sid) == check_for_caller_and_recipient_id(caller_user_id):
#     #todo: if yes send a 'calls can start, in text mode' message to the caller and recipient ses_id room
#     pass
#   else:
#     #todo: if no send an error to the client(to destroy the call and start again)
#     pass


@socketio.on('audio_chunks')
def handle_audio_blobs(blob, user):
  user_id = user.get('id')
  # user_name = user.get('username')
  user_language = user.get('language')
  session_id = request.sid  # Capture the session ID
  socketio.start_background_task(process_audio_transcribe_and_translate, blob, user_id, user_language, session_id)

def process_audio_transcribe_and_translate(blob, user_id, user_language, session_id):
  # with app.app_context():
  input_filename = process_audio(blob, user_id)
  transcribed_text = transcribe_audio_to_english(input_filename, user_id)
  os.remove(input_filename)

  translated_text = translate_text(transcribed_text, user_language, user_id)
  print(translated_text)
  socketio.emit('translated_text', translated_text, namespace='/', to=session_id)


@socketio.on('end_call')
def handle_end_call(blob):
  pass

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