cmake_minimum_required(VERSION 3.20)
project(backtest_engine LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(_core src/cpp/bindings.cpp)

install(TARGETS _core DESTINATION backtest_engine)
