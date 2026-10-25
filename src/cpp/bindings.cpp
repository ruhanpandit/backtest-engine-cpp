#include <pybind11/pybind11.h>

namespace py = pybind11;

// Day 1 hello-world -- replaced with real bindings on Day 5
std::string hello() { return "backtest-engine-cpp is alive"; }

PYBIND11_MODULE(_core, m) {
    m.doc() = "C++20 backtest execution engine";
    m.def("hello", &hello, "Smoke test that the C++ extension loads");
}
