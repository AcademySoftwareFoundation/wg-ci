#include <nanobind/nanobind.h>

#include <cmath>
#include <sstream>

namespace nb = nanobind;

NB_MODULE(NanobindTestModule, m)
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

  m.def("getList", [](size_t n)
        {
            nb::list l;
            for (size_t i = 0; i < n; ++i) {
                l.append(i * i);
            }

            return l;
        });

  m.def("getPythonVersion", []()
        {
            std::ostringstream ss;
            ss << PY_MAJOR_VERSION << '.' << PY_MINOR_VERSION << '.' << PY_MICRO_VERSION;
            return nb::str(ss.str().c_str());
        });
}
