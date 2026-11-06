import logging
import main


def test_invalid_menu_choice_logs_warning(monkeypatch, caplog):
    inputs = iter(["abc", "8"])

    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    with caplog.at_level(logging.WARNING):
        main.main()

    assert "Invalid choice" in caplog.text
    assert "WARNING" in caplog.text
def test_unexpected_error_logs_exception(caplog):
    with caplog.at_level(logging.ERROR):
        try:
            raise RuntimeError("Test unexpected error")
        except Exception:
            main.logger.exception("An unexpected error occurred")

    assert "An unexpected error occurred" in caplog.text
    assert "RuntimeError: Test unexpected error" in caplog.text