from bson import ObjectId
from flask import Blueprint, jsonify, request
from app.decorators import token_required
from app.models.category import Category
from app.models.users import LoginPayload
from pydantic import ValidationError
from app.models.category import *
from app import db

category_bp = Blueprint("category_bp", __name__)


# RF: O sitema deve permitir o cadastro de novas categorias
@category_bp.route("/category", methods=["POST"])
@token_required
def create_category(token):
    try:
        category = Category(**request.get_json())
    except ValidationError as e:
        return jsonify({"message": "Error on creating category"})

    result = db.categories.insert_one(category.model_dump())

    return jsonify({"message": "Category created", "id": str(result.inserted_id)}), 201


# RF: O sitema deve permitir a alterar os dados da categoria
@category_bp.route("/category/<string:category_id>", methods=["PUT"])
@token_required
def update_category(token, category_id):
    try:
        oid = ObjectId(category_id)
        update_data = UpdateCategory(**request.get_json())

    except ValidationError as e:
        return jsonify({"error": e.errors()})

    update_result = db.categories.update_one(
        {"_id": oid}, {"$set": update_data.model_dump(exclude_unset=True)}
    )

    if update_result.matched_count == 0:
        return jsonify({"error": "Category not found!"}), 404

    updated_category = db.categories.find_one({"_id": oid})

    return jsonify(
        CategoryDBModel(**updated_category).model_dump(by_alias=True, exclude=None)
    )


# RF: O sitema deve permitir a leitura de todas as categorias
@category_bp.route("/category", methods=["GET"])
@token_required
def get_categories(token):
    categories_cursor = db.categories.find({})
    categories_list = [
        CategoryDBModel(**category).model_dump(by_alias=True, exclude_none=True)
        for category in categories_cursor
    ]

    return jsonify(categories_list)


# RF: O sitema deve permitir a pesquisa de categorias
@category_bp.route("/category/search/<string:category_name>", methods=["GET"])
@token_required
def get_category_by_name(token, category_name):
    categories = db.categories.find({"name": category_name})

    if not categories:
        categories_list = [
            CategoryDBModel(**category).model_dump(by_alias=True, exclude_none=True)
            for category in categories
        ]

        return jsonify(categories_list)
    else:
        return jsonify({"message": f"Category not found!"})


# RF: O sitema deve permitir a deleção de categorias
@category_bp.route("/category/<string:category_id>", methods=["DELETE"])
@token_required
def delete_category(token, category_id):
    try:
        oid = ObjectId(category_id)
    except:
        return jsonify({"error": "id category error"}), 400

    delete_category = db.categories.delete_one({"_id": oid})

    if delete_category.deleted_count == 0:
        return jsonify({"error": "Category not found"}), 404

    return "", 204
