#include <fakeit/single_header/standalone/fakeit.hpp>
#include <stddef.h>

struct Interface {
  virtual int foo() = 0;
};

int main() {
  using namespace fakeit;

  Mock<Interface> mock;

  When(Method(mock, foo)).Return(42);

  Interface &inst = mock.get();

  if (inst.foo() == 42) {
    return 0;
  }

  return 1;
}
