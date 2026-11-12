#pragma once

#include <cmath>
#include <cstdint>
#include <vector>

namespace engine {

// ---- Order / Trade structs ------------------------------------------------

enum class Side : int32_t { Buy = 1, Sell = -1 };
enum class EntryType : int32_t { Market = 0, Limit = 1 };

enum class ExitReason : int32_t {
    Target  = 0,
    Stop    = 1,
    Session = 2,
    Roll    = 3,
    EndOfData = 4,
};

struct Order {
    int64_t signal_bar;
    Side    side;
    EntryType entry_type;
    double  entry_price;   // 0.0 for market orders
    double  stop;
    double  target;
    int32_t contracts;
};

struct Trade {
    int64_t entry_bar;
    int64_t exit_bar;
    double  entry_price;
    double  exit_price;
    ExitReason exit_reason;
    double  pnl;           // net of commission, rounded to the cent
};

// ---- Engine parameters ----------------------------------------------------

struct EngineParams {
    double tick_size;          // 0.25 for ES/MES/NQ/MNQ
    double point_value;        // MES=5.0, MNQ=2.0
    double commission_per_side;
};

// ---- Core function --------------------------------------------------------

inline double round_cent(double x) {
    return std::round(x * 100.0) / 100.0;
}

inline std::vector<Trade> run(
    // bar arrays (length = num_bars)
    const double* open,
    const double* high,
    const double* low,
    const double* close,
    const int32_t* session_date,
    const int64_t* instrument_id,
    int64_t num_bars,
    // orders (length = num_orders)
    const Order* orders,
    int64_t num_orders,
    // params
    const EngineParams& params)
{
    std::vector<Trade> trades;
    trades.reserve(static_cast<size_t>(num_orders));

    for (int64_t oi = 0; oi < num_orders; ++oi) {
        const auto& ord = orders[oi];
        int64_t entry_bar = ord.signal_bar + 1;

        if (entry_bar >= num_bars) continue;

        // -- Compute entry price ----------------------------------------
        double entry_price = 0.0;
        int side_sign = static_cast<int>(ord.side);  // +1 buy, -1 sell

        if (ord.entry_type == EntryType::Market) {
            // Market: open + 1 tick slippage in trade direction
            entry_price = open[entry_bar]
                        + side_sign * params.tick_size;
        } else {
            // Limit entry (Day 4)
            // TODO: implement limit fill logic
            continue;
        }

        // -- Scan for exit ----------------------------------------------
        bool filled = false;

        for (int64_t bi = entry_bar; bi < num_bars; ++bi) {

            // Session flatten: next bar has a different session_date
            // Check if we need to flatten at the *next* bar's open
            if (bi + 1 < num_bars
                && session_date[bi + 1] != session_date[bi]) {
                double exit_price = open[bi + 1];
                double raw_pnl = (exit_price - entry_price)
                               * side_sign * params.point_value
                               * ord.contracts;
                trades.push_back({
                    entry_bar, bi + 1, entry_price, exit_price,
                    ExitReason::Session,
                    round_cent(raw_pnl - 2.0 * params.commission_per_side
                               * ord.contracts),
                });
                filled = true;
                break;
            }

            // Roll flatten: next bar has a different instrument_id
            if (bi + 1 < num_bars
                && instrument_id[bi + 1] != instrument_id[bi]) {
                double exit_price = open[bi + 1];
                double raw_pnl = (exit_price - entry_price)
                               * side_sign * params.point_value
                               * ord.contracts;
                trades.push_back({
                    entry_bar, bi + 1, entry_price, exit_price,
                    ExitReason::Roll,
                    round_cent(raw_pnl - 2.0 * params.commission_per_side
                               * ord.contracts),
                });
                filled = true;
                break;
            }

            // Stop and target check
            bool stop_in_range = false;
            bool target_in_range = false;

            if (ord.side == Side::Buy) {
                stop_in_range   = low[bi]  <= ord.stop;
                target_in_range = high[bi] >= ord.target;
            } else {
                stop_in_range   = high[bi] >= ord.stop;
                target_in_range = low[bi]  <= ord.target;
            }

            // Rule #8: both in range on same bar -> stop wins
            if (stop_in_range && target_in_range) {
                target_in_range = false;
            }

            if (stop_in_range) {
                // Gap-through: bar opens past the stop
                double exit_price;
                if (ord.side == Side::Buy) {
                    exit_price = (open[bi] < ord.stop)
                               ? open[bi] : ord.stop;
                } else {
                    exit_price = (open[bi] > ord.stop)
                               ? open[bi] : ord.stop;
                }

                double raw_pnl = (exit_price - entry_price)
                               * side_sign * params.point_value
                               * ord.contracts;
                trades.push_back({
                    entry_bar, bi, entry_price, exit_price,
                    ExitReason::Stop,
                    round_cent(raw_pnl - 2.0 * params.commission_per_side
                               * ord.contracts),
                });
                filled = true;
                break;
            }

            if (target_in_range) {
                double exit_price = ord.target;
                double raw_pnl = (exit_price - entry_price)
                               * side_sign * params.point_value
                               * ord.contracts;
                trades.push_back({
                    entry_bar, bi, entry_price, exit_price,
                    ExitReason::Target,
                    round_cent(raw_pnl - 2.0 * params.commission_per_side
                               * ord.contracts),
                });
                filled = true;
                break;
            }
        }

        // If we scanned all bars with no exit, flatten at last close
        if (!filled) {
            double exit_price = close[num_bars - 1];
            double raw_pnl = (exit_price - entry_price)
                           * side_sign * params.point_value
                           * ord.contracts;
            trades.push_back({
                entry_bar, num_bars - 1, entry_price, exit_price,
                ExitReason::EndOfData,
                round_cent(raw_pnl - 2.0 * params.commission_per_side
                           * ord.contracts),
            });
        }
    }

    return trades;
}

}  // namespace engine
