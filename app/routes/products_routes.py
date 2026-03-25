from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from app import db
from bson import ObjectId
from app.models.products import *
from app.decorators import token_required
from app.models.users import *

products_bp = Blueprint("products_bp", __name__)

#===== Products ======
# RF: O sistema deve permitir listagem de todos os produtos
@products_bp.route("/products", methods=["GET"])
@token_required
def get_products():
    products_cursor = db.products.find({})
    products_list = [
        ProductDBModel(**product).model_dump(by_alias=True, exclude_none=True)
        for product in products_cursor
    ]

    return jsonify(products_list)


# RF: O sistema deve permitir a criação de novos produtos
@products_bp.route("/products", methods=["POST"])
@token_required
def create_product(token):
    try:
        product = Product(**request.get_json())
    except ValidationError as e:
        return jsonify({"message": "Error on creating product"})

    result = db.products.insert_one(product.model_dump())

    return jsonify({"message": "Product created", "id": str(result.inserted_id)}), 201


# RF: O sistema deve permitir a visualização dos detalhes de cada produto
@products_bp.route("/product/<string:product_id>", methods=["GET"])
@token_required
def get_product_by_id(product_id):
    try:
        oid = ObjectId(product_id)
    except Exception as e:
        return jsonify(
            {"error": f"Erro ao transformar o : {product_id} em ObjectID: {e}"}
        )

    product = db.products.find_one({"_id": oid})

    if product:
        product_model = ProductDBModel(**product).model_dump(
            by_alias=True, exclude_none=True
        )
        return jsonify(product_model)
    else:
        return jsonify({"error": f"Produto não encontrado : {product_id} | {e}"})


# RF: O sistema deve permitir a atualização de cada produto
@products_bp.route("/product/<string:product_id>", methods=["PUT"])
@token_required
def update_product(token, product_id):
    try:
        oid = ObjectId(product_id)
        update_data = UpdateProduct(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.errors()})
    
    update_result = db.products.update_one(
        {
            {"_id": oid},
            {"$set": update_data.model_dump(exclude_unset=True)},
        }
    )

    if update_result.matched_count == 0:
        return jsonify({"error": "product not found"}), 404
    
    updated_product = db.products.find_one({"_id": oid})
    
    return jsonify(ProductDBModel(**updated_product).model_dump(by_alias=True, exclude=None))


# RF: O sistema deve permitir a deleção de cada produto
@products_bp.route("/products/<string:product_id>", methods=["DELETE"])
@token_required
def delete_product(token, product_id):
    try:
        oid = ObjectId(product_id)
    except:
        return jsonify({"error": "id product error"}), 400
    
    delete_product = db.products.delete_one({"_id": oid})

    if delete_product.deleted_count == 0:
        return jsonify({"error": "Product not found"}), 404

    return "", 204