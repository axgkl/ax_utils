#include "stack.c"
#include "Python.h"
#include "compat.h"
#include <string.h>

typedef struct {
    PyDictObject dict;
} AXTree;


static int
_add_value(PyObject *tree, PyObject *key, PyObject *value)
{
    if (!PyDict_Check(tree)) {
        PyErr_Format(PyExc_TypeError, "Node is not a tree");
        return -1;
    }

    if (PyDict_Check(value) && !PyObject_TypeCheck(value, tree->ob_type)) {
        value = PyObject_CallFunction((PyObject*)tree->ob_type, "O", value);
        if(value == NULL) {
            return -1;
        }

        /* Setitem increments the refcount */
        const int rc = PyDict_SetItem(tree, key, value);

        /* PyObject_CallFunction creates a new reference */
        Py_DECREF(value);

        return rc;
    }

    return PyDict_SetItem(tree, key, value);
}

static PyObject*
_add_new_subtree(PyObject *tree, PyObject *key)
{
    if (!PyDict_Check(tree)) {
        return PyErr_Format(PyExc_TypeError, "Node is not a tree");
    }

    PyObject * new_tree;

    if ((new_tree = PyObject_CallObject((PyObject*)tree->ob_type, 0)) == NULL) {
        return NULL;
    }

    if (PyDict_SetItem(tree, key, new_tree) == -1) {
        Py_DECREF(new_tree);
        return NULL;
    }

    /* Reference is hold by tree */
    Py_DECREF(new_tree);
    return new_tree;
}

/*
 * key is of type char ** because the caller has then the name of the leaf
 */
static PyObject *
_find_node(PyObject *tree, char **name, int create_no_exists)
{
    register char *tmp;
    PyObject *new_tree;
    PyObject *lookup_ob;

    tmp = strchr(*name, '.');
    while (tmp) {
        if(!PyDict_Check(tree)) {
            return PyErr_Format(PyExc_KeyError, "Wrong subtree:%s", *name);
        }

        if ((lookup_ob = PyStr_FromStringAndSize(*name, tmp-*name)) == NULL) {
            return NULL;
        }

        new_tree = PyDict_GetItemWithError(tree, lookup_ob);
        if ((new_tree == NULL) && PyErr_Occurred()) {
            Py_DECREF(lookup_ob);
            return NULL;
        }

        if (new_tree == NULL) {
            if (create_no_exists) {
                if ((new_tree = _add_new_subtree(tree, lookup_ob))==NULL) {
                    Py_DECREF(lookup_ob);
                    return NULL;
                }
            }
            else {
                Py_DECREF(lookup_ob);
                return PyErr_Format(PyExc_KeyError, "Wrong subtree:%s", *name);
            }
        }
        Py_DECREF(lookup_ob);
        tree = new_tree;
        *name = tmp + 1;
        tmp = strchr(*name, '.');
    }

    return tree;
}

static int
ax_tree_ass_subscript(PyObject *tree, PyObject *key, PyObject *value)
{
    char *name;
    int ret;

    if (value == NULL) {
        /* Currently a '.' inside the key is not supported */
        return PyDict_DelItem(tree, key);
    }

    name = PyStr_AsString(key);
    if (name == NULL) {
        return -1;
    }

    if ((tree = _find_node(tree, &name, 1)) == NULL) {
        return -1;
    }

    key = PyStr_FromString(name);
    ret = _add_value(tree, key, value);
    Py_DECREF(key);
    return ret;
}

static PyObject *
_lookup_in_dict(PyObject *mp, PyObject *key, char *name)
{
    PyObject *val = PyDict_GetItemWithError(mp, key);
    if (val == NULL) {
        if (PyErr_Occurred()) {
            return NULL;
        }

        return PyErr_Format(PyExc_KeyError, "Wrong leaf: %s", name);
    }

    /* PyDict_GetItem returns a borrowed reference. */
    Py_INCREF(val);
    return val;
}

static PyObject *
ax_tree_subscript(PyObject *tree, PyObject *key)
{
    char *name = PyStr_AsString(key);
    if (name == NULL) {
        return NULL;
    }

    PyObject *subtree = _find_node(tree, &name, 0);
    if (subtree == NULL) {
        return NULL;
    }

    if (tree == subtree) {
        return _lookup_in_dict(tree, key, name);
    }

    if (!PyDict_Check(subtree)) {
        return PyErr_Format(PyExc_KeyError, "Wrong leaf: %s", name);
    }

    key = PyStr_FromString(name);
    tree = _lookup_in_dict(subtree, key, name);
    Py_DECREF(key);

    return tree;
}

static PyMappingMethods AXTree_as_mapping = {
    NULL, /*mp_length*/
    (binaryfunc)ax_tree_subscript, /*mp_subscript*/
    (objobjargproc)ax_tree_ass_subscript, /* mp_ass_subscript */
};


/* Return 1 if `key` is in dict `op`, 0 if not, and -1 on error. */
static int
ax_tree_sq_contains(PyObject *tree, PyObject *key)
{

    PyObject *val = ax_tree_subscript(tree, key);

    if (val == NULL) {
        if (PyErr_ExceptionMatches(PyExc_KeyError)) {
            PyErr_Clear();
            return 0;
        }
        return -1;
    }

    Py_DECREF(val);
    return 1;
}

/* To implement "key in dict" */
static PySequenceMethods AXTree_as_sequence = {
    0,                          /* sq_length */
    0,                          /* sq_concat */
    0,                          /* sq_repeat */
    0,                          /* sq_item */
    0,                          /* sq_slice */
    0,                          /* sq_ass_item */
    0,                          /* sq_ass_slice */
    ax_tree_sq_contains,        /* sq_contains */
    0,                          /* sq_inplace_concat */
    0,                          /* sq_inplace_repeat */
};

/* Declaration for possible iterator types */
#define LEAF_KEYS 0
#define LEAF_VALUES 1
#define LEAF_ITEMS 2

/* forward declarations */
static PyObject * ax_tree_iter_new(PyObject *tree, unsigned int type);
PyTypeObject AXTreeIteratorType;

static PyObject *
ax_tree_iter_leaf_keys(PyObject *tree)
{
    return ax_tree_iter_new(tree, LEAF_KEYS);
}

static PyObject *
ax_tree_iter_leaf_values(PyObject *tree)
{
    return ax_tree_iter_new(tree, LEAF_VALUES);
}

static PyObject *
ax_tree_iter_leaf_items(PyObject *tree)
{
    return ax_tree_iter_new(tree, LEAF_ITEMS);
}

static PyObject *
ax_tree_iter_leave_keys(PyObject *tree)
{
    char warning[] = "iter_leave_keys is deprecated, use iter_leaf_keys instead. " \
                     "The iter_leave_keys method will be removed 2014-05-15";
    if (PyErr_WarnEx(PyExc_DeprecationWarning, warning, 1) == -1) {
        return NULL;
    }
    return ax_tree_iter_leaf_keys(tree);
}

static PyObject *
ax_tree_iter_leave_values(PyObject *tree)
{
    char warning[] = "iter_leave_values is deprecated, use iter_leaf_values instead. " \
                     "The iter_leave_values method will be removed 2014-05-15";
    if (PyErr_WarnEx(PyExc_DeprecationWarning, warning, 1) == -1) {
        return NULL;
    }

    return ax_tree_iter_leaf_values(tree);
}

static PyObject *
ax_tree_iter_leave_items(PyObject *tree)
{
    char warning[] = "iter_leave_items is deprecated, use iter_leaf_items instead. " \
                     "The iter_leave_items method will be removed 2014-05-15";
    if (PyErr_WarnEx(PyExc_DeprecationWarning, warning, 1) == -1) {
        return NULL;
    }

    return ax_tree_iter_leaf_items(tree);
}

static PyObject *
ax_tree_get(register PyObject *tree, PyObject *args)
{
    PyObject *key;
    PyObject *failobj = Py_None;

    if (!PyArg_UnpackTuple(args, "get", 1, 2, &key, &failobj)) {
        return NULL;
    }

    PyObject *val = ax_tree_subscript(tree, key);

    if ((val == NULL) && PyErr_ExceptionMatches(PyExc_KeyError)) {
        PyErr_Clear();
        Py_INCREF(failobj);
        return failobj;
    }

    return val;
}

/* Here comes a lot of update/init stuff. */
static int
merge_by_dict(PyObject *tree, PyObject *to_merge)
{

    PyObject *key;
    PyObject *value;
    Py_ssize_t pos = 0;

    while (PyDict_Next(to_merge, &pos, &key, &value)) {
        if (PyObject_SetItem(tree, key, value) == -1) {
            return -1;
        }
    }
    return 0;
}

static int
merge_by_keys(PyObject *tree, PyObject *to_merge)
{
    PyObject *keys = PyMapping_Keys(to_merge);
    PyObject *iter;
    PyObject *key;
    PyObject *value;
    int status;

    if (keys == NULL) {
        return -1;
    }

    iter = PyObject_GetIter(keys);
    Py_DECREF(keys);
    if (iter == NULL) {
        return -1;
    }

    for (key = PyIter_Next(iter); key; key = PyIter_Next(iter)) {
        value = PyObject_GetItem(to_merge, key);
        if (value == NULL) {
            Py_DECREF(iter);
            Py_DECREF(key);
            return -1;
        }
        status = PyObject_SetItem(tree, key, value);
        Py_DECREF(key);
        Py_DECREF(value);
        if (status == -1) {
            Py_DECREF(iter);
            return -1;
        }
    }
    Py_DECREF(iter);
    if (PyErr_Occurred()) {
        return -1;
    }
    return 0;
}

static int
merge_by_seq(PyObject *tree, PyObject *to_merge)
{
    PyObject *it;
    PyObject *item;
    PyObject *fast;

    it = PyObject_GetIter(to_merge);
    if (it == NULL) {
        return -1;
    }

    while ((item = PyIter_Next(it))) {
        fast = PySequence_Fast(item, "Cannot convert to a sequence");
        Py_DECREF(item);

        if (fast == NULL) {
            Py_DECREF(it);
            return -1;
        }

        Py_ssize_t item_size = PySequence_Fast_GET_SIZE(fast);

        if (item_size != 2) {
            PyErr_SetString(PyExc_ValueError, "Sequence item needs size 2");
            Py_DECREF(it);
            Py_DECREF(fast);
            return -1;
        }

        PyObject *key = PySequence_Fast_GET_ITEM(fast, 0);
        PyObject *value = PySequence_Fast_GET_ITEM(fast, 1);

        if (PyObject_SetItem(tree, key, value) == -1) {
            Py_DECREF(it);
            Py_DECREF(fast);
            return -1;
        }

        Py_DECREF(fast);
    }

    Py_DECREF(it);

    return PyErr_Occurred() ? -1 : 0;
}

static int
update_common(PyObject *tree, PyObject *args, PyObject *kwargs, char *methname)
{
    PyObject *arg = NULL;

    if (!PyArg_UnpackTuple(args, methname, 0, 1, &arg)) {
        return -1;
    }

    if ((arg != NULL) && (arg != Py_None)) {
        if (PyDict_Check(arg)) {
            if (merge_by_dict(tree, arg) == -1) {
                return -1;
            }
        }
        else if (PyObject_HasAttrString(arg, "keys")) {
            if (merge_by_keys(tree, arg) == -1) {
                return -1;
            }
        }
        else {
            if (merge_by_seq(tree, arg) == -1) {
                return -1;
            }
        }
    }

    if (kwargs != NULL) {
        if (PyDict_Check(kwargs)) {
            if (merge_by_dict(tree, kwargs) == -1) {
                return -1;
            }
        }
        else {
            return merge_by_keys(tree, kwargs);
        }
    }
    return 0;
}

static int
ax_tree_init(PyObject *self, PyObject *args, PyObject *kwargs)
{
    return update_common(self, args, kwargs, "init");
}

static PyObject *
ax_tree_update(PyObject *self, PyObject *args, PyObject *kwargs)
{
    if (update_common(self, args, kwargs, "update") == -1) {
        return NULL;
    }
    Py_RETURN_NONE;
}

static PyObject *
ax_tree_contains(PyObject *tree, PyObject *key)
{

    int ret_val = ax_tree_sq_contains(tree, key);

    if (ret_val == 1) {
        Py_RETURN_TRUE;
    }

    if (ret_val == 0) {
        Py_RETURN_FALSE;
    }

    return NULL;
}


static PyMethodDef ax_tree_methods[] = {
    {"iter_leave_keys", (PyCFunction)ax_tree_iter_leave_keys, METH_NOARGS, ""},
    {"iter_leave_values", (PyCFunction)ax_tree_iter_leave_values, METH_NOARGS, ""},
    {"iter_leave_items", (PyCFunction)ax_tree_iter_leave_items, METH_NOARGS, ""},
    {"iter_leaf_keys", (PyCFunction)ax_tree_iter_leaf_keys, METH_NOARGS, ""},
    {"iter_leaf_values", (PyCFunction)ax_tree_iter_leaf_values, METH_NOARGS, ""},
    {"iter_leaf_items", (PyCFunction)ax_tree_iter_leaf_items, METH_NOARGS, ""},
    {"get", (PyCFunction)ax_tree_get, METH_VARARGS, ""},
    {"update", (PyCFunction)ax_tree_update, METH_VARARGS | METH_KEYWORDS, ""},
    {"__contains__", (PyCFunction)ax_tree_contains, METH_O | METH_COEXIST, ""},

    {NULL, NULL, 0, NULL}
};


static PyTypeObject AXTreeType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_ax_tree._AXTree",      /* tp_name */
    sizeof(AXTree),          /* tp_basicsize */
    0,                       /* tp_itemsize */
    0,                       /* tp_dealloc */
    0,                       /* tp_print */
    0,                       /* tp_getattr */
    0,                       /* tp_setattr */
    0,                       /* tp_compare */
    0,                       /* tp_repr */
    0,                       /* tp_as_number */
    &AXTree_as_sequence,     /* tp_as_sequence */
    &AXTree_as_mapping,      /* tp_as_mapping */
    0,                       /* tp_hash */
    0,                       /* tp_call */
    0,                       /* tp_str */
    0,                       /* tp_getattro */
    0,                       /* tp_setattro */
    0,                       /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,   /* tp_flags */
    0,                       /* tp_doc */
    0,                       /* tp_traverse */
    0,                       /* tp_clear */
    0,                       /* tp_richcompare */
    0,                       /* tp_weaklistoffset */
    0,                       /* tp_iter */
    0,                       /* tp_iternext */
    ax_tree_methods,         /* tp_methods */
    0,                       /* tp_members */
    0,                       /* tp_getset */
    0,                       /* tp_base */
    0,                       /* tp_dict */
    0,                       /* tp_descr_get */
    0,                       /* tp_descr_set */
    0,                       /* tp_dictoffset */
    ax_tree_init,            /* tp_init */
    0,                       /* tp_alloc */
    0,                       /* tp_new */
};

typedef struct {
    PyObject_HEAD;
    item_stack_t *nodes;
    unsigned int type;
    PyTypeObject *tree_type;
    char *tmp_name;
    unsigned int tmp_name_len;
} ax_tree_iterator;

static PyObject*
build_node_name(ax_tree_iterator *ti, PyObject *parent, PyObject *key)
{
    Py_ssize_t parent_len;
    Py_ssize_t key_len;

    const char *p = PyStr_AsStringAndSize(parent, &parent_len);
    const char *k = PyStr_AsStringAndSize(key, &key_len);

    if ((p == NULL) || (k == NULL)) {
        return NULL;
    }

    const Py_ssize_t total = parent_len + 1 + key_len;

    if (total > ti->tmp_name_len) {
        ti->tmp_name = realloc(ti->tmp_name, total);
        ti->tmp_name_len = total;
    }

    memcpy(ti->tmp_name, p, parent_len);
    ti->tmp_name[parent_len] = '.';
    memcpy(ti->tmp_name + (parent_len +1), k, key_len);

    return PyStr_FromStringAndSize(ti->tmp_name, total);
}

static int
add_nodes(PyObject * parent, ax_tree_iterator *ti, PyObject *tree)
{
    PyObject *key, *value;
    Py_ssize_t pos = 0;

    while (PyDict_Next(tree, &pos, &key, &value)) {
        if (parent == NULL) {
            Py_INCREF(key);
        }
        else {
            key = build_node_name(ti, parent, key);
        }
        Py_INCREF(value);
        item_stack_push(ti->nodes, key, value);
    }
    return 0;

}

static PyObject *
ax_tree_iter_new(PyObject *tree, unsigned int type)
{
    ax_tree_iterator * ti;
    ti = PyObject_GC_New(ax_tree_iterator, &AXTreeIteratorType);
    if(ti == NULL) {
        return NULL;
    }

    ti->nodes = item_stack_create();
    ti->type = type;
    ti->tree_type = tree->ob_type;
    ti->tmp_name = malloc(32);
    ti->tmp_name_len = 32;

    add_nodes(NULL, ti, tree);

    PyObject_GC_Track(ti);
    return (PyObject*) ti;
}

static int
ax_tree_iter_clear(ax_tree_iterator *ti)
{
    entry_t t;
    int pos=0;
    while (item_stack_iter(&pos, ti->nodes, &t)) {
        Py_CLEAR(t.key);
        Py_CLEAR(t.value);
    }
    return 0;
}

static void
ax_tree_iter_dealloc(ax_tree_iterator *ti)
{
    ax_tree_iter_clear(ti);
    item_stack_free(ti->nodes);
    free(ti->tmp_name);
    PyObject_GC_Del(ti);
}

static int
ax_tree_iter_traverse(ax_tree_iterator *ti, visitproc visit, void *arg)
{
    entry_t t;
    int pos=0;
    while (item_stack_iter(&pos, ti->nodes, &t)) {
        /* t.key is always string => NO cycles possbile */
        Py_VISIT(t.value);
    }
    return 0;
}

static PyObject*
ax_tree_iter_next(ax_tree_iterator *ti)
{
    entry_t t;
    PyObject *ret;
    while (ti->nodes->next) {
        t = *item_stack_pop(ti->nodes);
        if (PyObject_TypeCheck(t.value, ti->tree_type)) {
            /* If t.value is empty it falls through and
             * is handled as an ordianary leaf/value.
             *
             * As soon as it has values t.value is not a leaf.
             * => Just add the nodes to the stack.
             */
            if (PyDict_Size(t.value)) {
                add_nodes(t.key, ti, t.value);
                /* Decref the refcount AFTER using the objects,
                 * otherwise they get freed before using.
                 */
                Py_DECREF(t.key);
                Py_DECREF(t.value);
                continue;
            }
        }

        switch (ti->type) {
            /* We dont need to incremnt the reference count here.
             * Becase while adding it to the stack we increment it
             */
            case LEAF_KEYS:
                Py_DECREF(t.value);
                return t.key;
            case LEAF_VALUES:
                Py_DECREF(t.key);
                return t.value;
            case LEAF_ITEMS:
                ret = PyTuple_Pack(2, t.key, t.value);
                Py_DECREF(t.key);
                Py_DECREF(t.value);
                return ret;
        }
    }
    /* this is stop iteration */
    return NULL;
}

PyTypeObject AXTreeIteratorType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "AXTreeIterator",             /*tp_name*/
    sizeof(ax_tree_iterator),     /*tp_basicsize*/
    0,                            /*tp_itemsize*/
    (destructor)ax_tree_iter_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC, /*tp_flags*/
    "Iterator over leafes",                                        /* tp_doc */
    (traverseproc)ax_tree_iter_traverse,                           /* tp_traverse */
    (inquiry)ax_tree_iter_clear,                                   /* tp_clear */
    0,                                                             /* tp_richcompare */
    0,                                                             /* tp_weaklistoffset */
    PyObject_SelfIter,                                             /* tp_iter */
    (iternextfunc)ax_tree_iter_next,                               /* tp_iternext */
    0,             /* tp_methods */
    0,             /* tp_members */
    0,             /* tp_getset */
    0,             /* tp_base */
    0,             /* tp_dict */
    0,             /* tp_descr_get */
    0,             /* tp_descr_set */
    0,             /* tp_dictoffset */
    0,             /* tp_init */
    0,             /* tp_alloc */
    0,             /* tp_new */
};

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,  /* m_base */
    "_ax_tree",             /* m_name */
    "AXTree module",        /* m_doc */
    -1,                     /* m_size */
    NULL,                   /* m_methods */
};


MODULE_INIT_FUNC(_ax_tree)
{
    AXTreeType.tp_base = &PyDict_Type;
    if (PyType_Ready(&AXTreeType) < 0) {
        return NULL;
    }

    PyObject *m = PyModule_Create(&moduledef);
    if (m == NULL) {
        return NULL;
    }

    Py_INCREF(&AXTreeType);
    PyModule_AddObject(m, "_AXTree", (PyObject*) &AXTreeType);

    if (PyType_Ready(&AXTreeIteratorType) < 0) {
        return NULL;
    }

    return m;
}
