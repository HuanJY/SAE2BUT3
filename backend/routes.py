from flask import Blueprint, request, jsonify
from models import db, User, Chat, Message
import bcrypt
from utils import generate_token, verify_token

bp = Blueprint('routes', __name__)

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email déjà utilisé'}), 409

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user = User(firstname=firstname, lastname=lastname, email=email, password=hashed_password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Utilisateur créé avec succès'}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        token = generate_token(user.user_id)
        return jsonify({'token': token}), 200

    return jsonify({'error': 'Identifiants invalides'}), 401

@bp.route('/chats', methods=['GET'])
def get_chats():
    token = request.headers.get('Authorization').split(" ")[1]
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Token invalide ou expiré'}), 401

    chats = Chat.query.filter_by(user_id=user_id).all()
    return jsonify([
        {
            'chat_id': chat.chat_id,
            'title': chat.title,
            'create_time': chat.create_time,
            'last_message': chat.messages[-1].content if chat.messages else None
        } for chat in chats
    ]), 200

@bp.route('/chats', methods=['POST'])
def create_chat():
    token = request.headers.get('Authorization').split(" ")[1]
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Token invalide ou expiré'}), 401

    data = request.get_json()
    title = data.get('title', 'Nouvelle conversation')

    chat = Chat(title=title, user_id=user_id)
    db.session.add(chat)
    db.session.commit()

    return jsonify({'chat_id': chat.chat_id, 'title': chat.title, 'create_time': chat.create_time}), 201

@bp.route('/chats/<int:chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    token = request.headers.get('Authorization').split(" ")[1]
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Token invalide ou expiré'}), 401

    chat = Chat.query.filter_by(chat_id=chat_id, user_id=user_id).first()
    if not chat:
        return jsonify({'error': 'Conversation introuvable'}), 404

    db.session.delete(chat)
    db.session.commit()
    return jsonify({'message': 'Conversation supprimée avec succès'}), 200

@bp.route('/chats/<int:chat_id>/messages', methods=['GET'])
def get_messages(chat_id):
    token = request.headers.get('Authorization').split(" ")[1]
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Token invalide ou expiré'}), 401

    chat = Chat.query.filter_by(chat_id=chat_id, user_id=user_id).first()
    if not chat:
        return jsonify({'error': 'Conversation introuvable'}), 404

    messages = chat.messages
    return jsonify([{'message_id': message.message_id, 'content': message.content, 'is_user': message.is_user, 'create_time': message.create_time} for message in messages]), 200

@bp.route('/chats/<int:chat_id>/messages', methods=['POST'])
def create_message(chat_id):
    token = request.headers.get('Authorization').split(" ")[1]
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Token invalide ou expiré'}), 401

    chat = Chat.query.filter_by(chat_id=chat_id, user_id=user_id).first()
    if not chat:
        return jsonify({'error': 'Conversation introuvable'}), 404

    data = request.get_json()
    content = data.get('content')
    if not content:
        return jsonify({'error': 'Le contenu du message est requis'}), 400
    
    is_user = data.get('is_user')
    if is_user is None:
        return jsonify({'error': 'is_user est requis'}), 400
    if not isinstance(is_user, bool):
        return jsonify({'error': 'is_user doit être un booléen'}), 400

    message = Message(content=content, chat_id=chat_id, is_user=is_user)
    full_response = f"Tu as dit : {content}"
    response = Message(content=full_response, chat_id=chat_id, is_user=False)
    
    db.session.add(message)
    db.session.add(response)
    db.session.commit()

    return jsonify({'message_id': response.message_id, 'content': response.content, 'is_user': response.is_user, 'create_time': response.create_time}), 201