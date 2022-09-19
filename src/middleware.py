from functools import wraps

import jwt
from flask import request
from jwt import InvalidSignatureError, ExpiredSignatureError

from src.models import UserModel
from src.config import BEARER_KEY


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        token = None

        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']

        if not token:
            return {"code": 401,
                    "success": False,
                    "message": "A valid token is missing"}, 401

        try:
            data = jwt.decode(token, BEARER_KEY, algorithms=["HS256"])
            current_user = UserModel.query.filter_by(id=data['id']).first()
            if current_user:
                return f(*args, **kwargs)
            else:
                return {"code": 401,
                        "success": False,
                        "message": "Token missing or invalid"}, 401

        except InvalidSignatureError:
            return {"code": 401,
                    "success": False,
                    "message": "Token invalid"}, 401

        except ExpiredSignatureError:
            return {"code": 401,
                    "success": False,
                    "message": "Token expired"}, 401

    return decorator
