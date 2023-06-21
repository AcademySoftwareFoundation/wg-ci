#include <iostream>

#include <libxml/xmlversion.h>


int main(int, char**) {
  LIBXML_TEST_VERSION
  std::cout << "Using libxml2 version " << LIBXML_DOTTED_VERSION << "\n";
  return 0;
}
