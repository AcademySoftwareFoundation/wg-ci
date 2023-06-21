// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#include <omp.h>
#include <iostream>

int main ()
{
    const int nThreads = 4;
    omp_set_num_threads(nThreads);
    if(nThreads == omp_get_max_threads())
    {
        std::cout << "[SUCCESS] number threads:" << omp_get_max_threads() << std::endl;
        return 0;
    }
    std::cout << "[FAILURE] number threads:" << omp_get_max_threads() << std::endl;
    return -1;
}
