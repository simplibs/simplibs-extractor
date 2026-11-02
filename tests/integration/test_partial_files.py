import warnings
from pathlib import Path
import pytest
from simplibs.extractor import Profile, extract, format_summary


@pytest.fixture
def project(tmp_path) -> Path:
    folder = tmp_path / "project"
    (folder / "src").mkdir(parents=True)
    (folder / "src" / "good.txt").write_text("good\n", encoding="utf-8")
    (folder / "src" / "odd.txt").write_text("odd\n", encoding="utf-8")
    return folder


def _profile(make_action) -> Profile:
    """A step that cannot handle `odd.txt` fully: it warns and leaves that text as it is."""

    def step(text):
        if text.startswith("odd"):
            warnings.warn("cannot be processed fully")
            return text
        return text.upper()

    return Profile("t", "partial", steps=make_action(step))


def test_a_partial_file_is_reported_and_the_run_is_successful(project, make_action) -> None:
    result = extract(source=project, profile=_profile(make_action), dry_run=True)
    assert [f.relative for f in result.ok_files] == ["src/good.txt"]
    assert [(f.relative, f.reason) for f in result.partial_files] == [("src/odd.txt", "cannot be processed fully")]
    assert result.error_files == ()
    assert result.success is True


def test_a_partial_file_is_in_the_written_output_as_it_was(project, make_action) -> None:
    result = extract(source=project, profile=_profile(make_action))
    output = result.target.read_text(encoding="utf-8")
    assert "GOOD" in output                    # cleaned by the step
    assert "odd" in output                     # left as it was, but present
    assert "ODD" not in output


def test_the_bytes_in_count_the_partial_file_too(project, make_action) -> None:
    result = extract(source=project, profile=_profile(make_action), dry_run=True)
    sizes = sum((project / "src" / name).stat().st_size for name in ("good.txt", "odd.txt"))
    assert result.bytes_in == sizes            # the size on disk: on Windows a text file is longer by its line endings


def test_the_summary_names_the_partial_file(project, make_action) -> None:
    summary = format_summary(extract(source=project, profile=_profile(make_action), dry_run=True))
    assert "1 ok, 1 partial, 0 skipped, 0 errors" in summary
    assert "partial: src/odd.txt (cannot be processed fully)" in summary


def test_the_warning_does_not_leak_out_of_the_run(project, make_action) -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        extract(source=project, profile=_profile(make_action), dry_run=True)
    assert [str(item.message) for item in caught] == []
