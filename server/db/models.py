from datetime import datetime, timedelta
from enum import Enum

import jwt
from mongoengine import StringField, EmailField, DateField, ReferenceField, IntField, BooleanField, \
    ListField, EnumField, DateTimeField, EmbeddedDocumentListField, FloatField, EmbeddedDocumentField
import mongoengine_goodjson as gj
import json

from server import login_manager, Config


class Organization(gj.Document):
    meta = {
        'collection': 'organizations'
    }

    name = StringField(required=True, unique=True)
    createdAt = DateField(required=True)
    createdBy = ReferenceField('Person', required=True)
    # trips = ListField(ReferenceField('Trip'))
    # people = ListField(ReferenceField('Person'))

    def __str__(self):
        return f"Organization({self.name}, created by {self.createdBy} at {self.createdAt})"

    def serialize(self):
        return json.loads(self.to_json())


class MeanOfTransport(Enum):
    AIRPLANE = 'airplane'
    TRAIN = 'train'
    CAR = 'car'
    BUS = 'bus'
    BOAT = 'boat'
    BIKE = 'bike'
    UNKNOWN = 'unknown'


class Transport(gj.EmbeddedDocument):

    mean = EnumField(MeanOfTransport, required=True, default=MeanOfTransport.UNKNOWN)
    leavesAt = DateTimeField(required=True)
    arrivesAt = DateTimeField()
    cityFrom = StringField(required=True)
    cityTo = StringField(required=True)
    note = StringField()
    amount = FloatField(required=True, min_value=0)

    def __str__(self):
        return f"Transport({self.mean}, [{self.cityFrom}({self.leavesAt}) - {self.cityTo}({self.arrivesAt})])"

    def serialize(self):
        return json.loads(self.to_json())


class Accommodation(gj.EmbeddedDocument):

    city = StringField(required=True)
    dateFrom = DateField(required=True)
    dateTo = DateField(required=True)
    note = StringField()
    amount = FloatField(required=True, min_value=0)

    def __str__(self):
        return f"Accommodation({self.city}, [{self.dateFrom} - {self.dateTo}])"

    def serialize(self):
        return json.loads(self.to_json())


class Todo(gj.EmbeddedDocument):

    title = StringField(required=True)
    amount = FloatField(required=True, min_value=0)
    note = StringField()

    def __str__(self):
        return f"Todo({self.title}, {self.amount}€)"

    def serialize(self):
        return json.loads(self.to_json())


class Vote(gj.EmbeddedDocument):

    person = ReferenceField('Person', required=True)
    points = IntField(required=True, min_value=0)

    def __str__(self):
        return f"Vote({self.person.firstName} {self.person.lastName}, points={self.points})"

    def serialize(self):
        return json.loads(self.to_json())


class Amounts(gj.EmbeddedDocument):

    foodAndDrinks = FloatField(required=True, min_value=0, default=0)
    gettingAround = FloatField(required=True, min_value=0, default=0)
    totalEstimate = FloatField(required=True, min_value=0, default=0)
    totalFinal = FloatField(min_value=0, default=0)

    def __str__(self):
        return f"Amount(est={self.totalEstimate}€, final={self.totalFinal}€)"

    def serialize(self):
        return json.loads(self.to_json())


class Trip(gj.Document):
    meta = {
        'collection': 'trips'
    }

    name = StringField(required=True, unique_with=['survey'])
    votes = EmbeddedDocumentListField(Vote, default=[])
    accepted = BooleanField(required=True, default=False)
    createdAt = DateField(required=True)
    createdBy = ReferenceField('Person', required=True)
    place = StringField(required=True)
    dateFrom = DateField(required=True)
    dateTo = DateField(required=True)
    accommodation = EmbeddedDocumentListField(Accommodation, default=[])
    transportsThere = EmbeddedDocumentListField(Transport, default=[])
    transportsBack = EmbeddedDocumentListField(Transport)
    todos = EmbeddedDocumentListField(Todo)
    participants = ListField(ReferenceField('Person'), required=True, default=[])
    survey = ReferenceField('TripSurvey', required=True)
    amounts = EmbeddedDocumentField(Amounts)
    note = StringField()

    def __str__(self):
        return f"Trip({self.name}, created by {self.createdBy} at {self.createdAt})"

    def serialize(self):
        return json.loads(self.to_json())


class Statistics(gj.EmbeddedDocument):

    tripsCount = IntField(required=True, min_value=0, default=0)
    tripsVoted = IntField(required=True, min_value=0, default=0)
    lengthInDays = IntField(required=True, min_value=0, default=0)
    votePointsGiven = IntField(required=True, min_value=0, default=0)
    tripsVoteSorted = ListField(ReferenceField(Trip), default=[])

    def __str__(self):
        return f"Statistics(trips#={self.tripsCount}, tripsVoted={self.tripsVoted}, length={self.lengthInDays}, votePoints={self.votePointsGiven})"

    def serialize(self):
        return json.loads(self.to_json())


class TripSurvey(gj.Document):
    meta = {
        'collection': 'tripSurveys'
    }

    title = StringField(required=True, unique_with=['organization'])
    trips = ListField(ReferenceField(Trip), default=[])
    statistics = EmbeddedDocumentField(Statistics)
    organization = ReferenceField(Organization, required=True)
    createdAt = DateField(required=True)
    createdBy = ReferenceField('Person', required=True)
    tripsPerPerson = IntField(required=True, min_value=1, default=1)
    openUntil = DateField(required=True)

    def __str__(self):
        return f"TripSurvey({self.title}, created by {self.createdBy} until {self.openUntil}, tpp={self.tripsPerPerson})"

    def serialize(self):
        return json.loads(self.to_json())


class Person(gj.Document):
    meta = {
        'collection': 'people'
    }

    firstName = StringField(required=True)
    lastName = StringField(required=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    createdAt = DateField(required=True)
    organizations = ListField(ReferenceField(Organization))
    trips = ListField(ReferenceField(Trip))
    friends = ListField(ReferenceField('self'))

    def __repr__(self):
        return f"Person({self.firstName} {self.lastName}, {self.email})"

    def __str__(self):
        return f"Person({self.firstName} {self.lastName}, {self.email})"

    def serialize(self):
        obj = json.loads(self.to_json())
        del obj['password']
        return obj

    def generate_token(self) -> str:
        return jwt.encode({'firstName': self.firstName,
                           'lastName': self.lastName,
                           'email': self.email,
                           'exp': datetime.utcnow() + timedelta(minutes=100)},
                          Config.SECRET_KEY)


@login_manager.request_loader
def load_user(request):
    token = request.headers.get('Authorization')
    if token is None:
        token = request.args.get('token')

    if token is not None:
        username, password = token.split(":")  # naive token
        # user_entry = Person.get(username)
        # if (user_entry is not None):
        #     user = User(user_entry[0], user_entry[1])
        #     if (user.password == password):
        #         return user
    return None
