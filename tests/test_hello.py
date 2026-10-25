"""Smoke test: proves the pybind11 extension builds and loads."""

from backtest_engine import hello


def test_hello_returns_string():
    result = hello()
    assert isinstance(result, str)
    assert "alive" in result
