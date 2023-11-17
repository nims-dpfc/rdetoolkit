import pytest
from rdetoolkit.exceptions import StructuredError, catch_exception_with_message


def test_catch_exception_with_message_Exception():
    error_message = "Error: test error"

    @catch_exception_with_message(errro_message=error_message)
    def test_func(has_raise):
        if has_raise:
            raise Exception("This is an internal error!")

    assert test_func(False) is None

    with pytest.raises(Exception) as ex:
        test_func(True)

    assert str(ex.value) == error_message


def test_catch_exception_with_message_StructuredError():
    error_message = "Error: test error"
    error_code = 20

    @catch_exception_with_message(errro_message=error_message, error_code=error_code)
    def test_func(has_raise):
        if has_raise:
            raise StructuredError("This is an internal error!")

    assert test_func(False) is None

    with pytest.raises(StructuredError) as ex:
        test_func(True)

    assert ex.value.eMsg == error_message
    assert ex.value.eCode == error_code
    assert isinstance(ex.value.eObj, StructuredError)
