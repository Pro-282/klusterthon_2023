import uuid
from sqlalchemy.dialects.postgresql import UUID
from app import db

class CallLog(db.Model):
  __tablename__ = 'call_logs'

  id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  sender_user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
  receiver_user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
  timestamp = db.Column(db.DateTime, nullable=False)
  duration = db.Column(db.Time, nullable=False)
  status = db.Column(db.String, nullable=False)