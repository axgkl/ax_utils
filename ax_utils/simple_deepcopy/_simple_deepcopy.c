#include "Python.h"
#include "compat.h"
#include "datetime.h"

/* Fallback to pythons slow deepcopy if a object type is not known. */
static PyObject* slow_deepcopy = NULL;

/* AXtree class. */
static PyObject* AXTree = NULL;

/* Forward declarations. */
static PyObject* _deepcopy(PyObject* ob);
static PyObject* _deepcopy_dict(PyObject* ob);
static PyObject* _deepcopy_tuple(PyObject* ob);
static PyObject* _deepcopy_list(PyObject* ob);
static PyObject* _deepcopy_set(PyObject* ob);
static PyObject* _deepcopy_axtree(PyObject* ob);
static PyObject* _deepcopy_dict_impl(PyObject* ob, PyObject* new_ob);

static PyObject*
deepcopy(PyObject* self, PyObject* ob)
{
    return _deepcopy(ob);
}


static PyObject*
_deepcopy(PyObject* ob)
{
    if (PyDict_CheckExact(ob)) {
        return _deepcopy_dict(ob);
    }

    if (PyTuple_CheckExact(ob)) {
       return _deepcopy_tuple(ob);
    }

    if (PyList_CheckExact(ob)) {
        return _deepcopy_list(ob);
    }

    if (PyBytes_CheckExact(ob) || PyUnicode_CheckExact(ob)) {
        Py_INCREF(ob);
        return ob;
    }

    if (PyInt_CheckExact(ob) || PyLong_CheckExact(ob) || PyFloat_CheckExact(ob)) {
        Py_INCREF(ob);
        return ob;
    }

    if (PyBool_Check(ob)) {
        Py_INCREF(ob);
        return ob;
    }

    if (ob == Py_None) {
        Py_INCREF(ob);
        return ob;
    }

    if (PyAnySet_CheckExact(ob)) {
        return _deepcopy_set(ob);
    }

    if (PyDateTime_CheckExact(ob)) {
        Py_INCREF(ob);
        return ob;
    }

    if (PyObject_IsInstance(ob, AXTree)) {
        return _deepcopy_axtree(ob);
    }

    return PyObject_CallFunctionObjArgs(slow_deepcopy, ob, NULL);
}

static PyObject*
_deepcopy_axtree(PyObject* ob)
{
    return _deepcopy_dict_impl(ob, PyObject_CallObject(AXTree, NULL));
}

static PyObject*
_deepcopy_dict(PyObject* ob)
{
    return _deepcopy_dict_impl(ob, PyDict_New());
}

static PyObject*
_deepcopy_tuple(PyObject* ob)
{
    PyObject* new_item = NULL;
    Py_ssize_t i = 0;

    PyObject* new_ob = PyTuple_New(PyTuple_GET_SIZE(ob));
    if (new_ob == NULL) {
        return NULL;
    }

    for (i=0; i<PyTuple_GET_SIZE(ob); i++) {
        if ((new_item = _deepcopy(PyTuple_GET_ITEM(ob, i))) == NULL) {
            Py_DECREF(new_ob);
            return NULL;
        }
        PyTuple_SET_ITEM(new_ob, i, new_item);
    }
    return new_ob;
}

static PyObject*
_deepcopy_list(PyObject* ob)
{
    PyObject* new_item = NULL;
    Py_ssize_t i = 0;

    PyObject* new_ob = PyList_New(PyList_GET_SIZE(ob));
    if (new_ob == NULL) {
        return NULL;
    }

    for (i=0; i<PyList_GET_SIZE(ob); i++) {
        if ((new_item = _deepcopy(PyList_GET_ITEM(ob, i))) == NULL) {
            Py_DECREF(new_ob);
            return NULL;
        }
        PyList_SET_ITEM(new_ob, i, new_item);
    }
    return new_ob;
}

static PyObject*
_deepcopy_set(PyObject* ob)
{
    PyObject* new_item = NULL;
    PyObject* item = NULL;
    PyObject* item2 = NULL;

    if (PyFrozenSet_CheckExact(ob)) {
        new_item = PyFrozenSet_New(NULL);
    }

    else {
        new_item = PySet_New(NULL);
    }

    if (new_item == NULL) {
        return NULL;
    }

    PyObject* iter = PyObject_GetIter(ob);
    while((item = PyIter_Next(iter))) {
        item2 = _deepcopy(item);
        Py_DECREF(item);
        PySet_Add(new_item, item2);
        Py_DECREF(item2);
    }

    Py_DECREF(iter);
    return new_item;
}

/* This code is shared between _deepcopy_axtree and _deepcopy_dict.
 * The good thing is that underneath AXTree is also a 'dict'.
 * => The PyDict_Next PyDict_SetItem work there too.
 * Which is very close to 'ludicrous speed'.
 */
static PyObject*
_deepcopy_dict_impl(PyObject* ob, PyObject* new_ob)
{
    PyObject* key = NULL;
    PyObject* value = NULL;
    Py_ssize_t pos = 0;

    if (new_ob == NULL) {
        return NULL;
    }

    while (PyDict_Next(ob, &pos, &key, &value)) {
        if ((key = _deepcopy(key)) == NULL) {
            Py_DECREF(new_ob);
            return NULL;
        }

        if ((value = _deepcopy(value)) == NULL) {
            Py_DECREF(new_ob);
            Py_DECREF(key);
            return NULL;
        }

        if (PyDict_SetItem(new_ob, key, value) == -1) {
            Py_DECREF(key);
            Py_DECREF(value);
            Py_DECREF(new_ob);
            return NULL;
        }
        else {
            Py_DECREF(key);
            Py_DECREF(value);
        }

    }
    return new_ob;
}

static PyMethodDef simple_deepcopy_methods[] = {
    {"deepcopy", deepcopy, METH_O, "Docu"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,  /* m_base */
    "_simple_deepcopy",     /* m_name */
    "",                     /* m_doc */
    -1,                     /* m_size */
    simple_deepcopy_methods,    /* m_methods */
};



MODULE_INIT_FUNC(_simple_deepcopy)
{
    PyObject* mod_name = NULL;
    PyObject* mod_ob = NULL;

    /* Import copy module and get the deepcopy function. */
    mod_name = PyStr_FromString("copy");

    mod_ob = PyImport_Import(mod_name);
    Py_DECREF(mod_name);
    if (mod_ob == NULL) {
        return NULL;
    }

    slow_deepcopy = PyObject_GetAttrString(mod_ob, "deepcopy");
    Py_DECREF(mod_ob);
    if (slow_deepcopy == NULL) {
        return NULL;
    }

    /* Import ax_tree module and get the AXTree class. */
    mod_name = PyStr_FromString("ax_utils.ax_tree.ax_tree");

    mod_ob = PyImport_Import(mod_name);
    Py_DECREF(mod_name);
    if (mod_ob == NULL) {
        return NULL;
    }

    AXTree = PyObject_GetAttrString(mod_ob, "AXTree");
    Py_DECREF(mod_ob);
    if (AXTree == NULL) {
        return NULL;
    }

    /* Import the datetime C API. */
    PyDateTime_IMPORT;

    /* Initialze the current module. */
    return PyModule_Create(&moduledef);
}
