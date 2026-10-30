import pytest
from simplibs.exception import NotFoundError
from simplibs.extractor.cli._helpers import print_error
from simplibs.extractor.registry._validations import raise_profile_not_found_error


def test_a_card_goes_to_standard_error_as_it_prints(capsys) -> None:
    with pytest.raises(NotFoundError) as caught:
        raise_profile_not_found_error("python/nothing", ["generic/all"])
    print_error(caught.value)

    captured = capsys.readouterr()
    assert captured.err == str(caught.value) + "\n"
    assert captured.out == ""


def test_any_exception_is_printed_too(capsys) -> None:
    print_error(RuntimeError("boom"))
    captured = capsys.readouterr()
    assert captured.err == "boom\n"
    assert captured.out == ""


def test_it_returns_nothing(capsys) -> None:
    assert print_error(RuntimeError("boom")) is None
