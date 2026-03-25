from flask import Blueprint, jsonify, request
from app.models.category import Category
from app.models.users import LoginPayload
from pydantic import ValidationError
from app import db

category_bp = Blueprint("category_bp", __name__)

# RF: O sitema deve permitir o cadastro de novas categorias
@category_bp.route("/category", methods=["POST"])
def create_category(token):
    try:
        category = Category(**request.get_json())
    except ValidationError as e:
        return jsonify({"message": "Error on creating category"})

    result = db.categories.insert_one(category.model_dump())

    return jsonify({"message": "Category created", "id": str(result.inserted_id)}), 201

# RF: O sitema deve permitir a deleção de categorias
@category_bp.route("/category/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    return jsonify({"message": f"Delete category id: {category_id}"})

# RF: O sitema deve permitir a alterar os dados da categoria
@category_bp.route("/category/<int:category_id>", methods=["PUT"])
def update_category(category_id):
    return jsonify({"message": f"Update category id: {category_id}"})

# RF: O sitema deve permitir a leitura de todas as categorias
@category_bp.route("/category", methods=["GET"])
def get_categories():
    return jsonify({"message": "List categories"})

# RF: O sitema deve permitir a pesquisa de categorias
@category_bp.route("/category/<string:category>", methods=["GET"])
def get_category_by_name(category):
    return jsonify({"message": f"Category: {category}"})