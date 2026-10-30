from pathlib import Path
import pytest
from simplibs.extractor.constants import GENERATED_MARKER, MARKER_SCAN_LINES
from simplibs.extractor.definitions import Entry
from simplibs.extractor.logic.read import read_source
from simplibs.extractor.logic.render import RenderContext, build_tree, render_plain


def _context(**overrides) -> RenderContext:
    values = {"title": "My code", "source": Path("project"), "profile_key": "generic/all", "add_tree": False}
    values.update(overrides)
    return RenderContext(**values)


HEADER = f"# {GENERATED_MARKER}\n# My code\n# profile: generic/all\n"


# ---------------------------------------------------------------- the exact layout

def test_without_entries_only_the_header_is_written() -> None:
    assert render_plain([], _context()) == HEADER


def test_without_entries_there_is_no_tree_even_when_asked() -> None:
    assert render_plain([], _context(add_tree=True)) == HEADER


def test_files_follow_the_header_as_file_blocks() -> None:
    entries = [Entry("a.py", ".py", "print(1)\n"), Entry("b.txt", ".txt", "hello\n")]
    assert render_plain(entries, _context()) == (
        HEADER + "\n# FILE: a.py\nprint(1)\n\n# FILE: b.txt\nhello\n"
    )


def test_the_tree_comes_between_the_header_and_the_files() -> None:
    entries = [Entry("a.py", ".py", "print(1)\n"), Entry("b.txt", ".txt", "hello\n")]
    assert render_plain(entries, _context(add_tree=True)) == (
        HEADER
        + "\n# TREE\n├── a.py\n└── b.txt\n"
        + "\n# FILE: a.py\nprint(1)\n\n# FILE: b.txt\nhello\n"
    )


def test_the_tree_is_made_by_build_tree() -> None:
    entries = [Entry("src/a.py", ".py", "x\n"), Entry("b.py", ".py", "y\n")]
    output = render_plain(entries, _context(add_tree=True))
    assert "# TREE\n" + build_tree(["src/a.py", "b.py"]) + "\n" in output


def test_an_empty_file_keeps_its_header_line() -> None:
    assert render_plain([Entry("empty.txt", ".txt", "")], _context()) == HEADER + "\n# FILE: empty.txt\n"


def test_an_empty_file_does_not_hide_the_next_one() -> None:
    entries = [Entry("empty.txt", ".txt", ""), Entry("b.txt", ".txt", "x\n")]
    output = render_plain(entries, _context())
    assert output.index("# FILE: empty.txt") < output.index("# FILE: b.txt")
    assert output.endswith("# FILE: b.txt\nx\n")


# ---------------------------------------------------------------- the text of a file

def test_trailing_line_breaks_of_the_text_are_cut() -> None:
    output = render_plain([Entry("a.txt", ".txt", "x\ny\n\n\n")], _context())
    assert output == HEADER + "\n# FILE: a.txt\nx\ny\n"


def test_inner_blank_lines_indentation_and_trailing_spaces_are_kept() -> None:
    text = "def f():\n    x = 1  \n\n\n    return x\n"
    output = render_plain([Entry("a.py", ".py", text)], _context())
    assert text.rstrip("\n") in output


def test_diacritics_are_kept() -> None:
    output = render_plain([Entry("a.txt", ".txt", "Příliš žluťoučký kůň\n")], _context())
    assert "Příliš žluťoučký kůň" in output


def test_the_order_of_the_entries_is_kept() -> None:
    entries = [Entry("b.txt", ".txt", "b\n"), Entry("a.txt", ".txt", "a\n")]
    output = render_plain(entries, _context())
    assert output.index("# FILE: b.txt") < output.index("# FILE: a.txt")


def test_the_relative_path_is_written_as_it_is() -> None:
    output = render_plain([Entry("src/pkg/a.py", ".py", "x\n")], _context())
    assert "# FILE: src/pkg/a.py\n" in output


# ---------------------------------------------------------------- the frame

@pytest.mark.parametrize("add_tree", [False, True])
@pytest.mark.parametrize("title", ["T", "A very long title " * 20, "Příliš žluťoučký kůň"])
@pytest.mark.parametrize("has_entries", [False, True])
def test_the_marker_is_the_first_line(add_tree, title, has_entries) -> None:
    """The read phase only looks at the first lines: the marker is always on the very first one."""
    entries = [Entry("a.py", ".py", "x = 1\n")] if has_entries else []
    lines = render_plain(entries, _context(add_tree=add_tree, title=title)).splitlines()
    assert lines[0] == f"# {GENERATED_MARKER}"
    assert GENERATED_MARKER in "\n".join(lines[:MARKER_SCAN_LINES])


def test_the_output_ends_with_exactly_one_line_break() -> None:
    for entries in ([], [Entry("a.py", ".py", "x = 1\n\n\n")], [Entry("e.py", ".py", "")]):
        output = render_plain(entries, _context())
        assert output.endswith("\n")
        assert not output.endswith("\n\n")


def test_the_absolute_path_of_the_source_is_not_written() -> None:
    source = Path("/home/secret-user/very-private/project")
    output = render_plain([Entry("a.py", ".py", "x = 1\n")], _context(source=source))
    assert "secret-user" not in output
    assert "very-private" not in output


def test_the_same_input_gives_the_same_output() -> None:
    entries = [Entry("a.py", ".py", "x = 1\n"), Entry("b.md", ".md", "# T\n")]
    assert render_plain(entries, _context(add_tree=True)) == render_plain(entries, _context(add_tree=True))


def test_the_entries_are_not_changed() -> None:
    entries = [Entry("a.py", ".py", "x = 1\n")]
    render_plain(entries, _context())
    assert entries == [Entry("a.py", ".py", "x = 1\n")]


def test_the_output_is_recognized_as_generated_when_it_is_read_again(tmp_path) -> None:
    path = tmp_path / "out.txt"
    path.write_text(render_plain([Entry("a.py", ".py", "x = 1\n")], _context(add_tree=True)), encoding="utf-8")

    report, text = read_source(path, tmp_path, None)

    assert report.status == "skipped"
    assert report.reason == "generated by simplibs-extractor"
    assert text is None
