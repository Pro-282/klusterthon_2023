from app import db
from app.users.models import User

class CallLog(db.Model):
    __tablename__ = 'call_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Time, nullable=False)
    status = db.Column(db.String, nullable=False)