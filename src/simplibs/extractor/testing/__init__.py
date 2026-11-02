from .assert_profile import assert_profile


__all__ = [
    "assert_profile",
]


_DESIGN_NOTES = """
# testing — Tools for Testing What You Build on the Extractor

## Purpose
An add-on of the extractor (`simplibs-extractor-python` is the first) delivers
profiles. This folder holds the tools that check them, so every add-on tests
its profiles the same way and nobody rewrites the same twenty lines:

    from simplibs.extractor.testing import assert_profile

## Not Imported by the Package Root
Like `cli`, it is reached by its own path. A program that only calls
`extract()` never loads it.

## Internal Components Registry

| Component        | Type     | Description                                                 |
| :--------------- | :------- | :---------------------------------------------------------- |
| `assert_profile` | Function | Checks a `Profile`: identity, selection of files, its steps. |
"""
