import pytest
from rdetoolkit.exceptions import (StructuredError,
                                       catch_exception_with_message)


def test_catch_exception_with_message():
    error_message = "Error: test error"

    @catch_exception_with_message(error_message)
    def test_func(has_raise):
        if has_raise:
            raise Exception("This is an internal error!")

    assert test_func(False) is None

    with pytest.raises(StructuredError) as ex:
        test_func(True)

    assert str(ex.value) == error_message
    assert isinstance(ex.value.eObj, Exception)
    assert str(ex.value.eObj) == "This is an internal error!"
