//
// Copyright (c) 2023 The Foundry Visionmongers Ltd.  All Rights Reserved.
//

#include "range/v3/all.hpp"
#include <iostream>

int main() {

  auto range = ranges::views::iota(0) |
               ranges::views::filter([](auto const i) { return i % 2 == 0; }) |
               ranges::views::transform([](auto const i) { return i * 5; }) |
               ranges::views::take(10) | ranges::views::reverse;

  auto const sum = ranges::accumulate(range, 0);

  std::cout << "range: " << range << std::endl;
  std::cout << "sum: " << sum << std::endl;

  bool passed = true;
  passed &= (range | ranges::to_vector) ==
            std::vector<int>{90, 80, 70, 60, 50, 40, 30, 20, 10, 0};
  passed &= sum == 450;

  return passed ? 0 : 1;
}