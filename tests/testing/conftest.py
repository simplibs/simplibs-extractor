import contextlib
import pytest
from simplibs.path.rules import AnyParentNameIs, HasSuffix
from simplibs.rules import IsIn
from simplibs.extractor.definitions import Profile


class Recorder:
    """A stand-in for the `subtests` fixture that records instead of failing.

    The blades of `assert_profile` open one subtest per checked value. With the real fixture a failing
    check fails the test, which is exactly what must not happen when a test wants to see that a check
    DOES fail. This one writes down which subtests passed and which failed (with the message), and
    lets every other kind of exception through.
    """

    def __init__(self) -> None:
        self.passed: list[str] = []
        self.failed: dict[str, str] = {}

    @property
    def names(self) -> list[str]:
        """Every subtest that was opened, passed or failed, in the order of opening."""
        return [*self.passed, *self.failed]

    @contextlib.contextmanager
    def test(self, msg=None, *args, **kwargs):
        name = msg if msg is not None else kwargs.get("name", "")
        try:
            yield
        except AssertionError as exc:
            self.failed[name] = str(exc)
        else:
            self.passed.append(name)


@pytest.fixture
def recorder() -> Recorder:
    """A fresh recorder in place of the `subtests` fixture."""
    return Recorder()


@pytest.fixture
def make_profile(make_action):
    """Build a profile that is correct by default; `make_profile(description="")` changes one thing.

    Takes `.py` files outside a folder named `tests`; `.py` text is upper-cased, any other text is stripped.
    """

    def make(**changes) -> Profile:
        fields = dict(
            system="python",
            name="clean",
            description="Python without tests",
            include=HasSuffix(".py"),
            exclude=AnyParentNameIs(IsIn(("tests",))),
            steps={
                ".py": make_action(str.upper, name="Upper"),
                "*": make_action(str.strip, name="Strip"),
            },
            output_name="python_clean.md",
            format="markdown",
        )
        fields.update(changes)
        return Profile(**fields)

    return make
