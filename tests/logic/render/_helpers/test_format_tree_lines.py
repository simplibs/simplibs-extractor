from simplibs.extractor.logic.render._helpers import format_tree_lines


def test_no_names_give_no_lines() -> None:
    assert format_tree_lines({}) == []


def test_one_file() -> None:
    assert format_tree_lines({"a.py": {}}) == ["└── a.py"]


def test_two_files_the_last_one_closes_the_branch() -> None:
    assert format_tree_lines({"a.py": {}, "b.py": {}}) == ["├── a.py", "└── b.py"]


def test_a_folder_gets_a_slash_and_its_children_are_indented() -> None:
    assert format_tree_lines({"src": {"a.py": {}}}) == ["└── src/", "    └── a.py"]


def test_the_line_of_an_unfinished_branch_continues_below_it() -> None:
    node = {"src": {"a.py": {}}, "z.txt": {}}
    assert format_tree_lines(node) == ["├── src/", "│   └── a.py", "└── z.txt"]


def test_folders_come_before_files() -> None:
    node = {"a.txt": {}, "z": {"b.txt": {}}}
    assert format_tree_lines(node) == ["├── z/", "│   └── b.txt", "└── a.txt"]


def test_sorting_ignores_the_case() -> None:
    assert format_tree_lines({"B.py": {}, "a.py": {}, "C.py": {}}) == ["├── a.py", "├── B.py", "└── C.py"]


def test_the_given_prefix_starts_every_line() -> None:
    assert format_tree_lines({"a.py": {}}, "  ") == ["  └── a.py"]


def test_deep_nesting() -> None:
    node = {"a": {"b": {"c.py": {}}}}
    assert format_tree_lines(node) == ["└── a/", "    └── b/", "        └── c.py"]
