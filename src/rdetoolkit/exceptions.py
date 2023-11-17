# ---------------------------------------------------------
# Copyright (c) 2022, Materials Data Platform Center, NIMS
#
# This software is released under the MIT License.
# ---------------------------------------------------------
# coding: utf-8

from functools import wraps
from typing import Optional


class StructuredError(Exception):
    def __init__(self, eMsg: str = "", eCode=1, eObj=None):
        super().__init__(eMsg)
        self.eMsg = eMsg
        self.eCode = eCode
        self.eObj = eObj


def catch_exception_with_message(*, errro_message: Optional[str] = None, error_code: Optional[int] = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except StructuredError as e:
                if errro_message is not None:
                    msg = errro_message
                else:
                    msg = str(e)

                if error_code is not None:
                    eCode = error_code
                else:
                    eCode = 1

                raise StructuredError(msg, eCode=eCode, eObj=e)

            except Exception as e:
                if errro_message is not None:
                    msg = errro_message
                else:
                    msg = str(e)
                raise Exception(msg)

        return wrapper

    return decorator
