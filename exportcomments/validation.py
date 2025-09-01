# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from exportcomments.exceptions import LocalParamValidationError
import re
import six


ORDER_BY_FIELD_RE = re.compile(r'^-?[a-z_]+$')


# NOTE: This function is deprecated in API v3 as order_by is no longer supported
# Kept for backward compatibility
def validate_order_by_param(order_by_param):
    """
    DEPRECATED: This function is deprecated in API v3.
    The new API v3 does not support order_by parameters.
    This function is kept for backward compatibility only.
    """
    def validate_order_by_field(order_by_field):
        if ',' in order_by_field:
            raise LocalParamValidationError(
                                            "'order_by' parameter has an invalid ',' (comma) character, try sending a list of "
                                            "strings if you need to specify multiple fields."
                                            )
        if not ORDER_BY_FIELD_RE.match(order_by_field):
            raise LocalParamValidationError(
                                            "'order_by' parameter as a string must be a valid field name, invalid characters "
                                            "where found."
                                            )
        return order_by_field

    order_by = []

    if isinstance(order_by_param, six.string_types):
        order_by.append(validate_order_by_field(order_by_param))
    else:
        try:
            order_by_param = list(order_by_param)
        except TypeError:
            raise LocalParamValidationError(
                                            "'order_by' parameter must be a string or a list (or iterable) of strings"
                                            )

        if not len(order_by_param):
            raise LocalParamValidationError(
                                            "'order_by' parameter must be a list (or iterable) of at least one string"
                                            )

        seen_fields = set()
        for order_by_field in order_by_param:
            if not isinstance(order_by_field, six.string_types):
                raise LocalParamValidationError(
                                                "'order_by' parameter must be a list (or iterable) of strings, non-string"
                                                "values were found"
                                                )

            order_by_field = validate_order_by_field(order_by_field)

            if order_by_field in seen_fields:
                raise LocalParamValidationError(
                                                "'order_by' parameter must be a list unique field names, duplicated fields "
                                                "where found."
                                                )

            order_by.append(order_by_field)

    return ','.join(order_by)
