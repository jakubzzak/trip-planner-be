class UnauthorizedAccessException(Exception):

    def __init__(self, message: str = None):
        self.message = message if message is not None else 'Unauthorized access!'


class InvalidRequestException(Exception):

    def __init__(self, message: str = 'Invalid request!'):
        self.message = message


class RecordAlreadyExistsException(Exception):

    def __init__(self, value: str = None):
        self.message = f"Record with value {value} already exist!" if value is not None else f"Record already exist!"


class RecordNotFoundException(Exception):

    def __init__(self, value: str = None):
        self.message = f"Record with value {value} does not exist!" if value is not None else f"Record does not exist!"


class WrongFormatException(Exception):

    def __init__(self, value: str = None):
        self.message = f"Value of {value} has incorrect format!" if value is not None else f"Incorrect format provided!"


class PermissionDeniedException(Exception):

    def __init__(self):
        self.message = f"You do not have permission to execute this action!"
