/* Copyright (c) 2015, Red Hat, Inc. and/or its affiliates
 * Licensed under the MIT license; see py3c.h
 */

#ifndef _PY3C_COMPAT_H_
#define _PY3C_COMPAT_H_
#include <Python.h>

#if PY_MAJOR_VERSION >= 3

/***** Python 3 *****/
#define IS_PY2 0
#define IS_PY3 1

#define MODULE_INIT_FUNC(name) \
    PyMODINIT_FUNC PyInit_ ## name(void); \
    PyMODINIT_FUNC PyInit_ ## name(void)

#define PyStr_Check PyUnicode_Check
#define PyStr_FromString PyUnicode_FromString
#define PyStr_FromStringAndSize PyUnicode_FromStringAndSize
#define PyStr_AsString PyUnicode_AsUTF8
#define PyStr_AsStringAndSize PyUnicode_AsUTF8AndSize

#else


/***** Python 2 *****/

#define IS_PY2 1
#define IS_PY3 0
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

#define PyStr_Check PyString_Check
#define PyStr_FromString PyString_FromString
#define PyStr_FromStringAndSize PyString_FromStringAndSize
#define PyStr_AsString PyString_AsString


static const char*
PyStr_AsStringAndSize(PyObject *ob, Py_ssize_t *size)
{
    char *buf;
    if (PyString_AsStringAndSize(ob, &buf, size) == -1) {
        return NULL;
    }

    return buf;
}

#if PY_MINOR_VERSION != 7 || (PY_MINOR_VERSION == 7 && PY_MICRO_VERSION < 12)
#define PyDict_GetItemWithError PyDict_GetItem
#else
#define PyDict_GetItemWithError _PyDict_GetItemWithError
#endif

#endif

#endif
