from app import db
from flask_bcrypt import Bcrypt
import uuid
from sqlalchemy.dialects.postgresql import UUID

bcrypt = Bcrypt()

class User(db.Model):
  __tablename__ = 'users'

  id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  username = db.Column(db.String(80), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password_hash = db.Column(db.String(128), nullable=False)
  phone_number = db.Column(db.Integer, unique=True, nullable=True)
  profile_pic = db.Column(db.String)
  peer_id = db.Column(db.String(128), nullable=True)
  is_online = db.Column(db.Boolean, default=False, nullable=True)
  language = db.Column(db.String(50),default='english', nullable=False)

  @staticmethod
  def hash_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

  def check_password(self, password):
    return bcrypt.check_password_hash(self.password_hash, password)