import runpy
from pathlib import Path
import pytest
from simplibs.exception import AlreadyExistsError, NotFoundError, ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.constants import DEFAULT_SCRIPT_NAME, GENERATED_MARKER
from simplibs.extractor.definitions import Profile
from simplibs.extractor.registry import register_profile
from simplibs.extractor.scripts import generate_local_script
from simplibs.path import normalize_path


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------- where the script goes

def test_a_folder_gets_the_default_script_name(tmp_path) -> None:
    script = generate_local_script(tmp_path)
    assert script == normalize_path(tmp_path) / DEFAULT_SCRIPT_NAME
    assert script.is_file()


def test_a_file_path_is_used_as_it_is(tmp_path) -> None:
    script = generate_local_script(tmp_path / "run_extraction.py")
    assert script == normalize_path(tmp_path) / "run_extraction.py"
    assert script.is_file()


def test_the_path_may_be_text(tmp_path) -> None:
    script = generate_local_script(str(tmp_path / "run.py"))
    assert script.is_file()


def test_a_missing_folder_in_front_of_the_script_is_created(tmp_path) -> None:
    script = generate_local_script(tmp_path / "new" / "deeper" / "run.py")
    assert script.is_file()


def test_the_result_is_an_absolute_path(tmp_path) -> None:
    script = generate_local_script(tmp_path / "run.py")
    assert isinstance(script, Path)
    assert script.is_absolute()


# ---------------------------------------------------------------- what the script says

def test_the_default_profile_is_written(tmp_path) -> None:
    assert "profile='generic/all'" in _text(generate_local_script(tmp_path))


def test_a_profile_key_is_written(tmp_path) -> None:
    register_profile(Profile("python", "code"))
    assert "profile='python/code'" in _text(generate_local_script(tmp_path, "python/code"))


def test_a_profile_object_is_written_by_its_key(tmp_path) -> None:
    profile = Profile("python", "unregistered")
    assert "profile='python/unregistered'" in _text(generate_local_script(tmp_path, profile))


def test_the_script_names_itself_in_the_run_line(tmp_path) -> None:
    assert "python run_extraction.py" in _text(generate_local_script(tmp_path / "run_extraction.py"))


def test_the_script_is_valid_python(tmp_path) -> None:
    script = generate_local_script(tmp_path)
    compile(_text(script), str(script), "exec")


# ---------------------------------------------------------------- refusals

@pytest.mark.parametrize("name", ["script.txt", "script", "script.py.txt", "script.pyc"])
def test_a_name_that_is_not_python_gives_a_config_invalid_card(subtests, tmp_path, name) -> None:
    path = tmp_path / name
    assert_exception_function(
        subtests,
        generate_local_script,
        invalid_params=(path,),
        valid_params=(tmp_path / "ok.py",),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="parameter 'path'",
        value=str(normalize_path(path)),
        problem=f"The script name {name!r} does not end with '.py'.",
        expected="A file name ending with '.py', or a folder.",
        verbose=False,
    )
    assert not path.exists()


def test_an_unknown_profile_fails_before_anything_is_written(tmp_path) -> None:
    with pytest.raises(NotFoundError):
        generate_local_script(tmp_path, "python/nothing")
    assert list(tmp_path.iterdir()) == []


def test_an_existing_script_is_not_replaced_by_default(tmp_path) -> None:
    script = tmp_path / "run.py"
    script.write_text("# my own script\n", encoding="utf-8")
    with pytest.raises(AlreadyExistsError):
        generate_local_script(script)
    assert _text(script) == "# my own script\n"


def test_overwrite_replaces_an_existing_script(tmp_path) -> None:
    script = tmp_path / "run.py"
    script.write_text("# my own script\n", encoding="utf-8")
    generate_local_script(script, overwrite=True)
    assert "extract_here" in _text(script)


def test_overwrite_is_keyword_only(tmp_path) -> None:
    with pytest.raises(TypeError):
        generate_local_script(tmp_path / "run.py", None, True)  # type: ignore[misc]


# ---------------------------------------------------------------- the script really works

def _project(folder: Path) -> None:
    (folder / "a.txt").write_text("hello from a\n", encoding="utf-8")
    (folder / "b.py").write_text("x = 1\n", encoding="utf-8")


def test_running_the_script_makes_the_output_next_to_it_without_the_script(tmp_path, capsys) -> None:
    _project(tmp_path)
    script = generate_local_script(tmp_path)

    runpy.run_path(str(script), run_name="__main__")

    output = tmp_path / "extraction.md"
    text = _text(output)
    assert text.splitlines()[0] == f"<!-- {GENERATED_MARKER} -->"
    assert "hello from a" in text and "x = 1" in text
    assert "extract_here" not in text
    assert "Extraction:" in capsys.readouterr().out


def test_importing_the_script_does_not_run_it(tmp_path, capsys) -> None:
    _project(tmp_path)
    script = generate_local_script(tmp_path)

    runpy.run_path(str(script))      # run_name is not "__main__"

    assert not (tmp_path / "extraction.md").exists()
    assert capsys.readouterr().out == ""


def test_the_script_uses_the_profile_it_was_made_for(tmp_path) -> None:
    _project(tmp_path)
    register_profile(Profile("t", "plain-one", format="plain", output_name="dump.txt"))
    script = generate_local_script(tmp_path, "t/plain-one")

    runpy.run_path(str(script), run_name="__main__")

    assert "# FILE: a.txt" in _text(tmp_path / "dump.txt")
