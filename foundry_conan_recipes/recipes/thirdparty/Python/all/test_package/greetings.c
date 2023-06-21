#include <Python.h>
#include <stdio.h>

static PyObject* greetings_hello(PyObject* self, PyObject* args) {
  const char* name;
  if(!PyArg_ParseTuple(args, "s", &name)) {
    return NULL;
  }
  printf("Hello %s, the world awaits!\n", name);
  return Py_None;
}


static PyMethodDef methods_in_module[] = {
  { "hello",  greetings_hello, METH_VARARGS, "Print some upbeat string for you." },
  { NULL, NULL, 0, NULL },
};


#if PY_MAJOR_VERSION >= 3

static PyModuleDef greetings_module_def = {
  PyModuleDef_HEAD_INIT,
  "greetings",
  NULL,
  -1,
  methods_in_module,
};

PyMODINIT_FUNC PyInit_greetings() {
  PyObject* m;
  m = PyModule_Create(&greetings_module_def);
  if (m == NULL)
    return NULL;

  return m;
}

#else

PyMODINIT_FUNC initgreetings() {
  PyObject* m;
  m = Py_InitModule("greetings", methods_in_module);
  if (m == NULL)
    return;
}

#endif