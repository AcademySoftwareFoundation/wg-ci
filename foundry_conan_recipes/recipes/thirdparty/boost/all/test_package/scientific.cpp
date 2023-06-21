#include <boost/archive/text_oarchive.hpp>
#include <iostream>
#include <sstream>
#include <string>

int main()
{
  std::stringstream os;
  boost::archive::text_oarchive oa(os);
  oa.use_scientific_output = false;
  oa << 123.12345678901234;

  std::size_t found = os.str().find("e+");
  if (found == std::string::npos) {
    std::cout << "123.12345678901234 is kept as " << os.str() << std::endl;
    return 0;
  }
  else {
    std::cout << "123.12345678901234 is changed to " << os.str() << std::endl;
    return 1;
  }
}
