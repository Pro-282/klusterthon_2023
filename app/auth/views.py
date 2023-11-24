from flask import Blueprint, request, jsonify, make_response, current_app
from app import db
from app.users.models import User
import jwt
import datetime
from functools import wraps
import re

auth_blueprint = Blueprint('auth', __name__)

# Email and phone number validation regex patterns
EMAIL_REGEX = re.compile(r'\b[\w.-]+@[\w.-]+\.\w{2,4}\b')
PHONE_REGEX = re.compile(r'^\+?1?\d{9,15}$')  # Adjust the regex as per your requirements

def token_required(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    token = None

    if 'Authorization' in request.headers:
      token = request.headers['Authorization'].split(" ")[1]

    if not token:
      return jsonify({'message': 'Token is missing!'}), 401

    try:
      data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
      current_user = User.query.get(data['user_id'])
    except:
      return jsonify({'message': 'Token is invalid!'}), 401

    return f(current_user, *args, **kwargs)

  return decorated

@auth_blueprint.route('/signup', methods=['POST'])
def signup():
  data = request.get_json()

  if not EMAIL_REGEX.match(data['email']):
    return jsonify({'message': 'Invalid email address'}), 400
  
  phone_number = data.get('phone_number')
  if phone_number and not PHONE_REGEX.match(phone_number):
    return jsonify({'message': 'Invalid phone number'}), 400

  # Check if user already exists
  existing_user_query = User.query.filter(User.email == data['email'])
  if phone_number:
    existing_user_query = existing_user_query.filter(User.phone_number == phone_number)

  existing_user = existing_user_query.first()
  if existing_user:
    return jsonify({'message': 'User with given email or phone number already exists'}), 409

  hashed_password = User.hash_password(data['password'])
  new_user = User(username=data['username'], email=data['email'], phone_number=phone_number, password_hash=hashed_password)
  
  db.session.add(new_user)
  db.session.commit()
  # Create a token for the new user
  token = jwt.encode({
    'user_id': new_user.id,
    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=5)  # Token expires in 1 hour
  }, current_app.config['SECRET_KEY'], algorithm="HS256")

  return jsonify({'message': 'Registered successfully', 'token': token}), 201

@auth_blueprint.route('/login', methods=['POST'])
def login():
  auth = request.authorization

  if not auth or not auth.username or not auth.password:
    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

  user = User.query.filter((User.username == auth.username) | (User.email == auth.username)).first()

  if not user:
    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

  if user.check_password(auth.password):
    token = jwt.encode({
      'user_id': user.id,
      'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=5)  # Token expires in 1 hour
    }, current_app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({'token': token})

  return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
