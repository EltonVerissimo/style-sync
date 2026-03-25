from functools import wraps
from flask import request, jsonify, current_app

import jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'message': 'token malformado'})
            
        if not token:
            return jsonify({'message': 'token não encontrado'}), 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'token expirado'}), 401
        
        except jwt.InvalidTokenError:
            return jsonify({'message': 'token inválido'}), 401
        
        return f(data, *args, **kwargs)

    return decorated