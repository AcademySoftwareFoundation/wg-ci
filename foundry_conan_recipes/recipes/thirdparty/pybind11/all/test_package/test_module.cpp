#include <cmath>
#include <sstream>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

// Define a simple test module to be loaded and exercised.
PYBIND11_MODULE(Pybind11TestModule, m)
{
    m.def("addInts", [](int a, int b)
          {
              return a + b;
          });

    m.def("sqrtFloat", [](float v)
          {
              return sqrtf(v);
          });
    
    m.def("getString", []()
          {
              return "does this work?";
          });

    m.def("getVector", [](size_t n)
          {
              std::vector<int> v;
              for (size_t i = 0; i < n; ++i)
              {
                  v.push_back(i * i);
              }

              return v;
          });

    m.def("getPythonVersion", []()
          {
              std::ostringstream ss;
              ss << PY_MAJOR_VERSION << '.' << PY_MINOR_VERSION << '.' << PY_MICRO_VERSION;
              return ss.str();
          });

}
