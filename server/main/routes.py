from flask import request, session, Blueprint, Response
from sqlalchemy.exc import IntegrityError

from server import db
from server.config import CustomResponse, InvalidRequestException, Config

main = Blueprint('main', __name__, url_prefix='/api')


@main.route("/sendMail", methods=['POST'])
def send_mail() -> Response:
    res = CustomResponse()
    try:
        t_db = db['test_database']
        t_coll = t_db['test_collection']
        my_data = None
        for key in t_coll.find():
            my_data = key.get('test_data')

        res.set_data(my_data)
    except InvalidRequestException as e:
        # db.session.rollback()
        res.set_error(e.message)
    except IntegrityError as e:
        # db.session.rollback()
        res.set_error(Config.UNHANDLED_EXCEPTION_MESSAGE)
    return res.get_response()
