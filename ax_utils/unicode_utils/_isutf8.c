#include "Python.h"
#include "compat.h"

/*
 * Portions Copyright 2001 Unicode, Inc.
 *
 * Disclaimer
 *
 * This source code is provided as is by Unicode, Inc. No claims are
 * made as to fitness for any particular purpose. No warranties of any
 * kind are expressed or implied. The recipient agrees to determine
 * applicability of information provided. If this file has been
 * purchased on magnetic or optical media from Unicode, Inc., the
 * sole remedy for any claim will be exchange of defective media
 * within 90 days of receipt.
 *
 * Limitations on Rights to Redistribute This Code
 *
 * Unicode, Inc. hereby grants the right to freely use the information
 * supplied in this file in the creation of products supporting the
 * Unicode Standard, and to make copies of this file in any form
 * for internal or external distribution as long as this notice
 * remains attached.
 */

/*
 * Index into the table below with the first byte of a UTF-8 sequence to
 * get the number of trailing bytes that are supposed to follow it.
 */
static const char trailingBytesForUTF8[256] = {
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
    2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2, 3,3,3,3,3,3,3,3,4,4,4,4,5,5,5,5
};

/* --------------------------------------------------------------------- */

/*
 * Utility routine to tell whether a sequence of bytes is legal UTF-8.
 * This must be called with the length pre-determined by the first byte.
 * The length can be set by:
 *  length = trailingBytesForUTF8[*source]+1;
 * and the sequence is illegal right away if there aren't that many bytes
 * available.
 * If presented with a length > 4, this returns 0.  The Unicode
 * definition of UTF-8 goes up to 4-byte sequences.
 */
static unsigned char
isLegalUTF8(const unsigned char* source, int length) {
    unsigned char a;
    const unsigned char* srcptr = source + length;
    switch (length) {
    default: return 0;
        /* Everything else falls through when "true"... */
    case 4: if ((a = (*--srcptr)) < 0x80 || a > 0xBF) return 0;
    case 3: if ((a = (*--srcptr)) < 0x80 || a > 0xBF) return 0;
    case 2: if ((a = (*--srcptr)) > 0xBF) return 0;
        switch (*source) {
            /* no fall-through in this inner switch */
            case 0xE0: if (a < 0xA0) return 0; break;
            case 0xF0: if (a < 0x90) return 0; break;
            case 0xF4: if ((a > 0x8F) || (a < 0x80)) return 0; break;
            default:  if (a < 0x80) return 0;
        }
        case 1: if (*source >= 0x80 && *source < 0xC2) return 0;
        if (*source > 0xF4) return 0;
    }
    return 1;
}

static unsigned char
is_valid(const unsigned char* string, const Py_ssize_t length) {
    Py_ssize_t position = 0;

    while (position < length) {
        const int sequence_length = trailingBytesForUTF8[*(string + position)] + 1;
        if ((position + sequence_length) > length) {
            return 0;
        }

        if (!isLegalUTF8(string + position, sequence_length)) {
            return 0;
        }

        position += sequence_length;
    }

    return 1;
}


static PyObject*
is_utf8(PyObject *self, PyObject *ob)
{
    /* When it is a unicode object this method makes no much sense.
     * Since the unicode object does not care about encododings.
     * It just holds the 'code points'. So it is safe to say 'True' :)
     */

    if (PyUnicode_Check(ob) == 1) {
           Py_RETURN_TRUE;
    }

    const char *data = PyBytes_AsString(ob);
    if (data == NULL) {
        return NULL;
    }

    /* We already did the check for valid string above
     * => safe to use the non-checking macro.
     */
    const Py_ssize_t size = PyBytes_GET_SIZE(ob);

    if (is_valid((unsigned char*) data, size)) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}


static PyMethodDef isutf8_methods[] = {
    {"is_utf8", is_utf8, METH_O, "Docu"},
    {NULL, NULL, 0, NULL}

};

static struct PyModuleDef moduledef =  {
    PyModuleDef_HEAD_INIT,          /* m_base */
    "_isutf8",                      /* m_name */
    "",                             /* m_doc */
    0,                              /* m_size */
    isutf8_methods,                 /* m_methods */
};


MODULE_INIT_FUNC(_isutf8)
{
    return PyModule_Create(&moduledef);
}
