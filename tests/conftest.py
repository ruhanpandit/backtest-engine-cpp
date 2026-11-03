"""Shared fixtures for backtest-engine-cpp tests."""

import numpy as np
import pytest


@pytest.fixture()
def ten_bar_fixture():
    """10-bar MES series with 3 hand-calculated trades.

    Bars:
        Bar | Open     | High     | Low      | Close    | Session  | InstID
        ----|----------|----------|----------|----------|----------|-------
          0 | 4500.00  | 4505.00  | 4498.00  | 4503.00  | 20230901 | 1
          1 | 4503.00  | 4510.00  | 4501.00  | 4508.00  | 20230901 | 1
          2 | 4508.00  | 4515.00  | 4506.00  | 4514.00  | 20230901 | 1
          3 | 4514.00  | 4516.00  | 4509.00  | 4510.00  | 20230901 | 1
          4 | 4510.00  | 4512.00  | 4504.00  | 4505.00  | 20230901 | 1
          5 | 4505.00  | 4507.00  | 4500.00  | 4501.00  | 20230901 | 1
          6 | 4501.00  | 4506.00  | 4499.00  | 4504.00  | 20230901 | 1
          7 | 4504.00  | 4508.00  | 4497.00  | 4498.00  | 20230901 | 1
          8 | 4498.00  | 4503.00  | 4495.00  | 4500.00  | 20230901 | 1
          9 | 4500.00  | 4502.00  | 4496.00  | 4499.00  | 20230902 | 1

    Orders:
        Trade 1: signal bar 0, market buy, stop 4500.00, target 4514.00
        Trade 2: signal bar 4, market buy, stop 4503.00, target 4506.00
        Trade 3: signal bar 7, market buy, stop 4490.00, target 4510.00

    Expected results (MES: $5/point, tick 0.25, commission $0.62/side):
        Trade 1: entry bar 1 @ 4503.25, exit bar 2 @ 4514.00, target hit, +$52.51
        Trade 2: entry bar 5 @ 4505.25, exit bar 5 @ 4503.00, stop (same-bar), -$12.49
        Trade 3: entry bar 8 @ 4498.25, exit bar 9 @ 4500.00, session flatten, +$7.51
        Total: +$47.53
    """
    bars = {
        "ts_ns": np.array([
            1_693_526_400_000_000_000 + i * 60_000_000_000 for i in range(10)
        ], dtype=np.int64),
        "open": np.array(
            [4500.0, 4503.0, 4508.0, 4514.0, 4510.0,
             4505.0, 4501.0, 4504.0, 4498.0, 4500.0],
            dtype=np.float64,
        ),
        "high": np.array(
            [4505.0, 4510.0, 4515.0, 4516.0, 4512.0,
             4507.0, 4506.0, 4508.0, 4503.0, 4502.0],
            dtype=np.float64,
        ),
        "low": np.array(
            [4498.0, 4501.0, 4506.0, 4509.0, 4504.0,
             4500.0, 4499.0, 4497.0, 4495.0, 4496.0],
            dtype=np.float64,
        ),
        "close": np.array(
            [4503.0, 4508.0, 4514.0, 4510.0, 4505.0,
             4501.0, 4504.0, 4498.0, 4500.0, 4499.0],
            dtype=np.float64,
        ),
        "volume": np.array(
            [100, 150, 200, 120, 130, 140, 110, 160, 180, 90],
            dtype=np.float64,
        ),
        "instrument_id": np.array(
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            dtype=np.int64,
        ),
        "session_date": np.array(
            [20230901, 20230901, 20230901, 20230901, 20230901,
             20230901, 20230901, 20230901, 20230901, 20230902],
            dtype=np.int32,
        ),
    }

    # Orders: signal_bar, side (1=buy), entry_type (0=market), entry_price,
    #         stop, target, contracts
    orders = np.array([
        (0, 1, 0, 0.0,    4500.0, 4514.0, 1),
        (4, 1, 0, 0.0,    4503.0, 4506.0, 1),
        (7, 1, 0, 0.0,    4490.0, 4510.0, 1),
    ], dtype=[
        ("signal_bar", np.int64),
        ("side", np.int32),        # 1 = buy, -1 = sell
        ("entry_type", np.int32),  # 0 = market, 1 = limit
        ("entry_price", np.float64),
        ("stop", np.float64),
        ("target", np.float64),
        ("contracts", np.int32),
    ])

    expected_trades = [
        {
            "entry_bar": 1,
            "exit_bar": 2,
            "entry_price": 4503.25,
            "exit_price": 4514.00,
            "exit_reason": "target",
            "pnl": 52.51,
        },
        {
            "entry_bar": 5,
            "exit_bar": 5,
            "entry_price": 4505.25,
            "exit_price": 4503.00,
            "exit_reason": "stop",
            "pnl": -12.49,
        },
        {
            "entry_bar": 8,
            "exit_bar": 9,
            "entry_price": 4498.25,
            "exit_price": 4500.00,
            "exit_reason": "session",
            "pnl": 7.51,
        },
    ]

    return bars, orders, expected_trades
