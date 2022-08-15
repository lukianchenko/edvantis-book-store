from functools import wraps

import jwt
from flask import request

from models import UserModel


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        token = None

        if 'x-api-key' in request.headers:
            token = request.headers['x-api-key']

        if not token:
            return {"code": 401,
                    "success": False,
                    "message": "A valid token is missing"}, 401

        try:
            data = jwt.decode(jwt, key=token, algorithms=["HS256", ])
            current_user = UserModel.query.filter_by(id=data['id']).first()
        except ValueError:
            return {"code": 401,
                    "success": False,
                    "message": "Token is invalid"}, 401

            return f(current_user, *args, **kwargs)

    return decorator
