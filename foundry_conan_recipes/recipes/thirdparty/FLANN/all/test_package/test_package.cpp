// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#include <flann/flann.hpp>
#include <flann/ext/lz4.h>

using namespace flann;

int main()
{
  const size_t r = 5;
  const size_t nn = 8;

  //Test a function that requires linking
  const int bound_size = LZ4_compressBound(128);

  Matrix<float> dataset(new float[r * nn], r, nn);

  // construct an randomized kd-tree index using 4 kd-trees
  Index<L2<float> > index(dataset, flann::KDTreeIndexParams(4));
  index.buildIndex();

  delete[] dataset.ptr();

  return 0;
}

