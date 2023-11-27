from flask import Blueprint, request, jsonify, current_app
from app import db
from app.auth.views import token_required
from app.users.models import User

users_blueprint = Blueprint('user', __name__)

@token_required
@users_blueprint.route('/all_users', methods=['GET'])
def all_users():
    all_users = User.query.all()
    all_users_list = [{'id': user.id,
                      'username': user.username,
                      'email': user.email,
                      'phone_number': user.phone_number,
                      'profile_pic': user.profile_pic,
                      'peer_id': user.peer_id,
                      'is_online': user.is_online,
                      'language': user.language} for user in all_users]
    return jsonify(all_users_list)