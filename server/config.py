from dotenv import load_dotenv
import os
from flask import Response, json, session

from server.main.exceptions import UnauthorizedAccessException

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # DATABASE_URI = os.environ.get('DATABASE_URI')
    MONGODB_SETTINGS = {
        'host': os.environ.get('DATABASE_URI')
    }

    MAIL_SERVER = 'smtp.websupport.sk'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    MAIL_SENDER_NAME = os.environ.get('EMAIL_SENDER_NAME')
    MAIL_OVERRIDE = os.environ.get('OVERRIDE_EMAIL')

    UNHANDLED_EXCEPTION_MESSAGE = os.environ.get('UNHANDLED_EXCEPTION_MESSAGE') \
        if os.environ.get('UNHANDLED_EXCEPTION_MESSAGE') is not None \
        else 'Ups! Unhandled exception occurred.'


class CustomResponse:

    def __init__(self, data: any = None, error: str = None, librarian_level: bool = False):
        if librarian_level and session.get('login_type') != 'librarian':
            self.ok = False
            self.data = None
            self.error = None
            raise UnauthorizedAccessException

        self.ok = True
        self.data = data
        self.error = error

    def get_data(self):
        return self.data

    def set_data(self, value: any) -> None:
        self.error = None
        self.data = value
        self.ok = True

    def set_error(self, value: str) -> None:
        self.data = None
        self.error = value
        self.ok = False

    def __repr__(self):
        return f"CustomResponse(ok={self.ok} data={self.data}, error={self.error})"

    def get_response(self, status: int = None) -> Response:
        return Response(json.dumps({"ok": self.ok, "data": self.data, "error": self.error}),
                        status=status if status is not None else 200 if self.ok else 406, mimetype='application/json')
