#include "gperftools/tcmalloc.h"
#include "gperftools/malloc_extension.h"

#include <iostream>

int main() {

  static constexpr size_t kSize = 64;
  void* memory = tc_malloc(kSize);

  if (memory == nullptr) {
    std::cerr << "failed to allocate memory" << std::endl;
    return 1;
  }

  size_t size = tc_malloc_size(memory);

  if (size < kSize) {
    std::cerr << "failed to allocate " << kSize << " bytes" << std::endl;
    return 2;
  }

  static constexpr size_t kReallocSize = kSize * 2 * 2;
  memory = tc_realloc(memory, kReallocSize);

  if (memory == nullptr) {
    std::cerr << "failed to reallocate memory" << std::endl;
    return 3;
  }

  size = tc_malloc_size(memory);

  if (size < kReallocSize) {
    std::cerr << "failed to reallocate to " << kReallocSize << " bytes" << std::endl;
    return 4;
  }

  tc_free(memory);

  MallocExtension::instance()->ReleaseFreeMemory();

  std::cout << "TC Malloc appears to be working as expected" << std::endl;
  return 0;
}
