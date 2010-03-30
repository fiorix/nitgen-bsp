#include <string.h>
#include <Python.h>
#include <NBioAPI.h>

struct capture_data {
    int image_width;
    int image_height;
    int buffer_size;
    unsigned char *buffer;
};

static PyObject *bsp_open(PyObject *self, PyObject *args)
{
    NBioAPI_RETURN err;
    NBioAPI_HANDLE m_hBSP;
    NBioAPI_VERSION m_Version;
    NBioAPI_UINT32 dev_cnt;
    NBioAPI_DEVICE_ID *dev_list;
    NBioAPI_DEVICE_INFO_0 m_DeviceInfo0;

    err = NBioAPI_Init(&m_hBSP);
    if(err != NBioAPIERROR_NONE)
        return PyErr_Format(PyExc_RuntimeError, "cannot initialize NBioAPI");

    NBioAPI_GetVersion(m_hBSP, &m_Version);
    err = NBioAPI_EnumerateDevice(m_hBSP, &dev_cnt, &dev_list);
    if(dev_cnt == 0)
        return PyErr_Format(PyExc_RuntimeError, "device not found");

    err = NBioAPI_OpenDevice(m_hBSP, NBioAPI_DEVICE_ID_AUTO);
    if(err != NBioAPIERROR_NONE)
        return PyErr_Format(PyExc_RuntimeError, "cannot open device");

    memset(&m_DeviceInfo0, 0, sizeof(NBioAPI_DEVICE_INFO_0));
    NBioAPI_GetDeviceInfo(m_hBSP, NBioAPI_DEVICE_ID_AUTO, 0, &m_DeviceInfo0);

    return Py_BuildValue("(iii)", m_hBSP,
        m_DeviceInfo0.ImageWidth, m_DeviceInfo0.ImageHeight);
}

static PyObject *bsp_close(PyObject *self, PyObject *args)
{
    NBioAPI_HANDLE m_hBSP;
    if(!PyArg_ParseTuple(args, "i", &m_hBSP))
        return PyErr_Format(PyExc_TypeError, "invalid bsp handler");

    NBioAPI_CloseDevice(m_hBSP, NBioAPI_DEVICE_ID_AUTO);
    Py_INCREF(Py_None);
    return Py_None;
}

NBioAPI_RETURN MyCaptureCallback(NBioAPI_WINDOW_CALLBACK_PARAM_PTR_0 pCallbackParam, NBioAPI_VOID_PTR pUserParam)
{
    struct capture_data *data = (struct capture_data *) pUserParam;
    memcpy(data->buffer, pCallbackParam->lpImageBuf, data->buffer_size);
    return NBioAPIERROR_NONE;
}

static PyObject *bsp_capture(PyObject *self, PyObject *args)
{
    NBioAPI_RETURN err;
    NBioAPI_HANDLE m_hBSP;
    NBioAPI_FIR_HANDLE capFIR;
    NBioAPI_WINDOW_OPTION winOption;
    struct capture_data data;

    memset(&data, 0, sizeof(data));
    if(!PyArg_ParseTuple(args, "iii", &m_hBSP, &data.image_width, &data.image_height))
        return PyErr_Format(PyExc_TypeError, "invalid arguments");

    data.buffer_size = data.image_width * data.image_height;
    data.buffer = PyMem_Malloc(data.buffer_size);

    memset(&winOption, 0, sizeof(NBioAPI_WINDOW_OPTION));
    winOption.Length = sizeof(NBioAPI_WINDOW_OPTION);
    winOption.CaptureCallBackInfo.CallBackType = 0;
    winOption.CaptureCallBackInfo.CallBackFunction = MyCaptureCallback;
    winOption.CaptureCallBackInfo.UserCallBackParam = &data;

    capFIR = NBioAPI_INVALID_HANDLE;
    err = NBioAPI_Capture(m_hBSP, NBioAPI_FIR_PURPOSE_VERIFY, &capFIR, -1, NULL, &winOption);
    if(err != NBioAPIERROR_NONE)
        return PyErr_Format(PyExc_RuntimeError, "cannot capture fingerprint");

    return Py_BuildValue("(s#i)", data.buffer, data.buffer_size, capFIR);
}

static PyObject *bsp_verify(PyObject *self, PyObject *args)
{
    NBioAPI_RETURN err;
    NBioAPI_HANDLE m_hBSP;
    NBioAPI_INPUT_FIR cap1, cap2;
    NBioAPI_BOOL bResult = NBioAPI_FALSE;
    NBioAPI_FIR_HANDLE fir1_handle, fir2_handle;
    NBioAPI_FIR_TEXTENCODE fir1_text, fir2_text;
    PyObject *rawF1, *rawF2;

    if(!PyArg_ParseTuple(args, "iOO", &m_hBSP, &rawF1, &rawF2))
        return PyErr_Format(PyExc_TypeError, "invalid arguments");

    /* determine format of FIR 1: handler or text */
    if(PyInt_Check(rawF1)) {
        PyArg_Parse(rawF1, "i", &fir1_handle);
        cap1.Form = NBioAPI_FIR_FORM_HANDLE;
        cap1.InputFIR.FIRinBSP = &fir1_handle;
    } else if(PyString_Check(rawF1)) {
        char *text_stream;
        PyArg_Parse(rawF1, "s", &text_stream);
        fir1_text.IsWideChar = NBioAPI_FALSE;
        fir1_text.TextFIR = text_stream;
        cap1.Form = NBioAPI_FIR_FORM_TEXTENCODE;
        cap1.InputFIR.TextFIR = &fir1_text;
    } else
        return PyErr_Format(PyExc_TypeError, "unknown format of cap1");

    /* determine format of FIR 2: handler or text */
    if(PyInt_Check(rawF2)) {
        PyArg_Parse(rawF2, "i", &fir2_handle);
        cap2.Form = NBioAPI_FIR_FORM_HANDLE;
        cap2.InputFIR.FIRinBSP = &fir2_handle;
    } else if(PyString_Check(rawF2)) {
        char *text_stream;
        PyArg_Parse(rawF2, "s", &text_stream);
        fir2_text.IsWideChar = NBioAPI_FALSE;
        fir2_text.TextFIR = text_stream;
        cap2.Form = NBioAPI_FIR_FORM_TEXTENCODE;
        cap2.InputFIR.TextFIR = &fir2_text;
    } else
        return PyErr_Format(PyExc_TypeError, "unknown format of cap2");

    /* warning: cannot verify text VS handle and vice-versa */
    err = NBioAPI_VerifyMatch(m_hBSP, &cap1, &cap2, &bResult, NULL);
    if(err != NBioAPIERROR_NONE)
        return PyErr_Format(PyExc_RuntimeError, "cannot verify");
    return Py_BuildValue("i", bResult);
}

static PyObject *bsp_free_fir(PyObject *self, PyObject *args)
{
    NBioAPI_HANDLE m_hBSP;
    NBioAPI_FIR_HANDLE fir;

    if(!PyArg_ParseTuple(args, "ii", &m_hBSP, &fir))
        return PyErr_Format(PyExc_TypeError, "invalid arguments");

    NBioAPI_FreeFIRHandle(m_hBSP, fir);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *bsp_text_fir(PyObject *self, PyObject *args)
{
    NBioAPI_RETURN err;
    NBioAPI_HANDLE m_hBSP;
    NBioAPI_FIR_HANDLE fir;
    NBioAPI_FIR_TEXTENCODE TextFIR;

    if(!PyArg_ParseTuple(args, "ii", &m_hBSP, &fir))
        return PyErr_Format(PyExc_TypeError, "invalid arguments");

    err = NBioAPI_GetTextFIRFromHandle(m_hBSP, fir, &TextFIR, NBioAPI_FALSE);
    if(err != NBioAPIERROR_NONE)
        return PyErr_Format(PyExc_RuntimeError, "cannot retrieve text-encoded FIR");

    return Py_BuildValue("s", TextFIR.TextFIR);
}

static PyMethodDef BspMethods[] = {
    {"open", bsp_open, 0, "open bsp device"},
    {"close", bsp_close, METH_VARARGS, "close bsp device"},
    {"capture", bsp_capture, METH_VARARGS, "capture fingerprint"},
    {"verify", bsp_verify, METH_VARARGS, "verify fingerprints"},
    {"free_fir", bsp_free_fir, METH_VARARGS, "release FIR memory"},
    {"text_fir", bsp_text_fir, METH_VARARGS, "return text-encoded FIR"},
    {NULL, NULL, 0, NULL},
};

PyMODINIT_FUNC init_bsp_module(void)
{
    PyObject *m;

    m = Py_InitModule("_bsp_module", BspMethods);
    if(m == NULL)
        return;
}
