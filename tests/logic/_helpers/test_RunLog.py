import logging
from simplibs.extractor.logic._helpers import RunLog


class SimplibsLike:
    """A logger with the four `log_*` methods of SimpleLogger; records (method, message, args)."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str, tuple]] = []

    def log_debug(self, message, *args):
        self.calls.append(("log_debug", message, args))

    def log_info(self, message, *args):
        self.calls.append(("log_info", message, args))

    def log_success(self, message, *args):
        self.calls.append(("log_success", message, args))

    def log_warning(self, message, *args):
        self.calls.append(("log_warning", message, args))


class StandardLike:
    """A logger with only the standard methods."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str, tuple]] = []

    def debug(self, message, *args):
        self.calls.append(("debug", message, args))

    def info(self, message, *args):
        self.calls.append(("info", message, args))

    def warning(self, message, *args):
        self.calls.append(("warning", message, args))


class BothKinds(SimplibsLike):
    """A logger that has both families of methods."""

    def info(self, message, *args):
        self.calls.append(("info", message, args))


def _write_all(log: RunLog) -> None:
    log.debug("d %s", 1)
    log.info("i %s", 2)
    log.success("s %s", 3)
    log.warning("w %s", 4)


def test_without_a_logger_every_call_is_silent() -> None:
    _write_all(RunLog(None))
    _write_all(RunLog())


def test_a_simplibs_like_logger_gets_its_own_methods() -> None:
    logger = SimplibsLike()
    _write_all(RunLog(logger))
    assert logger.calls == [
        ("log_debug", "d %s", (1,)),
        ("log_info", "i %s", (2,)),
        ("log_success", "s %s", (3,)),
        ("log_warning", "w %s", (4,)),
    ]


def test_a_standard_logger_gets_the_standard_methods_and_success_is_info() -> None:
    logger = StandardLike()
    _write_all(RunLog(logger))
    assert logger.calls == [
        ("debug", "d %s", (1,)),
        ("info", "i %s", (2,)),
        ("info", "s %s", (3,)),
        ("warning", "w %s", (4,)),
    ]


def test_the_simplibs_methods_win_when_a_logger_has_both() -> None:
    logger = BothKinds()
    log = RunLog(logger)
    log.info("hello")
    assert logger.calls == [("log_info", "hello", ())]


def test_the_message_and_its_arguments_are_passed_on_unformatted() -> None:
    """Formatting belongs to the logger (and is skipped when the level is off)."""
    logger = SimplibsLike()
    RunLog(logger).info("a %s b %d", "x", 5)
    assert logger.calls == [("log_info", "a %s b %d", ("x", 5))]


def test_a_message_without_arguments() -> None:
    logger = SimplibsLike()
    RunLog(logger).warning("plain")
    assert logger.calls == [("log_warning", "plain", ())]


def test_a_real_standard_logger_formats_the_message_and_maps_the_levels(caplog) -> None:
    logger = logging.getLogger("extractor-test-runlog")
    log = RunLog(logger)
    with caplog.at_level(logging.DEBUG, logger="extractor-test-runlog"):
        _write_all(log)
    records = [(record.levelno, record.getMessage()) for record in caplog.records if record.name == "extractor-test-runlog"]
    assert records == [
        (logging.DEBUG, "d 1"),
        (logging.INFO, "i 2"),
        (logging.INFO, "s 3"),
        (logging.WARNING, "w 4"),
    ]


def test_the_adapter_uses_slots() -> None:
    assert not hasattr(RunLog(None), "__dict__")
