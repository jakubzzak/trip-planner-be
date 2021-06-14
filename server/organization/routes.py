from datetime import datetime
from flask import request, Blueprint, Response, jsonify, make_response
from mongoengine import FieldDoesNotExist, ValidationError, NotUniqueError, DoesNotExist

from server import Config
from server.db.models import Person, Organization
from server.user import token_required

organizations = Blueprint('organizations', __name__, url_prefix='/api/organization')


@organizations.route("/create", methods=['PUT'])
@token_required
def create_organization(person: Person) -> Response:
    try:
        org = Organization(**request.get_json(), createdBy=person, createdAt=datetime.utcnow()).save()
        person.update(add_to_set__organizations=org)
        return make_response(jsonify(org.serialize()), 201)
    except FieldDoesNotExist as e:
        return make_response(jsonify(message=str(e)), 400)
    except ValidationError as e:
        return make_response(jsonify(message=e.message), 400)
    except NotUniqueError:
        return make_response(jsonify(message='Organization with such name already exists!'), 400)
    except Exception as e:
        print(str(e))
        return make_response(jsonify(message=Config.UNHANDLED_EXCEPTION_MESSAGE), 500)


@organizations.route('/<organizationId>/addMember/<userId>')
@token_required
def add_member(person: Person, organizationId: str, userId: str) -> Response:
    try:
        org = Organization.objects.get(id=organizationId)
        new_member = Person.objects.get(id=userId)
        if org and new_member:
            new_member.update(add_to_set__organizations=org)
            return make_response(jsonify(), 204)
        return make_response(jsonify(message='Organization or a person could not be found!'), 400)
    except DoesNotExist as e:
        return make_response(jsonify(message='Organization or a person could not be found!'), 400)
    except Exception as e:
        print(str(e))
    return make_response(jsonify(message=Config.UNHANDLED_EXCEPTION_MESSAGE), 500)


@organizations.route('/<organizationId>/removeMember/<userId>')
@token_required
def remove_member(person: Person, organizationId: str, userId: str) -> Response:
    try:
        org = Organization.objects.get(id=organizationId)
        member = Person.objects.get(id=userId)
        if org and member:
            if org.createdBy == person and member != person:
                member.update(pull__organizations=org)
                return make_response(jsonify(), 204)
            return make_response(jsonify(message='You do not have permission for this action!'), 403)
        return make_response(jsonify(message='Organization or a person could not be found!'), 400)
    except DoesNotExist as e:
        return make_response(jsonify(message='Organization or a person could not be found!'), 400)
    except Exception as e:
        print(str(e))
    return make_response(jsonify(message=Config.UNHANDLED_EXCEPTION_MESSAGE), 500)
