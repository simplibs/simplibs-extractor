from pathlib import Path
import pytest
from simplibs.extractor.definitions import Entry, Profile
from simplibs.extractor.logic._helpers import process_source
from simplibs.extractor.logic.select import resolve_config


@pytest.fixture
def root(tmp_path) -> Path:
    folder = tmp_path / "project"
    folder.mkdir()
    return folder


def _plan(root: Path, **overrides):
    return resolve_config(None, {"source": root, **overrides})


def _write(root: Path, name: str, text: str) -> Path:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))
    return path


# ---------------------------------------------------------------- an included file

def test_a_text_file_gives_an_ok_report_and_an_entry(root) -> None:
    path = _write(root, "a.py", "x = 1\n")
    report, entry = process_source(path, _plan(root))
    assert report.status == "ok"
    assert report.reason is None
    assert report.path == path
    assert report.relative == "a.py"
    assert entry == Entry("a.py", ".py", "x = 1\n")


def test_the_report_counts_the_bytes_before_and_after(root) -> None:
    path = _write(root, "a.txt", "Příliš\n")
    report, _ = process_source(path, _plan(root))
    assert report.bytes_in == len("Příliš\n".encode("utf-8"))
    assert report.bytes_out == len("Příliš\n".encode("utf-8"))


def test_the_relative_path_uses_slashes(root) -> None:
    path = _write(root, "sub/deep/c.md", "# T\n")
    report, entry = process_source(path, _plan(root))
    assert report.relative == "sub/deep/c.md"
    assert entry.relative == "sub/deep/c.md"


def test_the_suffix_of_the_entry_is_lowercase(root) -> None:
    path = _write(root, "Script.PY", "x = 1\n")
    _, entry = process_source(path, _plan(root))
    assert entry.suffix == ".py"


def test_a_file_without_a_suffix(root) -> None:
    path = _write(root, "Makefile", "all:\n")
    _, entry = process_source(path, _plan(root))
    assert entry.suffix == ""


# ---------------------------------------------------------------- the steps

def test_the_steps_change_the_text_and_the_size_after(root, make_action) -> None:
    path = _write(root, "a.txt", "hello\n")
    profile = Profile("t", "up", steps=make_action(lambda text: text.upper() + "žž\n"))
    report, entry = process_source(path, _plan(root, profile=profile))
    assert entry.text == "HELLO\nžž\n"
    assert report.bytes_in == len("hello\n")
    assert report.bytes_out == len("HELLO\nžž\n".encode("utf-8"))


def test_the_step_of_the_suffix_is_used(root, make_action) -> None:
    py = _write(root, "a.py", "abc\n")
    md = _write(root, "b.md", "abc\n")
    profile = Profile("t", "map", steps={".py": make_action(str.upper)})
    plan = _plan(root, profile=profile)
    assert process_source(py, plan)[1].text == "ABC\n"
    assert process_source(md, plan)[1].text == "abc\n"


def test_a_step_that_raises_makes_an_error_report_and_no_entry(root, make_action) -> None:
    path = _write(root, "a.py", "x = 1\n")

    def broken(text):
        raise RuntimeError("boom")

    report, entry = process_source(path, _plan(root, profile=Profile("t", "bad", steps=make_action(broken))))

    assert entry is None
    assert report.status == "error"
    assert report.reason == "transform failed: RuntimeError: boom"


def test_the_error_report_keeps_what_was_known_about_the_file(root, make_action) -> None:
    path = _write(root, "sub/a.py", "x = 1\n")
    profile = Profile("t", "bad", steps=make_action(lambda text: 1 / 0))
    report, _ = process_source(path, _plan(root, profile=profile))
    assert report.path == path
    assert report.relative == "sub/a.py"
    assert report.bytes_in == len("x = 1\n")
    assert report.reason.startswith("transform failed: ZeroDivisionError")


def test_a_step_that_returns_no_text_makes_an_error_report(root, make_action) -> None:
    path = _write(root, "a.py", "x = 1\n")
    profile = Profile("t", "none", steps=make_action(lambda text: None))
    report, entry = process_source(path, _plan(root, profile=profile))
    assert entry is None
    assert report.status == "error"
    assert report.reason.startswith("transform failed: OperationError")


def test_a_failure_of_a_step_stays_one_line(root, make_action) -> None:
    path = _write(root, "a.py", "x = 1\n")
    profile = Profile("t", "none", steps=make_action(lambda text: None))
    report, _ = process_source(path, _plan(root, profile=profile))
    assert "\n" not in report.reason


def test_an_interrupt_is_not_swallowed(root, make_action) -> None:
    """Only ordinary errors belong to the file; Ctrl+C belongs to the user."""
    path = _write(root, "a.py", "x = 1\n")

    def interrupted(text):
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        process_source(path, _plan(root, profile=Profile("t", "stop", steps=make_action(interrupted))))


# ---------------------------------------------------------------- files that stay out

def test_a_binary_file_is_skipped_and_the_steps_never_see_it(root, make_action) -> None:
    path = root / "logo.png"
    path.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00")
    seen: list[str] = []
    profile = Profile("t", "spy", steps=make_action(lambda text: seen.append(text) or text))

    report, entry = process_source(path, _plan(root, profile=profile))

    assert entry is None
    assert report.status == "skipped"
    assert report.reason == "not a text file"
    assert seen == []


def test_a_file_that_is_too_large_is_skipped(root) -> None:
    path = _write(root, "big.txt", "x" * 100)
    report, entry = process_source(path, _plan(root, max_file_size=10))
    assert entry is None
    assert report.status == "skipped"
    assert report.reason.startswith("too large")


def test_the_size_limit_is_inclusive(root) -> None:
    path = _write(root, "a.txt", "x" * 10)
    report, entry = process_source(path, _plan(root, max_file_size=10))
    assert report.status == "ok"
    assert entry is not None


def test_no_limit_means_any_size(root) -> None:
    path = _write(root, "big.txt", "x" * 100_000)
    report, entry = process_source(path, _plan(root, max_file_size=None))
    assert report.status == "ok"
    assert len(entry.text) == 100_000


def test_a_generated_file_is_skipped(root) -> None:
    path = _write(root, "old.md", "<!-- simplibs-extractor:generated -->\n\n# Old\n")
    report, entry = process_source(path, _plan(root))
    assert entry is None
    assert report.status == "skipped"
    assert report.reason == "generated by simplibs-extractor"


def test_the_steps_are_not_run_for_a_skipped_file(root, make_action) -> None:
    path = _write(root, "old.md", "<!-- simplibs-extractor:generated -->\n")
    seen: list[str] = []
    profile = Profile("t", "spy", steps=make_action(lambda text: seen.append(text) or text))
    process_source(path, _plan(root, profile=profile))
    assert seen == []
