from flask import jsonify, request
from server import Config
import jwt
from server.db.models import Person
from functools import wraps


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            auth = request.headers.get('Authorization')
            if auth:
                token = auth.split(" ")[1]
            else:
                token = None

            if not token:
                return jsonify({'message': 'Token is missing!'}), 403
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            person = Person.objects.get(email=data.get('email'), firstName=data.get('firstName'), lastName=data.get('lastName'))
        except Exception as e:
            print(str(e))
            return jsonify({'message': 'Token is invalid!'}), 403
        return f(*args, person, **kwargs)
    return decorated
