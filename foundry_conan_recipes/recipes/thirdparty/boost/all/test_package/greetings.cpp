#include <boost/python.hpp>

char const* hello_world() {
  return "Hello, World!";
}

BOOST_PYTHON_MODULE(greetings) {
  using namespace boost::python;
  def("hello", hello_world);
}