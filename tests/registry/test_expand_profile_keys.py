import pytest
from simplibs.exception import ParamError, ValidationError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.registry import expand_profile_keys


@pytest.mark.parametrize(
    "system, names, expected",
    [
        ("python", "a", ["python/a"]),
        ("python", "a,b", ["python/a", "python/b"]),
        ("python", "a, b ,c", ["python/a", "python/b", "python/c"]),     # spaces around names are dropped
        ("python", " a ", ["python/a"]),
        ("python", "a,,b", ["python/a", "python/b"]),                    # empty items are skipped
        ("python", "a,", ["python/a"]),
        ("python", ["a", "b"], ["python/a", "python/b"]),                # a sequence works like one text
        ("python", ("a", "b"), ["python/a", "python/b"]),
        ("python", ["a,b", "c"], ["python/a", "python/b", "python/c"]),  # items are split on commas too
        ("python", "z,a,m", ["python/z", "python/a", "python/m"]),       # the order given is kept
    ],
)
def test_names_get_the_default_system(system, names, expected) -> None:
    assert expand_profile_keys(system, names) == expected


@pytest.mark.parametrize(
    "system, names, expected",
    [
        ("python", "generic/all", ["generic/all"]),                      # a full key wins over the default system
        ("python", "a,generic/all,b", ["python/a", "generic/all", "python/b"]),
        ("python", ["web/css", "b"], ["web/css", "python/b"]),
        (None, "python/a", ["python/a"]),                                # no default system is needed for full keys
        (None, "python/a,web/b", ["python/a", "web/b"]),
        (None, ["python/a", "web/b"], ["python/a", "web/b"]),
    ],
)
def test_full_keys_are_kept_as_they_are(system, names, expected) -> None:
    assert expand_profile_keys(system, names) == expected


def test_a_name_without_a_system_gives_a_profile_invalid_card(subtests) -> None:
    assert_exception_function(
        subtests,
        expand_profile_keys,
        invalid_params=(None, "a"),
        valid_params=(None, "python/a"),
        exception_type=ParamError,
        error_name="EXTRACTOR_PROFILE_INVALID",
        label="profile keys",
        value="a",
        problem="The profile 'a' has no system.",
        expected="a full key 'system/name', or a system given separately",
        verbose=False,
    )


def test_the_first_name_without_a_system_is_reported(subtests) -> None:
    assert_exception_function(
        subtests,
        expand_profile_keys,
        invalid_params=(None, "python/a,b,c"),
        exception_type=ParamError,
        error_name="EXTRACTOR_PROFILE_INVALID",
        value="b",
        problem="The profile 'b' has no system.",
        verbose=False,
    )


def test_an_empty_system_counts_as_no_system() -> None:
    with pytest.raises(ParamError):
        expand_profile_keys("", "a")


@pytest.mark.parametrize("names", ["", "   ", ",", " , ,, ", [], [""], ["", " "], ()])
def test_nothing_given_gives_a_profile_invalid_card(subtests, names) -> None:
    assert_exception_function(
        subtests,
        expand_profile_keys,
        invalid_params=("python", names),
        exception_type=ParamError,
        error_name="EXTRACTOR_PROFILE_INVALID",
        label="profile keys",
        value=names,
        problem="No profile was given.",
        expected="at least one profile name",
        verbose=False,
    )


@pytest.mark.parametrize(
    "system, names",
    [
        (5, "a"),
        (["python"], "a"),
        ("python", None),
        ("python", 5),
        ("python", ["a", 5]),
        ("python", {"a": 1}),
    ],
)
def test_wrong_types_are_rejected_by_the_type_layer(system, names) -> None:
    with pytest.raises(ValidationError):
        expand_profile_keys(system, names)
