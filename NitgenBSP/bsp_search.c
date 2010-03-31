#include <string.h>
#include <Python.h>
#include <NBioAPI.h>
#include <NBioAPI_IndexSearch.h>

static PyObject *search_initialize(PyObject *self, PyObject *args)
{
    NBioAPI_RETURN err;
    NBioAPI_HANDLE m_hBSP;

    if(!PyArg_ParseTuple(args, "i", &m_hBSP))
        return PyErr_Format(PyExc_TypeError, "invalid bsp handler");

    err = NBioAPI_InitIndexSearchEngine(m_hBSP);
    if(err != NBioAPIERROR_NONE)
        return PyErr_Format(PyExc_RuntimeError, "cannot initialize search engine");

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *search_terminate(PyObject *self, PyObject *args)
{
    NBioAPI_RETURN err;
    NBioAPI_HANDLE m_hBSP;

    if(!PyArg_ParseTuple(args, "i", &m_hBSP))
        return PyErr_Format(PyExc_TypeError, "invalid bsp handler");

    err = NBioAPI_TerminateIndexSearchEngine(m_hBSP);
    if(err != NBioAPIERROR_NONE)
        return PyErr_Format(PyExc_RuntimeError, "cannot terminate search engine");

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *search_insert(PyObject *self, PyObject *args)
{
    PyObject *rawFIR;
    NBioAPI_RETURN err;
    NBioAPI_HANDLE m_hBSP;
    NBioAPI_UINT32 userID;
    NBioAPI_INPUT_FIR inputFIR;
    NBioAPI_FIR_HANDLE fir_handle;
    NBioAPI_FIR_TEXTENCODE fir_text;
    NBioAPI_INDEXSEARCH_SAMPLE_INFO sample;

    if(!PyArg_ParseTuple(args, "iiO", &m_hBSP, &userID, &rawFIR))
        return PyErr_Format(PyExc_TypeError, "invalid arguments");

    /* determine format of FIR: handler or text */
    if(PyInt_Check(rawFIR)) {
        PyArg_Parse(rawFIR, "i", &fir_handle);
        inputFIR.Form = NBioAPI_FIR_FORM_HANDLE;
        inputFIR.InputFIR.FIRinBSP = &fir_handle;
    } else if(PyString_Check(rawFIR)) {
        PyArg_Parse(rawFIR, "s", &fir_text.TextFIR);
        fir_text.IsWideChar = NBioAPI_FALSE;
        inputFIR.Form = NBioAPI_FIR_FORM_TEXTENCODE;
        inputFIR.InputFIR.TextFIR = &fir_text;
    } else
        return PyErr_Format(PyExc_TypeError, "unknown format of FIR");

    memset(&sample, 0, sizeof(sample));
    err = NBioAPI_AddFIRToIndexSearchDB(m_hBSP, &inputFIR, userID, &sample);
    if(err != NBioAPIERROR_NONE)
        return PyErr_Format(PyExc_RuntimeError, "cannot add FIR to search engine");

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *search_remove(PyObject *self, PyObject *args)
{
    NBioAPI_RETURN err;
    NBioAPI_HANDLE m_hBSP;
    NBioAPI_UINT32 userID;

    if(!PyArg_ParseTuple(args, "ii", &m_hBSP, &userID))
        return PyErr_Format(PyExc_TypeError, "invalid arguments");

    err = NBioAPI_RemoveUserFromIndexSearchDB(m_hBSP, userID);
    if(err != NBioAPIERROR_NONE)
        return PyErr_Format(PyExc_RuntimeError, "cannot remove FIR from search engine");

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *search_identify(PyObject *self, PyObject *args)
{
    int seclevel;
    PyObject *rawFIR;
    NBioAPI_RETURN err;
    NBioAPI_HANDLE m_hBSP;
    NBioAPI_INPUT_FIR inputFIR;
    NBioAPI_FIR_HANDLE fir_handle;
    NBioAPI_FIR_TEXTENCODE fir_text;
    NBioAPI_INDEXSEARCH_FP_INFO info;

    if(!PyArg_ParseTuple(args, "iOi", &m_hBSP, &rawFIR, &seclevel))
        return PyErr_Format(PyExc_TypeError, "invalid arguments");

    /* determine format of FIR: handler or text */
    if(PyInt_Check(rawFIR)) {
        PyArg_Parse(rawFIR, "i", &fir_handle);
        inputFIR.Form = NBioAPI_FIR_FORM_HANDLE;
        inputFIR.InputFIR.FIRinBSP = &fir_handle;
    } else if(PyString_Check(rawFIR)) {
        PyArg_Parse(rawFIR, "s", &fir_text.TextFIR);
        fir_text.IsWideChar = NBioAPI_FALSE;
        inputFIR.Form = NBioAPI_FIR_FORM_TEXTENCODE;
        inputFIR.InputFIR.TextFIR = &fir_text;
    } else
        return PyErr_Format(PyExc_TypeError, "unknown format of FIR");

    memset(&info, 0, sizeof(info));
    err = NBioAPI_IdentifyDataFromIndexSearchDB(m_hBSP, &inputFIR, seclevel, &info, NULL);
    if(err == NBioAPIERROR_INDEXSEARCH_IDENTIFY_FAIL) {
        Py_INCREF(Py_None);
        return Py_None;
    } else if(err != NBioAPIERROR_NONE)
        return PyErr_Format(PyExc_RuntimeError, "cannot perform identify within the search engine");

    return Py_BuildValue("i", info.ID);
}

static PyObject *search_save(PyObject *self, PyObject *args)
{
    NBioAPI_RETURN err;
    NBioAPI_HANDLE m_hBSP;
    NBioAPI_CHAR *fullpath;

    if(!PyArg_ParseTuple(args, "is", &m_hBSP, &fullpath))
        return PyErr_Format(PyExc_TypeError, "invalid arguments");

    err = NBioAPI_SaveIndexSearchDBToFile(m_hBSP, fullpath);
    if(err != NBioAPIERROR_NONE)
        return PyErr_Format(PyExc_RuntimeError, "cannot save search engine DB to file");

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *search_load(PyObject *self, PyObject *args)
{
    NBioAPI_RETURN err;
    NBioAPI_HANDLE m_hBSP;
    NBioAPI_CHAR *fullpath;

    if(!PyArg_ParseTuple(args, "is", &m_hBSP, &fullpath))
        return PyErr_Format(PyExc_TypeError, "invalid arguments");

    err = NBioAPI_LoadIndexSearchDBFromFile(m_hBSP, fullpath);
    if(err != NBioAPIERROR_NONE)
        return PyErr_Format(PyExc_RuntimeError, "cannot load search engine DB from file");

    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef SearchMethods[] = {
    {"initialize", search_initialize, METH_VARARGS, "initialize search engine"},
    {"terminate", search_terminate, METH_VARARGS, "terminate search engine"},
    {"insert", search_insert, METH_VARARGS, "insert userID with FIR into the search engine"},
    {"remove", search_remove, METH_VARARGS, "remove userID from the search engine"},
    {"identify", search_identify, METH_VARARGS, "identify FIR using search engine"},
    {"save", search_save, METH_VARARGS, "save search engine db into file"},
    {"load", search_load, METH_VARARGS, "load search engine db from file"},
    {NULL, NULL, 0, NULL},
};

PyMODINIT_FUNC init_bsp_search(void)
{
    Py_InitModule("_bsp_search", SearchMethods);
}
