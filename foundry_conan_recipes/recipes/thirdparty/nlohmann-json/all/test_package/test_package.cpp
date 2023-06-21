// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#include <iostream>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

int main() {
    const json data = {
        {"pi", 3.141},
        {"happy", true},
        {"name", "Niels"},
        {"nothing", nullptr},
        {"answer", {
            {"everything", 42}
        }},
        {"list", {1, 0, 2}},
        {"object", {
            {"currency", "USD"},
            {"value", 42.99}
        }}
    };

    auto f = data["pi"].get<float>();
    std::cout << data.dump(4) << std::endl;
    return 0;
}
