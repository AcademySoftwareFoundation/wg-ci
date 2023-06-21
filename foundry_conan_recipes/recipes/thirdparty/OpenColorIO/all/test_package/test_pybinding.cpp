#include <PyOpenColorIO/PyOpenColorIO.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
namespace py = pybind11;

namespace OCIO = OCIO_NAMESPACE;

PYBIND11_MODULE(PyOcioBindTestModule, m) {
    m.def("checkPyOCIOTransform", [](py::object transform) 
    {
        return OCIO::IsPyTransform(transform.ptr());
    });
}