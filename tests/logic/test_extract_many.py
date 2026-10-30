import sys
from pathlib import Path
import pytest
from simplibs.exception import SimpleException, ValidationError
from simplibs.extractor.definitions import ExtractionConfig, ExtractionResult, FileReport
from simplibs.extractor.logic.select._validations import raise_source_not_found_error
from simplibs.extractor.logic.write._validations import raise_target_exists_error
from simplibs.extractor.logic import extract_many

# `simplibs.extractor.logic.extract_many` is also the name of the function, so the MODULE is taken from `sys.modules`.
MODULE = sys.modules["simplibs.extractor.logic.extract_many"]


def _config(tmp_path, name: str) -> ExtractionConfig:
    return ExtractionConfig(source=tmp_path / name)


def _success(config: ExtractionConfig) -> ExtractionResult:
    report = FileReport(Path("a.txt"), "a.txt", "ok", None, 1, 1)
    return ExtractionResult(config=config, profile_key="generic/all", target=None, files=(report,))


@pytest.fixture
def calls(monkeypatch):
    """Replace `extract` by a fake that records its calls; a config named `bad*` fails with a card."""
    recorded: list[tuple[ExtractionConfig, dict]] = []

    def fake_extract(config, **kwargs):
        recorded.append((config, kwargs))
        if Path(config.source).name.startswith("bad"):
            raise_source_not_found_error(Path(config.source))
        return _success(config)

    monkeypatch.setattr(MODULE, "extract", fake_extract)
    return recorded


def test_extract_many_gives_one_result_per_config_in_order(tmp_path, calls) -> None:
    """Every run is started, and the results come back in the order of the configs."""
    configs = [_config(tmp_path, name) for name in ("a", "b", "c")]

    results = extract_many(configs)

    assert [result.config for result in results] == configs
    assert [config for config, _ in calls] == configs
    assert all(result.success for result in results)


def test_extract_many_no_configs_no_results(calls) -> None:
    """Nothing to run."""
    assert extract_many([]) == []
    assert calls == []


def test_extract_many_a_failed_run_is_a_result_and_the_others_still_run(tmp_path, calls) -> None:
    """The error is turned into a result with `fatal`; it does not stop the batch."""
    configs = [_config(tmp_path, "a"), _config(tmp_path, "bad1"), _config(tmp_path, "c")]

    results = extract_many(configs)

    assert len(results) == 3
    assert [result.success for result in results] == [True, False, True]
    assert results[1].config is configs[1]
    assert results[1].fatal.startswith("NotFoundError: ")
    assert results[0].fatal is None and results[2].fatal is None
    assert len(calls) == 3


def test_extract_many_every_run_may_fail_alone(tmp_path, calls) -> None:
    """Nothing but failed results, still one per config."""
    configs = [_config(tmp_path, "bad1"), _config(tmp_path, "bad2")]

    results = extract_many(configs)

    assert [result.success for result in results] == [False, False]
    assert all(result.fatal for result in results)


def test_extract_many_stop_on_error_stops_after_the_first_failure(tmp_path, calls) -> None:
    """The failed run is in the list; the runs after it are never started."""
    configs = [_config(tmp_path, "a"), _config(tmp_path, "bad1"), _config(tmp_path, "c")]

    results = extract_many(configs, stop_on_error=True)

    assert len(results) == 2
    assert results[0].success is True
    assert results[1].success is False and results[1].config is configs[1]
    assert [config for config, _ in calls] == configs[:2]


def test_extract_many_stop_on_error_without_a_failure_runs_everything(tmp_path, calls) -> None:
    """The flag only matters after a failure."""
    configs = [_config(tmp_path, "a"), _config(tmp_path, "b")]

    results = extract_many(configs, stop_on_error=True)

    assert len(results) == 2
    assert all(result.success for result in results)


def test_extract_many_stop_on_error_is_off_by_default(tmp_path, calls) -> None:
    """The batch goes on after a failure unless asked to stop."""
    configs = [_config(tmp_path, "bad1"), _config(tmp_path, "b")]

    assert len(extract_many(configs)) == 2


def test_extract_many_passes_the_logger_to_every_run(tmp_path, calls) -> None:
    """One logger for the whole batch."""
    sentinel = object()
    configs = [_config(tmp_path, "a"), _config(tmp_path, "b")]

    extract_many(configs, logger=sentinel)

    assert [kwargs for _, kwargs in calls] == [{"logger": sentinel}, {"logger": sentinel}]


def test_extract_many_a_card_of_any_kind_becomes_a_result(tmp_path, monkeypatch) -> None:
    """Whatever the library raises as a card, not only a missing source."""

    def fake_extract(config, **kwargs):
        raise_target_exists_error(Path("out.md"))

    monkeypatch.setattr(MODULE, "extract", fake_extract)

    results = extract_many([_config(tmp_path, "a")])

    assert results[0].fatal.startswith("AlreadyExistsError: ")


def test_extract_many_an_error_that_is_not_a_card_is_not_hidden(tmp_path, monkeypatch) -> None:
    """A bug in the code is not a failed extraction: it comes out as it is."""

    def fake_extract(config, **kwargs):
        raise RuntimeError("a bug")

    monkeypatch.setattr(MODULE, "extract", fake_extract)

    with pytest.raises(RuntimeError):
        extract_many([_config(tmp_path, "a")])


def test_extract_many_the_failed_result_comes_from_the_card_not_from_the_exception_class(tmp_path, monkeypatch) -> None:
    """`SimpleException` is what is caught, so every card of the ecosystem qualifies."""
    caught: list[SimpleException] = []

    def fake_extract(config, **kwargs):
        try:
            raise_source_not_found_error(Path("x"))
        except SimpleException as error:
            caught.append(error)
            raise

    monkeypatch.setattr(MODULE, "extract", fake_extract)

    results = extract_many([_config(tmp_path, "a")])

    assert len(caught) == 1
    assert results[0].fatal.startswith(type(caught[0]).__name__)


@pytest.mark.parametrize("bad", ["abc", None, 5, [1], [None], ["abc"]], ids=["str", "None", "int", "list-of-int", "list-of-None", "list-of-str"])
def test_extract_many_rejects_configs_that_are_not_configs(bad) -> None:
    """A sequence of `ExtractionConfig` only."""
    with pytest.raises(ValidationError):
        extract_many(bad)


@pytest.mark.parametrize("flag", ["x", None, 1.5, []])
def test_extract_many_rejects_a_stop_on_error_that_is_not_a_bool(flag) -> None:
    """The flag is a bool."""
    with pytest.raises(ValidationError):
        extract_many([], stop_on_error=flag)
