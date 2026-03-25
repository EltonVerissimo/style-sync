from flask import Blueprint, jsonify, request, current_app
from app.models.users import LoginPayload
from app.models.sale import Sale
from pydantic import ValidationError
from app import db
from app.models.products import *
from app.decorators import token_required
from datetime import datetime, timedelta, timezone
from app.models.users import *

import jwt
import csv

main_bp = Blueprint("main_bp", __name__)

#===== Login ======
# RF: O sistema deve permitir que um usuário se autentique para obter um token
@main_bp.route("/login", methods=["POST"])
def login():
    try:
        raw_data = request.get_json()
        user_data = LoginPayload(**raw_data)

    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    except Exception as e:
        jsonify({"error": "Request error"}), 500

    if user_data.username == "admin" and user_data.password == "1234":
        tonken = jwt.encode(
            {
                "user_id": user_data.username,
                "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
            },
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

        return jsonify({"access_token": tonken}), 200
    return jsonify({"message": "Bad credentials"}), 401


# RF: O sistema deve permitir a importação de vendas através de um arquivo
@main_bp.route("/sales/upload", methods=["POST"])
@token_required
def upload_sales(token):
    if 'file' not in request.files:
        return jsonify({"error": "No file sent"})
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if file and file.filename.endswith('.csv'):
        import io

        csv_stream = io.StringIO(file.stream.read().decode('UTF-8'), newline=None)
        csv_reader = csv.DictReader(csv_stream)

        sales_to_insert = []
        errors = []

        for row_num, row in enumerate(csv_reader, 1):
            try:
                sale_data = Sale(**row)
                sales_to_insert.append(sale_data.model_dump())

            except ValidationError as e:
                errors.append(f"Linha {row_num}: Invalid data - {e.errors()}")
            except Exception as e:
                errors.append(f"Linha {row_num}: Unspected error in line - {str(e)}")
            
        if sales_to_insert:
            try:
                db.sales.insert_many(sales_to_insert)
            except Exception as e:
                return jsonify({"error": f"Error on data inserting: {str(e)}"}), 500
        
        return jsonify({
            "message": "Files uploaded successfuly.",
            "Sales imported": len(sales_to_insert),
            "Errors": errors
        }), 200