#include "Python.h"
#include "datetime.h"
#include "compat.h"

/* Forward declaration. */

typedef PyObject* (*convert_func)(PyObject *ob);
static PyObject * convert_nested(PyObject *ob, convert_func convert_string);

static int
is_any_datetime_object(PyObject* ob) {
    return (
        PyDate_Check(ob) ||
        PyDateTime_Check(ob) ||
        PyTime_Check(ob) ||
        PyDelta_Check(ob) ||
        PyTZInfo_Check(ob)
    );
}

static PyObject*
convert_dict_like(PyObject* ob, convert_func convert_string)
{
    PyObject *new_ob = NULL;
    PyObject *iterator = NULL;
    PyObject *key = NULL;
    PyObject *value = NULL;
    PyObject *new_key = NULL;
    PyObject *new_value = NULL;

    if ((new_ob = PyObject_CallObject((PyObject*) Py_TYPE(ob), NULL)) == NULL) {
        goto error;
    }

    if ((iterator = PyObject_GetIter(ob)) == NULL) {
        goto error;
    }

    while ((key = PyIter_Next(iterator))) {
        /* ensure that the XDECREF doesn't run on variables from the prev loop. */
        value = new_key = new_value = NULL;

        if ((value = PyObject_GetItem(ob, key)) == NULL) {
            goto error;
        }

        if ((new_key = convert_nested(key, convert_string)) == NULL) {
            goto error;
        }

        if ((new_value = convert_nested(value, convert_string)) == NULL) {
            goto error;
        }

        if (PyObject_SetItem(new_ob, new_key, new_value) == -1) {
            goto error;
        }

        Py_DECREF(key);
        Py_DECREF(value);
        Py_DECREF(new_key);
        Py_DECREF(new_value);
    }

    Py_DECREF(iterator);

    if (PyErr_Occurred()) {
        Py_DECREF(new_ob);
        return NULL;
    }

    return new_ob;

error:
    Py_XDECREF(new_ob);
    Py_XDECREF(iterator);
    Py_XDECREF(key);
    Py_XDECREF(value);
    Py_XDECREF(new_key);
    Py_XDECREF(new_value);
    return NULL;
}

static PyObject*
convert_dict(PyObject *ob, convert_func convert_string)
{
    PyObject *key, *value;
    Py_ssize_t pos = 0;
    PyObject *new_ob = PyDict_New();

    while (PyDict_Next(ob, &pos, &key, &value)) {
        if ((key = convert_nested(key, convert_string)) == NULL) {
            Py_DECREF(new_ob);
            return NULL;
        }

        if ((value = convert_nested(value, convert_string)) == NULL) {
            Py_DECREF(new_ob);
            Py_DECREF(key);
            return NULL;
        }

        if(PyDict_SetItem(new_ob, key, value) == -1) {
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

static PyObject*
convert_seq(PyObject *ob, convert_func convert_string)
{
    PyObject *seq = PySequence_Fast(ob, "ob is not a sequence");
    if (seq == NULL) {
        return NULL;
    }

    Py_ssize_t i = 0;
    Py_ssize_t seq_len = PySequence_Fast_GET_SIZE(seq);
    PyObject **items = PySequence_Fast_ITEMS(seq);

    for (i=0; i < seq_len; ++i) {
        PyObject *old_item = items[i];
        PyObject *new_item = convert_nested(old_item, convert_string);
        if (new_item == NULL) {
            Py_DECREF(seq);
            return NULL;
        }
        items[i] = new_item;
        Py_DECREF(old_item);
    }

    return seq;
}

static PyObject*
convert_nested(PyObject *ob, convert_func convert_string)
{
    /* dict. */
    if (PyDict_CheckExact(ob)) {
        return convert_dict(ob, convert_string);
    }

    /* sequence. */
    if (PyTuple_CheckExact(ob) || PyList_CheckExact(ob)) {
        return convert_seq(ob, convert_string);
    }

    /* numbers. */
    if (PyInt_Check(ob) || PyLong_Check(ob) || PyFloat_Check(ob)) {
        Py_INCREF(ob);
        return ob;
    }

    /* bool. */
    if (PyBool_Check(ob)) {
        Py_INCREF(ob);
        return ob;
    }

    /* none. */
    if (ob == Py_None) {
        Py_INCREF(ob);
        return ob;
    }

    if (PyBytes_CheckExact(ob) || PyUnicode_CheckExact(ob) || PyByteArray_CheckExact(ob)) {
        return convert_string(ob);
    }

    if (PyDict_Check(ob)) {
        return convert_dict_like(ob, convert_string);
    }

    if (is_any_datetime_object(ob)) {
        Py_INCREF(ob);
        return ob;
    }

    return PyErr_Format(
        PyExc_TypeError,
        "Got wrong type: %s",
        Py_TYPE(ob)->tp_name);
}

static PyObject*
encode_string(PyObject *ob)
{
    /* bytes are already encoded. */
    if (PyBytes_CheckExact(ob) || PyByteArray_CheckExact(ob)) {
        Py_INCREF(ob);
        return ob;
    }

    return PyUnicode_AsUTF8String(ob);
}

static PyObject*
decode_string(PyObject *ob)
{
    if (PyUnicode_CheckExact(ob)) {
        Py_INCREF(ob);
        return ob;
    }

#if IS_PY2
    if (PyByteArray_CheckExact(ob)) {
        return PyCodec_Decode(ob, "utf-8", "strict");
    }
#endif

    return PyUnicode_FromEncodedObject(ob, "utf-8", "strict");
}

static PyObject*
encode_nested(PyObject *self, PyObject *ob)
{
    return convert_nested(ob, &encode_string);
}

static PyObject*
decode_nested(PyObject *self, PyObject *ob)
{
    return convert_nested(ob, &decode_string);
}

/* python2:
 *  This method returns ob as 'str' or 'unicode'.
 *  What type exactly is returned is up to 'ob'.
 *  This method says, give me a string,
 *  but I don't care if ts type 'str' or 'unicode'
 *
 * python3:
 *  In python3 they made this 'hard' cut between
 *  text (unicode) and opaque data (bytes).
 *  So this method does not make much sense anymore.
 *  Current implementation is simple str(ob).
 */
static PyObject*
as_basestring(PyObject *self, PyObject *ob)
{
#if IS_PY2
    return _PyObject_Str(ob);
#endif

#if IS_PY3
    return PyObject_Str(ob);
#endif
}


static PyMethodDef convert_nested_methods[] = {
    {"encode_nested", encode_nested, METH_O, "Docu"},
    {"decode_nested", decode_nested, METH_O, ""},
    {"as_basestring", as_basestring, METH_O, "Docu"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef moduledef =  {
    PyModuleDef_HEAD_INIT,          /* m_base */
    "_convert_nested",              /* m_name */
    "",                             /* m_doc */
    0,                              /* m_size */
    convert_nested_methods,         /* m_methods */
};

MODULE_INIT_FUNC(_convert_nested)
{
    PyDateTime_IMPORT;
    return PyModule_Create(&moduledef);
}
