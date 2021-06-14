from datetime import datetime

from flask import request, Blueprint, Response, make_response, jsonify
from mongoengine import FieldDoesNotExist, ValidationError, NotUniqueError, DoesNotExist

from server import Config
from server.db.models import Person, Trip, TripSurvey, Organization
from server.trip import close_survey
from server.user import token_required

trips = Blueprint('trips', __name__, url_prefix='/api/trip')


@trips.route("/create", methods=['PUT'])
@token_required
def create_trip(person: Person):
    try:
        survey = TripSurvey.objects.get(id=request.get_json().get('surveyId'))
        if not survey:
            raise DoesNotExist
        del request.json['surveyId']
        trip = Trip(**request.get_json(), createdBy=person, createdAt=datetime.utcnow(), survey=survey).save()
        person.update(add_to_set__trips=trip)
        return make_response(jsonify(trip.serialize()), 201)
    except FieldDoesNotExist as e:
        return make_response(jsonify(message=str(e)), 400)
    except ValidationError as e:
        return make_response(jsonify(message=e.message), 400)
    except NotUniqueError:
        return make_response(jsonify(message='Trip with such name already exists!'), 400)
    except DoesNotExist as e:
        return make_response(jsonify(message='Referenced trip survey could not be found!'), 400)
    except Exception as e:
        print(str(e))
        return make_response(jsonify(message=Config.UNHANDLED_EXCEPTION_MESSAGE), 500)


@trips.route('/<tripId>/addParticipant/<userId>')
@token_required
def add_member(person: Person, tripId: str, userId: str) -> Response:
    try:
        trip = Trip.objects.get(id=tripId)
        new_member = Person.objects.get(id=userId)
        if trip and new_member and trip.organization in new_member.organizations:
            new_member.update(add_to_set__trips=trip)
            return make_response(jsonify(), 204)
        return make_response(jsonify(message='Trip or a person could not be found or the person '
                                             'does not belong to this organization!'), 400)
    except DoesNotExist as e:
        return make_response(jsonify(message='Trip or a person could not be found!'), 400)
    except Exception as e:
        print(str(e))
    return make_response(jsonify(message=Config.UNHANDLED_EXCEPTION_MESSAGE), 500)


@trips.route('/<tripId>/removeParticipant/<userId>')
@token_required
def remove_member(person: Person, tripId: str, userId: str) -> Response:
    try:
        trip = Trip.objects.get(id=tripId)
        member = Person.objects.get(id=userId)
        if trip and member:
            if (trip.createdBy == person or trip.organization.createdBy == person) and member != person:
                member.update(pull__trips=trip)
                return make_response(jsonify(), 204)
            return make_response(jsonify(message='You do not have permission for this action!'), 403)
        return make_response(jsonify(message='Trip or a person could not be found!'), 400)
    except DoesNotExist as e:
        return make_response(jsonify(message='Trip or a person could not be found!'), 400)
    except Exception as e:
        print(str(e))
    return make_response(jsonify(message=Config.UNHANDLED_EXCEPTION_MESSAGE), 500)


@trips.route('/survey/create', methods=['PUT'])
@token_required
def create_survey(person: Person) -> Response:
    try:
        org = Organization.objects.get(id=request.get_json().get('organizationId'))
        if not org:
            raise DoesNotExist
        del request.json['organizationId']
        survey = TripSurvey(**request.get_json(), createdBy=person, createdAt=datetime.utcnow(), organization=org).save()
        return make_response(jsonify(survey.serialize()), 201)
    except DoesNotExist as e:
        return make_response(jsonify(message='Organization could not be found!'), 400)
    except (FieldDoesNotExist, ValidationError) as e:
        return make_response(jsonify(message='Wrong data format!'), 400)
    except NotUniqueError as e:
        return make_response(jsonify(message='Survey with this title already exists within your organization!'), 400)
    except Exception as e:
        print(str(e))
    return make_response(jsonify(message=Config.UNHANDLED_EXCEPTION_MESSAGE), 500)


@trips.route('/survey/<surveyId>/close')
@token_required
def close_survey(person: Person, surveyId: str) -> Response:
    try:
        survey = TripSurvey.objects.get(id=surveyId)
        if not survey:
            raise DoesNotExist
        if person == survey.createdBy:
            close_survey()
            return make_response(jsonify(survey.serialize()))
        return make_response(jsonify(message='You do not have permission for this action!'), 403)
    except DoesNotExist as e:
        return make_response(jsonify(message='Organization could not be found!'), 400)
    except (FieldDoesNotExist, ValidationError) as e:
        return make_response(jsonify(message='Wrong data format!'), 400)
    except Exception as e:
        print(str(e))
    return make_response(jsonify(message=Config.UNHANDLED_EXCEPTION_MESSAGE), 500)
