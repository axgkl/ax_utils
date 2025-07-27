/* Copyright (c) 2015, Red Hat, Inc. and/or its affiliates
 * Licensed under the MIT license; see py3c.h
 */

#ifndef _PY3C_COMPAT_H_
#define _PY3C_COMPAT_H_
#include <Python.h>

#if PY_MAJOR_VERSION >= 3

/***** Python 3 *****/

#define MODULE_INIT_FUNC(name) \
    PyMODINIT_FUNC PyInit_ ## name(void); \
    PyMODINIT_FUNC PyInit_ ## name(void)
#else

/***** Python 2 *****/


#define PyModuleDef_HEAD_INIT 0

typedef struct PyModuleDef {
    int m_base;
    const char* m_name;
    const char* m_doc;
    Py_ssize_t m_size;
    PyMethodDef *m_methods;
} PyModuleDef;

#define PyModule_Create(def) \
    Py_InitModule3((def)->m_name, (def)->m_methods, (def)->m_doc)

#define MODULE_INIT_FUNC(name) \
    static PyObject *PyInit_ ## name(void); \
    PyMODINIT_FUNC init ## name(void); \
    PyMODINIT_FUNC init ## name(void) { PyInit_ ## name(); } \
    static PyObject *PyInit_ ## name(void)


#endif

#endif
