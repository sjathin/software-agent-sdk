"""Tests for standardized send_keys special key handling."""

import pytest

from openhands.tools.terminal.terminal.interface import (
    SUPPORTED_SPECIAL_KEYS,
    parse_ctrl_key,
)


# ── parse_ctrl_key ──────────────────────────────────────────────────


@pytest.mark.parametrize(
    "text, expected",
    [
        ("C-a", "C-a"),
        ("C-Z", "C-z"),
        ("CTRL-c", "C-c"),
        ("ctrl+d", "C-d"),
        ("CTRL+L", "C-l"),
        ("C-m", "C-m"),
    ],
)
def test_parse_ctrl_key_valid(text: str, expected: str) -> None:
    assert parse_ctrl_key(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "C-",  # no letter
        "C-ab",  # two letters
        "C-1",  # digit
        "hello",  # plain text
        "CTRL-",  # no letter
        "CTRL+12",  # not single letter
    ],
)
def test_parse_ctrl_key_invalid(text: str) -> None:
    assert parse_ctrl_key(text) is None


# ── SUPPORTED_SPECIAL_KEYS ──────────────────────────────────────────


def test_supported_special_keys_contains_essentials() -> None:
    for key in ("ENTER", "TAB", "ESC", "UP", "DOWN", "C-C", "C-D"):
        assert key in SUPPORTED_SPECIAL_KEYS


# ── SubprocessTerminal.send_keys ────────────────────────────────────


@pytest.fixture
def subprocess_terminal(tmp_path):
    """Create a real SubprocessTerminal for send_keys testing."""
    import platform

    if platform.system() == "Windows":
        pytest.skip("SubprocessTerminal not available on Windows")

    from openhands.tools.terminal.terminal.subprocess_terminal import (
        SubprocessTerminal,
    )

    term = SubprocessTerminal(work_dir=str(tmp_path))
    term.initialize()
    yield term
    term.close()


def test_subprocess_send_keys_ctrl_c(subprocess_terminal) -> None:
    """C-c should be recognized as a special key (not sent as literal text)."""
    # Should not raise; just verify it dispatches without error
    subprocess_terminal.send_keys("C-c")


def test_subprocess_send_keys_named_special(subprocess_terminal) -> None:
    """Named specials like TAB should be dispatched without error."""
    subprocess_terminal.send_keys("TAB")


def test_subprocess_send_keys_ctrl_variants(subprocess_terminal) -> None:
    """CTRL-x and CTRL+x forms should work."""
    subprocess_terminal.send_keys("CTRL-a")
    subprocess_terminal.send_keys("CTRL+e")


# ── TmuxTerminal.send_keys ─────────────────────────────────────────


@pytest.fixture
def tmux_terminal(tmp_path):
    """Create a real TmuxTerminal for send_keys testing."""
    import platform
    import shutil

    if platform.system() == "Windows":
        pytest.skip("TmuxTerminal not available on Windows")
    if shutil.which("tmux") is None:
        pytest.skip("tmux not installed")

    from openhands.tools.terminal.terminal.tmux_terminal import TmuxTerminal

    term = TmuxTerminal(work_dir=str(tmp_path))
    term.initialize()
    yield term
    term.close()


def test_tmux_send_keys_ctrl_c(tmux_terminal) -> None:
    tmux_terminal.send_keys("C-c")


def test_tmux_send_keys_named_special(tmux_terminal) -> None:
    tmux_terminal.send_keys("TAB")
    tmux_terminal.send_keys("UP")
    tmux_terminal.send_keys("ESC")


def test_tmux_send_keys_ctrl_variants(tmux_terminal) -> None:
    tmux_terminal.send_keys("CTRL-a")
    tmux_terminal.send_keys("CTRL+e")


def test_tmux_send_keys_plain_text(tmux_terminal) -> None:
    """Plain text should be sent literally (not interpreted as a key name)."""
    import time

    tmux_terminal.send_keys("echo hello_world")
    time.sleep(0.3)
    screen = tmux_terminal.read_screen()
    assert "hello_world" in screen
