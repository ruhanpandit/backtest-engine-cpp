"""Core engine tests against the hand-calculated 10-bar fixture."""

import pytest
from backtest_engine._core import run_engine

TICK_SIZE = 0.25
POINT_VALUE = 5.0   # MES: $5/point
COMMISSION = 0.62   # per side


def _run(bars, orders):
    """Helper: call the C++ engine with the fixture data."""
    return run_engine(
        bars["open"], bars["high"], bars["low"], bars["close"],
        bars["session_date"], bars["instrument_id"],
        orders["signal_bar"],
        orders["side"],
        orders["entry_type"],
        orders["entry_price"],
        orders["stop"],
        orders["target"],
        orders["contracts"],
        TICK_SIZE, POINT_VALUE, COMMISSION,
    )


class TestFillRules:
    """Each test maps to one exit path in the fixture."""

    def test_trade_count(self, ten_bar_fixture):
        """Engine must produce exactly 3 trades."""
        bars, orders, expected = ten_bar_fixture
        trades = _run(bars, orders)
        assert len(trades) == 3

    def test_target_hit(self, ten_bar_fixture):
        """Trade 1: market buy bar 0, target 4514.00 hit on bar 2."""
        bars, orders, expected = ten_bar_fixture
        trade = _run(bars, orders)[0]
        exp = expected[0]

        assert trade["entry_bar"]   == exp["entry_bar"]
        assert trade["exit_bar"]    == exp["exit_bar"]
        assert trade["entry_price"] == pytest.approx(exp["entry_price"])
        assert trade["exit_price"]  == pytest.approx(exp["exit_price"])
        assert trade["exit_reason"] == exp["exit_reason"]
        assert trade["pnl"]         == pytest.approx(exp["pnl"], abs=0.01)

    def test_stop_hit_same_bar(self, ten_bar_fixture):
        """Trade 2: market buy bar 4, stop and target both in range bar 5, stop wins."""
        bars, orders, expected = ten_bar_fixture
        trade = _run(bars, orders)[1]
        exp = expected[1]

        assert trade["entry_bar"]   == exp["entry_bar"]
        assert trade["exit_bar"]    == exp["exit_bar"]
        assert trade["entry_price"] == pytest.approx(exp["entry_price"])
        assert trade["exit_price"]  == pytest.approx(exp["exit_price"])
        assert trade["exit_reason"] == exp["exit_reason"]
        assert trade["pnl"]         == pytest.approx(exp["pnl"], abs=0.01)

    def test_session_flatten(self, ten_bar_fixture):
        """Trade 3: market buy bar 7, session changes at bar 9, flatten at open."""
        bars, orders, expected = ten_bar_fixture
        trade = _run(bars, orders)[2]
        exp = expected[2]

        assert trade["entry_bar"]   == exp["entry_bar"]
        assert trade["exit_bar"]    == exp["exit_bar"]
        assert trade["entry_price"] == pytest.approx(exp["entry_price"])
        assert trade["exit_price"]  == pytest.approx(exp["exit_price"])
        assert trade["exit_reason"] == exp["exit_reason"]
        assert trade["pnl"]         == pytest.approx(exp["pnl"], abs=0.01)

    def test_total_pnl(self, ten_bar_fixture):
        """Sum of all three trades must equal +$47.53."""
        bars, orders, expected = ten_bar_fixture
        trades = _run(bars, orders)
        total = sum(t["pnl"] for t in trades)
        assert total == pytest.approx(47.53, abs=0.01)
