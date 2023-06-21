#include "QtGui/pyside2_qtgui_python.h"
#include "QtWidgets/pyside2_qtwidgets_python.h"

#include "autodecref.h" // from shiboken
#include "sbkmodule.h"


void initPySide()
{
    Shiboken::AutoDecRef requiredCoreModule(Shiboken::Module::import("PySide2.QtCore"));
    if (requiredCoreModule.isNull()) {
        PyErr_SetString(PyExc_ImportError,"could not import PySide2.QtCore");
    }
    else {
        Shiboken::AutoDecRef requiredWidgetsModule(Shiboken::Module::import("PySide2.QtWidgets"));
        if (requiredWidgetsModule.isNull()) {
            PyErr_SetString(PyExc_ImportError,"could not import PySide2.QtWidgets");
        }
    }
}
