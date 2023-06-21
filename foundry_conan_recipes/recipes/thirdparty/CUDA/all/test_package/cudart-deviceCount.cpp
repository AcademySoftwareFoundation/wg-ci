#include <cuda_runtime.h>
#include <iostream>

int main()
{
  std::cout << "CUDA Device Query (Runtime API) test" << std::endl;

  int deviceCount = 0;
  cudaError_t error_id = cudaGetDeviceCount(&deviceCount);

  if (error_id != cudaSuccess) {
    std::cout << "cudaGetDeviceCount returned " << static_cast<int>(error_id)
              << " - error: " << cudaGetErrorString(error_id) << std::endl;
    if (error_id == cudaErrorInsufficientDriver) {
      std::cout << "This is expected on systems with no CUDA driver installed." << std::endl;
      return 0;
    }
    else {
      std::cout << "FAILED!" << std::endl;
      exit(EXIT_FAILURE);
    }
  }

  // cudaGetDeviceCount returns 0 if there are no CUDA capable devices.
  if (deviceCount == 0) {
    std::cout << "There are no available CUDA device(s)" << std::endl;
  }
  else {
    std::cout << "Detected " << deviceCount << " CUDA Capable device(s)" << std::endl;
  }

  return 0;
}