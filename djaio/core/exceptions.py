# -*- coding: utf-8 -*-


class BaseApiException(Exception):
    status_code = None
    message = None
    detail = None

    def to_dict(self):
        _output = {
            'code': self.status_code,
            'message': self.message
        }
        if self.detail:
            _output.update({'detail': self.detail})
        return _output


class ObjectAlreadyExistException(BaseApiException):
    status_code = 409
    message = 'Object with provided data already exist'


class ObjectNotFoundException(BaseApiException):
    # ToDo rewrite _id to key in next release
    status_code = 404
    message = 'Object with KEY %s not found'

    def __init__(self, _id, *args, **kwargs):
        self.message = self.message % _id
        super().__init__(args, kwargs)


class BadRequestException(BaseApiException):
    status_code = 400

    def __init__(self, *args, **kwargs):
        self.message = kwargs.get('message')
        super().__init__(args, kwargs)


class UnauthorizedException(BaseApiException):
    status_code = 401
    message = 'Can not authorized with provided data'


class ForbiddenException(BaseApiException):
    status_code = 403

    def __init__(self, *args, **kwargs):
        self.message = kwargs.get('message', 'forbidden')
        super().__init__(args, kwargs)


class TooManyRequestsException(BaseApiException):
    status_code = 429
    message = 'too many requests'
