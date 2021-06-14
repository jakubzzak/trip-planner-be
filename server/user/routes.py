import json

from flask import request, Blueprint, Response, render_template, make_response, jsonify
from mongoengine import ValidationError, NotUniqueError, DoesNotExist

from server import bcrypt, Config
from server.db.models import Person
from server.mail import send_mail
from server.main.exceptions import WrongFormatException, PermissionDeniedException
from server.user import token_required

users = Blueprint('users', __name__, url_prefix='/api/user')


@users.route("/register", methods=['PUT'])
def register() -> Response:
    try:
        password = request.get_json().get('password')
        if not password or len(password) < 8:
            raise WrongFormatException('password')
        pw_hash = bcrypt.generate_password_hash(password=password)
        request.json['password'] = pw_hash
        person = Person(**request.get_json()).save()

        success = send_mail(subject='Account created',
                            recipient_email=person.email,
                            html=render_template('confirm_registration.html', name=person.firstName))
        if success:
            return jsonify({'token': person.generate_token()})
    except WrongFormatException as e:
        return Response(json.dumps({'message': e.message}), mimetype='application/json', status=400)
    except NotUniqueError:
        return Response(json.dumps({'message': 'User with entered email already exists!'}), mimetype='application/json',
                        status=400)
    return Response(mimetype='application/json', status=500)


@users.route("/login", methods=['POST'])
def login() -> Response:
    try:
        person = Person.objects.get(email=request.json.get('email'))
        if person and bcrypt.check_password_hash(person.password, request.json.get('password')):
            return jsonify({'token': person.generate_token()})
    except Exception as e:
        print(str(e))
    return make_response('Wrong credentials!', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})


@users.route("/logout")
@token_required
def logout(person: Person) -> Response:
    return jsonify()


@users.route('/dashboard')
@token_required
def load_dashboard(person: Person):
    return jsonify(person.serialize())


@users.route('/addFriend/<userId>')
@token_required
def add_friend(person: Person, userId: str) -> Response:
    try:
        friend = Person.objects.get(id=userId)
        if not friend:
            raise DoesNotExist
        if friend == person:
            raise PermissionDeniedException
        friend.update(add_to_set__friends=[person])
        person.update(add_to_set__friends=[friend])
        person.reload()
        return jsonify(person.serialize())
    except PermissionDeniedException as e:
        return make_response(jsonify(message=e.message), 403)
    except (DoesNotExist, ValidationError) as e:
        return make_response(jsonify(message='User you referenced does not exist!'), 400)
    except Exception as e:
        print(str(e))
    return make_response(jsonify(message=Config.UNHANDLED_EXCEPTION_MESSAGE), 500)


@users.route('/removeFriend/<userId>')
@token_required
def remove_friend(person: Person, userId: str) -> Response:
    try:
        friend = Person.objects.get(id=userId)
        if not friend:
            raise DoesNotExist

        friend.update(pull__friends=person)
        person.update(pull__friends=friend)
        person.reload()
        return jsonify(person.serialize())
    except (DoesNotExist, ValidationError) as e:
        return make_response(jsonify(message='User you referenced does not exist!'), 400)
    except Exception as e:
        print(str(e))
    return make_response(jsonify(message=Config.UNHANDLED_EXCEPTION_MESSAGE), 500)
