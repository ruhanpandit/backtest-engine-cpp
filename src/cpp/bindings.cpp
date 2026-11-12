#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

#include "engine.hpp"

namespace py = pybind11;

std::string hello() { return "backtest-engine-cpp is alive"; }

// Temporary binding for Day 3 testing.
// Day 5 replaces this with zero-copy validation.
py::list run_engine_py(
    py::array_t<double>  open,
    py::array_t<double>  high,
    py::array_t<double>  low,
    py::array_t<double>  close,
    py::array_t<int32_t> session_date,
    py::array_t<int64_t> instrument_id,
    // order fields
    py::array_t<int64_t> signal_bar,
    py::array_t<int32_t> side,
    py::array_t<int32_t> entry_type,
    py::array_t<double>  entry_price,
    py::array_t<double>  stop,
    py::array_t<double>  target,
    py::array_t<int32_t> contracts,
    // params
    double tick_size,
    double point_value,
    double commission_per_side)
{
    auto num_bars   = open.shape(0);
    auto num_orders = signal_bar.shape(0);

    // Build Order structs
    std::vector<engine::Order> orders(static_cast<size_t>(num_orders));
    auto sb  = signal_bar.unchecked<1>();
    auto sd  = side.unchecked<1>();
    auto et  = entry_type.unchecked<1>();
    auto ep  = entry_price.unchecked<1>();
    auto st  = stop.unchecked<1>();
    auto tg  = target.unchecked<1>();
    auto ct  = contracts.unchecked<1>();

    for (int64_t i = 0; i < num_orders; ++i) {
        orders[static_cast<size_t>(i)] = {
            sb(i),
            static_cast<engine::Side>(sd(i)),
            static_cast<engine::EntryType>(et(i)),
            ep(i), st(i), tg(i), ct(i),
        };
    }

    engine::EngineParams params{tick_size, point_value, commission_per_side};

    auto trades = engine::run(
        open.data(), high.data(), low.data(), close.data(),
        session_date.data(), instrument_id.data(),
        num_bars,
        orders.data(), num_orders,
        params);

    // Return as list of dicts (Day 5 will return structured numpy array)
    py::list result;
    for (const auto& t : trades) {
        py::dict d;
        d["entry_bar"]   = t.entry_bar;
        d["exit_bar"]    = t.exit_bar;
        d["entry_price"] = t.entry_price;
        d["exit_price"]  = t.exit_price;
        d["pnl"]         = t.pnl;

        const char* reason = "unknown";
        switch (t.exit_reason) {
            case engine::ExitReason::Target:    reason = "target";  break;
            case engine::ExitReason::Stop:      reason = "stop";    break;
            case engine::ExitReason::Session:   reason = "session"; break;
            case engine::ExitReason::Roll:      reason = "roll";    break;
            case engine::ExitReason::EndOfData: reason = "eod";     break;
        }
        d["exit_reason"] = reason;
        result.append(d);
    }
    return result;
}

PYBIND11_MODULE(_core, m) {
    m.doc() = "C++20 backtest execution engine";
    m.def("hello", &hello, "Smoke test that the C++ extension loads");
    m.def("run_engine", &run_engine_py, "Run the backtest engine");
}
