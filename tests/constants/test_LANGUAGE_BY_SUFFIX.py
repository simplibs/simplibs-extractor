from types import MappingProxyType
import pytest
from simplibs.extractor.constants import LANGUAGE_BY_SUFFIX
from simplibs.extractor.definitions._helpers import is_suffix_key


def test_is_mapping_proxy() -> None:
    """The table is a read-only view."""
    assert isinstance(LANGUAGE_BY_SUFFIX, MappingProxyType)


def test_table_cannot_be_changed() -> None:
    """Writing to or deleting from the table fails, so nobody can change it globally by accident."""
    with pytest.raises(TypeError):
        LANGUAGE_BY_SUFFIX[".py"] = "other"  # type: ignore[index]
    with pytest.raises(TypeError):
        LANGUAGE_BY_SUFFIX[".xyz"] = "other"  # type: ignore[index]
    with pytest.raises(TypeError):
        del LANGUAGE_BY_SUFFIX[".py"]  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    "suffix, language",
    [
        (".py", "python"),
        (".js", "javascript"),
        (".jsx", "jsx"),
        (".ts", "typescript"),
        (".tsx", "tsx"),
        (".json", "json"),
        (".md", "markdown"),
        (".css", "css"),
        (".html", "html"),
        (".toml", "toml"),
        (".yml", "yaml"),
        (".yaml", "yaml"),
        (".sh", "bash"),
        (".sql", "sql"),
        (".txt", "text"),
    ],
)
def test_suffixes_map_correctly(suffix: str, language: str) -> None:
    """Every suffix of the table maps to its syntax-highlighting language."""
    assert LANGUAGE_BY_SUFFIX.get(suffix) == language


def test_unknown_suffix_has_no_entry() -> None:
    """A suffix that is not in the table gives no language (the renderer then writes no language)."""
    assert LANGUAGE_BY_SUFFIX.get(".xyz") is None
    assert LANGUAGE_BY_SUFFIX.get("") is None


def test_keys_are_lowercase_suffixes() -> None:
    """Lookups use a lowercased suffix, so every key must be one a lookup can actually hit."""
    for key in LANGUAGE_BY_SUFFIX:
        assert is_suffix_key(key), key
        assert key != "*", key


def test_values_are_non_empty_lowercase_names() -> None:
    """Every language name is a non-empty lowercase string."""
    for key, language in LANGUAGE_BY_SUFFIX.items():
        assert isinstance(language, str) and language, key
        assert language == language.lower(), key
