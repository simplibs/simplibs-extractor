import pytest
from simplibs.exception import OperationError, SimpleError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.logic.transform._validations import raise_step_result_error


class UpperStep:
    """A stand-in for an `Action`: only its class name is shown in the card."""


@pytest.mark.parametrize(
    "step, step_name",
    [(UpperStep(), "UpperStep"), (lambda text: text, "function"), (str.upper, "method_descriptor")],
    ids=["object", "lambda", "method-descriptor"],
)
@pytest.mark.parametrize(
    "result",
    [None, 5, ["a"], b"x", ("a", "b"), 1.5],
    ids=["None", "int", "list", "bytes", "tuple", "float"],
)
def test_raise_step_result_error_contract(subtests, step, step_name, result) -> None:
    """Verify raise_step_result_error produces a well-formed OperationError card naming the step and what it returned."""

    exc = assert_exception_function(
        subtests,
        raise_step_result_error,
        invalid_params=(step, result),
        exception_type=OperationError,
        error_name="EXTRACTOR_STEP_RESULT_INVALID",
        label=f"result of step {step_name}",
        value=result,
        problem=f"The step returned {type(result).__name__}, not str.",
        expected="A text: every step of a profile takes a str and returns a str.",
        how_to_fix=(
            "Make the step return the transformed text.",
            "Check the order of the steps: each one receives the text the previous one returned.",
        ),
        exception=TypeError,
        verbose=False,
    )

    # Catchable as the wrapped standard type and as "any error of this library"
    assert isinstance(exc, TypeError)
    assert isinstance(exc, SimpleError)
