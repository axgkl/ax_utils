#include "Python.h"
#include "compat.h"


typedef struct {
    PyObject* key;
    char* prev;
} key_iterator;


static int
key_iterator_init(key_iterator* it, PyObject* key)
{
    if ((it->prev = PyStr_AsString(key)) == NULL) {
        return -1;
    }

    return 0;
}

static int
key_iterator_next(key_iterator* it, PyObject** dst)
{
    register char* tmp;

    if (it->prev == NULL) {
        (*dst) = NULL;
        PyErr_Format(PyExc_RuntimeError, "key_iterator_next called too often");
        return -1;
    }

    tmp = strchr(it->prev, '.');

    if (tmp == NULL) {
        (*dst) = PyStr_FromString(it->prev);
    } else {
        (*dst) = PyStr_FromStringAndSize(it->prev, tmp - it->prev);
        tmp += 1;
    }

    it->prev = tmp;

    if ((*dst) == NULL) {
        return -1;
    } else if (tmp == NULL) {
        return 2;
    } else {
        return 1;
    }
}


static int
_recursive(PyObject* names, PyObject* to_add, PyObject* curr_node)
{
    int rc = 0;
    PyObject* name;
    PyObject* value;
    PyObject* tmp;
    PyObject* sep;
    Py_ssize_t pos=0;

    if (PyDict_Check(curr_node)) {
        while (PyDict_Next(curr_node, &pos, &name, &value)) {
            if (PyList_Append(names, name) == -1) {
                return -1;
            }

            if (_recursive(names, to_add, value) == -1) {
                return -1;
            }

            if (PySequence_DelItem(names, PyList_Size(names) - 1) == -1) {
                return -1;
            }
        }

    } else {
        /* We rely here on python doing caching. */
        if ((sep = PyStr_FromString(".")) == NULL) {
            return -1;
        }

        if ((tmp = PyStr_Join(sep, names)) == NULL) {
            Py_DECREF(sep);
            return -1;
        }

        rc = PyDict_SetItem(to_add, tmp, curr_node);
        Py_DECREF(sep);
        Py_DECREF(tmp);
    }

    return rc;
}

static PyObject*
tree_to_props(PyObject* p_self, PyObject* args)
{
    PyObject *tree, *props, *names;
    if (!PyArg_ParseTuple(args, "O!", &PyDict_Type, &tree)) {
        return NULL;
    }

    props = PyDict_New();
    names = PyList_New(0);

    if (_recursive(names, props, tree) == -1) {
        Py_DECREF(props);
        Py_DECREF(names);
        return NULL;
    } else {
        Py_DECREF(names);
        return props;
    }
}

static PyObject*
props_to_tree(PyObject *p_self, PyObject *args)
{
    int rc;
    PyObject* props;
    PyObject* tree;
    PyObject* name;
    PyObject* value;
    PyObject* local;
    PyObject* tmp_local = NULL;
    PyObject* tmp_key = NULL;
    Py_ssize_t pos = 0;
    key_iterator it;

    if(!PyArg_ParseTuple(args, "O!O", &PyDict_Type, &props, &tree)) {
        return NULL;
    }

    while (PyDict_Next(props, &pos, &name, &value)) {
        if (key_iterator_init(&it, name) == -1) {
            return NULL;
        }

        local = tree;
        Py_INCREF(local);

        while ((rc = key_iterator_next(&it, &tmp_key)) == 1) {
            if ((tmp_local = PyObject_GetItem(local, tmp_key)) == NULL) {
                goto error_in_loop;
            }

            Py_DECREF(tmp_key);
            Py_DECREF(local);
            local = tmp_local;
        }

        if (rc == -1) {
            goto error_in_loop;
        }

        if (PyObject_SetItem(local, tmp_key, value) == -1) {
            goto error_in_loop;
        }

        Py_DECREF(tmp_key);
        Py_DECREF(local);
    }

    Py_INCREF(tree);
    return tree;

error_in_loop:
    Py_XDECREF(tmp_key);
    Py_XDECREF(local);
    return NULL;
}

static PyMethodDef props_to_tree_methods[] = {
    {"_props_to_tree", props_to_tree, METH_VARARGS, ""},
    {"_tree_to_props", tree_to_props, METH_VARARGS, ""},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,  /* m_base */
    "_props_to_tree",       /* m_name */
    "",                     /* m_doc */
    0,                      /* m_size */
    props_to_tree_methods,  /* m_methods */
};


MODULE_INIT_FUNC(_props_to_tree)
{
    return PyModule_Create(&moduledef);
}
