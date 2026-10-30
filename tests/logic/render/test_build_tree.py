import pytest
from simplibs.extractor.logic.render import build_tree


def test_no_paths_give_an_empty_text() -> None:
    assert build_tree([]) == ""


def test_one_file() -> None:
    assert build_tree(["a.py"]) == "└── a.py"


def test_two_files() -> None:
    assert build_tree(["a.py", "b.txt"]) == "├── a.py\n└── b.txt"


def test_nested_paths() -> None:
    paths = ["src/a.py", "src/sub/b.py", "README.md"]
    assert build_tree(paths) == "\n".join(
        [
            "├── src/",
            "│   ├── sub/",
            "│   │   └── b.py",
            "│   └── a.py",
            "└── README.md",
        ]
    )


def test_the_order_of_the_input_does_not_matter() -> None:
    paths = ["src/a.py", "src/sub/b.py", "README.md"]
    assert build_tree(paths) == build_tree(list(reversed(paths)))


def test_one_deep_path() -> None:
    assert build_tree(["a/b/c.py"]) == "└── a/\n    └── b/\n        └── c.py"


def test_the_same_path_twice_is_drawn_once() -> None:
    assert build_tree(["a.py", "a.py"]) == "└── a.py"


def test_a_folder_is_shared_by_its_files() -> None:
    assert build_tree(["src/a.py", "src/b.py"]) == "└── src/\n    ├── a.py\n    └── b.py"


def test_folders_before_files_and_case_is_ignored() -> None:
    assert build_tree(["a.txt", "z/b.txt", "B.txt"]) == "\n".join(
        ["├── z/", "│   └── b.txt", "├── a.txt", "└── B.txt"]
    )


def test_spaces_and_diacritics_are_kept() -> None:
    assert build_tree(["příliš žluťoučký/kůň.py"]) == "└── příliš žluťoučký/\n    └── kůň.py"


def test_no_trailing_newline() -> None:
    assert not build_tree(["a.py", "b.py"]).endswith("\n")


@pytest.mark.parametrize("sequence", [["a.py"], ("a.py",)])
def test_any_sequence_works(sequence) -> None:
    assert build_tree(sequence) == "└── a.py"
