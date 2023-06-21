// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#include "vcl_iostream.h"
#include "vnl/vnl_matrix.h"
#include "vnl/vnl_matrix_fixed.h"
#include "vnl/vnl_vector.h"

int main() {
  vnl_matrix<double> P(3, 4);
  vnl_vector<double> X(4);
  vcl_cerr << P * X;

  vnl_matrix_fixed<float, 4, 4> m4x4;
  m4x4.fill_diagonal(100.0f);
  return 0;
}
