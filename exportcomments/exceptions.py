# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import


class ExportCommentsException(Exception):
    pass


class ExportCommentsLocalException(ExportCommentsException):
    pass


class LocalParamValidationError(ExportCommentsLocalException):
    pass


class ExportCommentsResponseException(ExportCommentsException):
    def __init__(self, status_code=500, detail='Internal server error',
                 error_code=None, response=None):
        self.detail = detail
        self.error_code = error_code
        self.status_code = status_code
        self.response = response

        message = 'Error'
        if error_code:
            message += ' {}'.format(error_code)
        message += ': {}'.format(detail)

        super(Exception, self).__init__(message)


# Request Validation Errors (422)


class RequestParamsError(ExportCommentsResponseException):
    pass


# Authentication (401)


class AuthenticationError(ExportCommentsResponseException):
    pass


# Forbidden (403)


class ForbiddenError(ExportCommentsResponseException):
    pass


class ModelLimitError(ForbiddenError):
    pass


# Not found Exceptions (404)


class ResourceNotFound(ExportCommentsResponseException):
    pass


class ModelNotFound(ResourceNotFound):
    pass


class TagNotFound(ResourceNotFound):
    pass


# Rate limit (429)


class PlanQueryLimitError(ExportCommentsResponseException):
    pass


class RateLimitError(ExportCommentsResponseException):
    pass


class PlanRateLimitError(RateLimitError):
    def __init__(self, seconds_to_wait=60, *args, **kwargs):
        self.seconds_to_wait = seconds_to_wait
        super(RateLimitError, self).__init__(*args, **kwargs)


class ConcurrencyRateLimitError(RateLimitError):
    pass


# State errors (423)


class ModelStateError(ExportCommentsResponseException):
    pass


RESPONSE_CODES_EXCEPTION_MAP = {
    422: RequestParamsError,
    401: AuthenticationError,
    403: {
        'MODEL_LIMIT': ModelLimitError,
        '*': ForbiddenError,
    },
    404: {
        'RESOURCE_NOT_FOUND': ResourceNotFound,
        '*': ResourceNotFound,
    },
    429: {
        'PLAN_RATE_LIMIT': PlanRateLimitError,
        'CONCURRENCY_RATE_LIMIT': ConcurrencyRateLimitError,
        'PLAN_QUERY_LIMIT': PlanQueryLimitError,
        '*': RateLimitError,
    },
    423: ModelStateError,
}


def get_exception_class(status_code, error_code=None):
    exception_or_dict = RESPONSE_CODES_EXCEPTION_MAP.get(status_code, ExportCommentsResponseException)
    if isinstance(exception_or_dict, dict):
        exception_class = exception_or_dict.get(error_code, exception_or_dict['*'])
    else:
        exception_class = exception_or_dict
    return exception_class
