from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from flask_cors import CORS
from flask_socketio import SocketIO

db = SQLAlchemy()
socketio = SocketIO()

def create_app(config_name):
  app = Flask(__name__)
  app.config['SECRET_KEY'] = '123edfyre34rtyhjuyt67uju7655t'
  # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
  app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  app.config['SQLALCHEMY_POOL_SIZE'] = 10
  app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30
  app.config['SQLALCHEMY_POOL_RECYCLE'] = 1800

  CORS(app, resources=[r'/api/*', r'/*', r'/socket.io/'], origins=["http://localhost:5173/*", "https://callee.vercel.app/*"])

  db.init_app(app)
  migrate = Migrate(app, db)

  socketio.init_app(app, cors_allowed_origins="*")

  # Import blueprints
  from app.health import health_blueprint
  from app.auth.views import auth_blueprint
  from app.socket.views import socket_blueprint
  from app.users.views import users_blueprint

  app.register_blueprint(health_blueprint)
  app.register_blueprint(auth_blueprint, url_prefix='/api/auth')
  app.register_blueprint(socket_blueprint, url_prefix='/')
  app.register_blueprint(users_blueprint, url_prefix='/api/user')

  with app.app_context():
      from app.users.models import User
      from app.calls.models import CallLog

  return app
