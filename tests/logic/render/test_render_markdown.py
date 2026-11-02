import re
from pathlib import Path
import pytest
from simplibs.extractor.constants import GENERATED_MARKER, LANGUAGE_BY_SUFFIX, MARKER_SCAN_LINES
from simplibs.extractor.definitions import Entry
from simplibs.extractor.logic.read import read_source
from simplibs.extractor.logic.render import RenderContext, build_tree, render_markdown
from simplibs.extractor.registry import register_language
from simplibs.extractor.registry._helpers import LANGUAGE_REGISTRY

OPENING = re.compile(r"^(`{3,}|~{3,})(\S*)\s*$")


def _context(**overrides) -> RenderContext:
    values = {"title": "My code", "source": Path("project"), "profile_key": "generic/all", "add_tree": False}
    values.update(overrides)
    return RenderContext(**values)


def _blocks(text: str) -> list[tuple[str, str]]:
    """The fenced blocks of a Markdown text as (language, code), read the way a Markdown reader reads fences."""
    lines = text.split("\n")
    blocks: list[tuple[str, str]] = []
    index = 0
    while index < len(lines):
        opening = OPENING.match(lines[index])
        if not opening:
            index += 1
            continue
        fence, language = opening.group(1), opening.group(2)
        closing = re.compile(re.escape(fence[0]) + "{" + str(len(fence)) + ",}")
        body: list[str] = []
        index += 1
        while index < len(lines) and not closing.fullmatch(lines[index].strip()):
            body.append(lines[index])
            index += 1
        blocks.append((language, "\n".join(body)))
        index += 1
    return blocks


# ---------------------------------------------------------------- the frame of the output

def test_the_marker_is_the_first_line() -> None:
    output = render_markdown([Entry("a.py", ".py", "x = 1\n")], _context())
    lines = output.splitlines()
    assert lines[0] == f"<!-- {GENERATED_MARKER} -->"
    assert lines[1] == ""


@pytest.mark.parametrize("add_tree", [False, True])
@pytest.mark.parametrize("title", ["T", "A very long title " * 20, "Příliš žluťoučký kůň"])
@pytest.mark.parametrize("has_entries", [False, True])
def test_the_marker_is_always_within_the_scanned_head(add_tree, title, has_entries) -> None:
    """The read phase only looks at the first lines: the marker must never be pushed out of them."""
    entries = [Entry("a.py", ".py", "x = 1\n")] if has_entries else []
    output = render_markdown(entries, _context(add_tree=add_tree, title=title))
    head = "\n".join(output.splitlines()[:MARKER_SCAN_LINES])
    assert GENERATED_MARKER in head


def test_title_and_profile_are_written() -> None:
    output = render_markdown([], _context(title="My code", profile_key="python/code-clean"))
    assert "# My code" in output
    assert "Profile: `python/code-clean`" in output


def test_the_output_ends_with_exactly_one_line_break() -> None:
    for entries in ([], [Entry("a.py", ".py", "x = 1\n\n\n")]):
        output = render_markdown(entries, _context())
        assert output.endswith("\n")
        assert not output.endswith("\n\n")


def test_the_absolute_path_of_the_source_is_not_written() -> None:
    source = Path("/home/secret-user/very-private/project")
    output = render_markdown([Entry("a.py", ".py", "x = 1\n")], _context(source=source))
    assert "secret-user" not in output
    assert "very-private" not in output


def test_without_entries_there_is_no_code_block_and_no_tree() -> None:
    output = render_markdown([], _context(add_tree=True))
    assert _blocks(output) == []


# ---------------------------------------------------------------- files

def test_every_file_has_a_heading_and_a_fenced_block_in_the_given_order() -> None:
    entries = [Entry("b.py", ".py", "b = 1\n"), Entry("a.py", ".py", "a = 1\n")]
    output = render_markdown(entries, _context())
    assert output.index("## `b.py`") < output.index("## `a.py`")
    assert _blocks(output) == [("python", "b = 1"), ("python", "a = 1")]


def test_the_path_in_the_heading_is_the_relative_path() -> None:
    output = render_markdown([Entry("src/pkg/a.py", ".py", "x = 1\n")], _context())
    assert "## `src/pkg/a.py`" in output


def test_trailing_line_breaks_of_the_text_are_not_part_of_the_code() -> None:
    output = render_markdown([Entry("a.py", ".py", "x = 1\ny = 2\n\n\n")], _context())
    assert _blocks(output) == [("python", "x = 1\ny = 2")]


def test_indentation_blank_lines_and_trailing_spaces_inside_the_text_are_kept() -> None:
    text = "def f():\n    x = 1  \n\n\n    return x\n"
    output = render_markdown([Entry("a.py", ".py", text)], _context())
    assert _blocks(output) == [("python", text.rstrip("\n"))]


def test_diacritics_are_kept() -> None:
    text = "# Příliš žluťoučký kůň\n"
    output = render_markdown([Entry("a.py", ".py", text)], _context())
    assert _blocks(output) == [("python", text.rstrip("\n"))]


def test_text_that_contains_a_fence_does_not_break_the_block() -> None:
    """A Markdown file that shows a code block must come out as one block."""
    text = "Use it like this:\n```python\nprint(1)\n```\nDone.\n"
    output = render_markdown([Entry("README.md", ".md", text)], _context())
    assert _blocks(output) == [("markdown", text.rstrip("\n"))]


def test_text_that_contains_a_longer_fence_does_not_break_the_block() -> None:
    text = "````\nnested ```\n````\n"
    output = render_markdown([Entry("README.md", ".md", text)], _context())
    assert _blocks(output) == [("markdown", text.rstrip("\n"))]


@pytest.mark.parametrize("text", ["", "\n", "\n\n\n", "   \n", "  \n\t\n"])
def test_an_empty_file_is_named_not_fenced(text) -> None:
    output = render_markdown([Entry("empty.py", ".py", text)], _context())
    assert "## `empty.py`" in output
    assert "(empty file)" in output
    assert _blocks(output) == []


def test_an_empty_file_does_not_hide_the_next_one() -> None:
    entries = [Entry("empty.py", ".py", ""), Entry("b.py", ".py", "b = 1\n")]
    output = render_markdown(entries, _context())
    assert _blocks(output) == [("python", "b = 1")]
    assert output.index("empty.py") < output.index("b.py")


# ---------------------------------------------------------------- the language of the fence

@pytest.mark.parametrize("suffix", sorted(LANGUAGE_BY_SUFFIX))
def test_a_known_suffix_gives_its_language(suffix) -> None:
    output = render_markdown([Entry(f"file{suffix}", suffix, "x\n")], _context())
    assert _blocks(output) == [(LANGUAGE_BY_SUFFIX[suffix], "x")]


def test_the_suffix_case_is_ignored() -> None:
    output = render_markdown([Entry("a.PY", ".PY", "x\n")], _context())
    assert _blocks(output) == [("python", "x")]


def test_an_unknown_suffix_is_used_as_the_language() -> None:
    output = render_markdown([Entry("a.xyz", ".xyz", "x\n")], _context())
    assert _blocks(output) == [("xyz", "x")]


def test_a_file_without_a_suffix_gets_a_plain_fence() -> None:
    output = render_markdown([Entry("Makefile", "", "all:\n")], _context())
    assert _blocks(output) == [("", "all:")]


# ---------------------------------------------------------------- the tree

def test_the_tree_is_the_first_block_when_it_is_asked_for() -> None:
    entries = [Entry("src/a.py", ".py", "a = 1\n"), Entry("b.py", ".py", "b = 1\n")]
    output = render_markdown(entries, _context(add_tree=True))
    assert _blocks(output) == [
        ("text", build_tree(["src/a.py", "b.py"])),
        ("python", "a = 1"),
        ("python", "b = 1"),
    ]


def test_no_tree_when_it_is_not_asked_for() -> None:
    entries = [Entry("src/a.py", ".py", "a = 1\n")]
    assert _blocks(render_markdown(entries, _context(add_tree=False))) == [("python", "a = 1")]


def test_the_tree_shows_only_the_given_entries() -> None:
    output = render_markdown([Entry("a.py", ".py", "x\n")], _context(add_tree=True))
    assert _blocks(output)[0] == ("text", "└── a.py")


# ---------------------------------------------------------------- as a whole

def test_the_same_input_gives_the_same_output() -> None:
    entries = [Entry("a.py", ".py", "x = 1\n"), Entry("b.md", ".md", "# T\n")]
    assert render_markdown(entries, _context(add_tree=True)) == render_markdown(entries, _context(add_tree=True))


def test_the_entries_are_not_changed() -> None:
    entries = [Entry("a.py", ".py", "x = 1\n")]
    render_markdown(entries, _context())
    assert entries == [Entry("a.py", ".py", "x = 1\n")]


def test_any_sequence_of_entries_works() -> None:
    entry = Entry("a.py", ".py", "x = 1\n")
    assert render_markdown((entry,), _context()) == render_markdown([entry], _context())


def test_the_output_is_recognized_as_generated_when_it_is_read_again(tmp_path) -> None:
    """Second run over the same folder: the first output must not be extracted into the second."""
    path = tmp_path / "out.md"
    path.write_text(render_markdown([Entry("a.py", ".py", "x = 1\n")], _context(add_tree=True)), encoding="utf-8")

    report, text = read_source(path, tmp_path, None)

    assert report.status == "skipped"
    assert report.reason == "generated by simplibs-extractor"
    assert text is None


# ---------------------------------------------------------------- the language of the fence comes from the registry

@pytest.fixture
def _restored_languages():
    """A language registered by a test must not leak into the next one."""
    saved = dict(LANGUAGE_REGISTRY)
    yield
    LANGUAGE_REGISTRY.clear()
    LANGUAGE_REGISTRY.update(saved)


def _render_language_entries(*entries: Entry) -> str:
    return render_markdown(list(entries), RenderContext("Title", Path("project"), "generic/all", False))


@pytest.mark.parametrize("suffix", [".mjs", ".cjs"])
def test_language_module_javascript_gets_the_javascript_fence(suffix) -> None:
    assert "```javascript" in _render_language_entries(Entry(f"a{suffix}", suffix, "export const a = 1;\n"))


def test_language_a_registered_one_is_used_for_the_fence(_restored_languages) -> None:
    register_language(".lua", "lua")
    assert "```lua" in _render_language_entries(Entry("a.lua", ".lua", "print(1)\n"))


def test_language_a_replaced_one_is_used_for_the_fence(_restored_languages) -> None:
    register_language(".py", "python3", replace_existing=True)
    assert "```python3" in _render_language_entries(Entry("a.py", ".py", "x = 1\n"))


def test_language_an_unknown_suffix_is_written_as_it_is_without_the_dot() -> None:
    assert "```nothing" in _render_language_entries(Entry("a.nothing", ".nothing", "text\n"))


def test_language_a_file_without_a_suffix_gets_a_plain_fence() -> None:
    assert "```\nall:" in _render_language_entries(Entry("Makefile", "", "all:\n"))
