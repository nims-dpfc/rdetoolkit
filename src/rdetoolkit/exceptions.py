# ---------------------------------------------------------
# Copyright (c) 2022, Materials Data Platform Center, NIMS
#
# This software is released under the MIT License.
# ---------------------------------------------------------
# coding: utf-8

from functools import wraps


class StructuredError(Exception):
    def __init__(self, eMsg: str = "", eCode=1, eObj=None):
        self.eMsg = eMsg
        self.eCode = eCode
        self.eObj = eObj


def catch_exception_with_message(errro_message):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                raise StructuredError(errro_message, eObj=e)

        return wrapper

    return decorator
