from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(64), nullable=False)
    lastname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    chats = db.relationship('Chat', backref='user', lazy=True)

class Chat(db.Model):
    __tablename__ = 'chat'

    chat_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    create_time = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

    messages = db.relationship('Message', backref='chat', lazy=True, order_by='Message.create_time.asc()')

class Message(db.Model):
    __tablename__ = 'message'

    message_id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(5000), nullable=False)
    is_user = db.Column(db.Boolean, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.chat_id'), nullable=False)
    context = db.Column(db.String(5000), nullable=True) # Only the "assistant" role uses this field
