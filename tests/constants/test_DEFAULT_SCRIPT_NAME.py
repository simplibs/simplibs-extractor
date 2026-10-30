from pathlib import Path
from simplibs.path import is_valid_filename
from simplibs.extractor.constants import DEFAULT_SCRIPT_NAME


def test_value() -> None:
    """The default generated local script name is `extract_here.py`."""
    assert DEFAULT_SCRIPT_NAME == "extract_here.py"
    assert isinstance(DEFAULT_SCRIPT_NAME, str)


def test_is_a_usable_python_file_name() -> None:
    """The name is a plain file name and ends with `.py`, so the script can be run."""
    assert is_valid_filename(DEFAULT_SCRIPT_NAME)
    assert Path(DEFAULT_SCRIPT_NAME).suffix == ".py"
