from flask import Blueprint, jsonify
from server.db.models import Person, Organization, Trip, TripSurvey

v1 = Blueprint('v1', __name__, url_prefix='/v1')


@v1.route("/organizations")
def list_organizations():
    organizations = Organization.objects
    return jsonify(list(map(lambda organization: organization.serialize(), organizations)))


@v1.route("/surveys")
def list_surveys():
    surveys = TripSurvey.objects
    return jsonify(list(map(lambda survey: survey.serialize(), surveys)))


@v1.route("/trips")
def list_trips():
    trips = Trip.objects
    return jsonify(list(map(lambda trip: trip.serialize(), trips)))


@v1.route("/people")
def list_people():
    people = Person.objects
    return jsonify(list(map(lambda person: person.serialize(), people)))
