"""Core engine tests against the hand-calculated 10-bar fixture."""

import pytest

COMMISSION_PER_SIDE = 0.62
POINT_VALUE = 5.0  # MES: $5/point
TICK_SIZE = 0.25


class TestFillRules:
    """Each test maps to one exit path in the fixture."""

    def test_target_hit(self, ten_bar_fixture):
        """Trade 1: market buy bar 0, target 4514.00 hit on bar 2."""
        bars, orders, expected = ten_bar_fixture
        expected_trade = expected[0]

        # TODO: replace with engine call once core is built (Day 3)
        # trades = run_engine(bars, orders, TICK_SIZE, POINT_VALUE, COMMISSION_PER_SIDE)
        # trade = trades[0]
        # assert trade["entry_bar"] == expected_trade["entry_bar"]
        # assert trade["exit_bar"] == expected_trade["exit_bar"]
        # assert trade["entry_price"] == pytest.approx(expected_trade["entry_price"])
        # assert trade["exit_price"] == pytest.approx(expected_trade["exit_price"])
        # assert trade["exit_reason"] == expected_trade["exit_reason"]
        # assert trade["pnl"] == pytest.approx(expected_trade["pnl"], abs=0.01)
        pytest.skip("engine not implemented yet")

    def test_stop_hit_same_bar(self, ten_bar_fixture):
        """Trade 2: market buy bar 4, stop and target both in range on bar 5, stop wins."""
        bars, orders, expected = ten_bar_fixture
        expected_trade = expected[1]

        pytest.skip("engine not implemented yet")

    def test_session_flatten(self, ten_bar_fixture):
        """Trade 3: market buy bar 7, session changes at bar 9, flatten at open."""
        bars, orders, expected = ten_bar_fixture
        expected_trade = expected[2]

        pytest.skip("engine not implemented yet")

    def test_total_pnl(self, ten_bar_fixture):
        """Sum of all three trades must equal +$47.53."""
        bars, orders, expected = ten_bar_fixture
        total = sum(t["pnl"] for t in expected)
        assert total == pytest.approx(47.53, abs=0.01)

        pytest.skip("engine not implemented yet")

    def test_trade_count(self, ten_bar_fixture):
        """Engine must produce exactly 3 trades."""
        pytest.skip("engine not implemented yet")
