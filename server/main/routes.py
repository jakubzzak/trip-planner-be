import json

from flask import request, Blueprint, Response, render_template


from server.db.models import Person

main = Blueprint('main', __name__, url_prefix='/api')


@main.route("/people")
def get_people() -> Response:
    people = Person.objects
    return Response(json.dumps([person.serialize() for person in people]), mimetype='application/json', status=200)


@main.route("/testCreate", methods=['POST'])
def create_person() -> Response:
    person = Person(**request.get_json()).save()
    return Response(json.dumps(person.serialize()), mimetype='application/json', status=201)
