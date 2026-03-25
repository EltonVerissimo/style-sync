from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from app import db
from app.models.products import *
from app.decorators import token_required
from app.models.users import *

user_bp = Blueprint("user_bp", __name__)

# RF: O sistema deve permitir o cadastro de novos usuários
@user_bp.route('/users', methods=['POST'])
@token_required
def create_user(token):
    try:
        user = User(**request.get_json())
    except ValidationError as e:
        return jsonify({"message": "Error on creating user"})

    result = db.users.insert_one(user.model_dump())

    return jsonify({"message": "User created", "id": str(result.inserted_id)}), 201

# RF: O sistema deve permitir a listagem dos usuários
@user_bp.route('/users', methods=['GET'])
@token_required
def get_users(token):
    users_cursor = db.users.find({})
    users_list = [UserDBModel(**user).model_dump(by_alias=True, exclude_none=True) for user in users_cursor]

    for user in users_cursor:
        user['_id'] = str(user['_id'])
        users_list.append(user)

    return jsonify(users_list), 200

# RF: O sistema deve permitir a deleção de usuários
@user_bp.route('/users/<string:user_id>', methods=['DELETE'])
@token_required
def delete_user(token, user_id):
    try:
        oid = ObjectId(user_id)
    except:
        return jsonify({"error": "user_id error"}), 400
    
    delete_user = db.users.delete_one({"_id": oid})

    if delete_user.deleted_count == 0:
        return jsonify({"error": "Users not found"}), 404

    return "", 204