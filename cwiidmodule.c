//Justin Tulloss
//
//Interface from Python to libcwiid
//

//Standard Includes
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <limits.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <pthread.h>

#include "Python.h"
#include "cwiid.h"
#include "cwiidmodule.h"

static PyObject* pyMesgCallback;
static bdaddr_t btAddr;
static int id;
//static pthread_t wiiThread;


//static void delwii(void* mote);
void callbackBridge(int id,int mesg_count, union cwiid_mesg* mesg[]);
void wiiStart(PyObject* self);

//Associates cwiid functions with python ones
static PyMethodDef modMethods[] = 
{
    {NULL, NULL}
};

static PyMethodDef cwiidMethods[] =
{

    {"__init__", constructorwii, METH_VARARGS, "cwiid(function)"},
    {"read", readwii, METH_VARARGS, "read from wiimote"},
    {"write", writewii, METH_VARARGS, "write to wiimote"},
    {"command", commandwii, METH_VARARGS, "send wiimote command"},
    {"disconnect", disconnectwii, METH_VARARGS, "disconnect wiimote"},
    {NULL, NULL}
};


void 
initcwiidmodule(void)
{
    PyMethodDef *def;
    PyObject* moduleDict;
    PyObject* classDict;
    PyObject* className;
    PyObject* cwiidClass;
    PyObject* m = Py_InitModule3("cwiidmodule", modMethods, 
        "Module for accessing the wiimote");

    id = 0;

    //Open the cwiid library
    dlopen("./libcwiid.so", RTLD_LAZY);

    //Construct our class
    moduleDict = PyModule_GetDict(m);
    classDict = PyDict_New();
    className = PyString_FromString("cwiidmodule");

    cwiidClass = PyClass_New(NULL, classDict, className);
    PyDict_SetItem(moduleDict, className, cwiidClass);
    Py_XDECREF(className);
    
    //add functions to class
    for (def = cwiidMethods; def->ml_name != NULL; def++)
    {
        PyObject *func = PyCFunction_New(def, NULL);
        PyObject *method = PyMethod_New(func, NULL, cwiidClass);
        PyDict_SetItemString(classDict, def->ml_name, method);
        Py_XDECREF(func);
        Py_XDECREF(method);
    }
}

PyObject* 
constructorwii(PyObject* self, PyObject* args)
{
    PyObject* temp;
    PyObject* myself;
    //Get out parameters
    if (PyArg_UnpackTuple(args, "constructor", 1, 2, &myself, &temp))
    {
        if (!PyCallable_Check(temp))
        {
            PyErr_SetString(PyExc_TypeError, "Parameter must be callable");
            return NULL;
        }
        Py_XINCREF(temp);
        Py_XDECREF(pyMesgCallback);

        pyMesgCallback = temp;
    }

    PyEval_InitThreads();
    //if(pthread_create(&wiiThread, NULL, (void*)wiiStart, myself))
    //    PyErr_SetString(PyExc_RuntimeError, "Could not create wii thread");
    wiiStart(myself);
    
    Py_INCREF(Py_None);
    return Py_None;
}

void 
wiiStart(PyObject* self)
{
    PyGILState_STATE gstate;
    PyObject* pyMote;
    cwiid_wiimote_t* theMote;
    btAddr = *BDADDR_ANY;
    //Set up wiimote (in a new thread)
    gstate = PyGILState_Ensure();
    if(!(theMote = cwiid_connect(&btAddr, callbackBridge, &id)))
    {
        PyErr_SetString(PyExc_RuntimeError, "Could not connect to wiimote");
        return;
    }
    //Create a python c object from the wiimote* and store it in the
    //cwiid python class
    pyMote=PyCObject_FromVoidPtr((void*) theMote, (void*) cwiid_disconnect);
    if(-1==PyObject_SetAttrString(self, "wiimote", pyMote))
    PyGILState_Release(gstate);
}


PyObject* 
readwii(PyObject* self, PyObject* args)
{
    /*
    PyObject* myself;
    PyObject* offset;
    PyObject* flags;
    PyObject* len;
    PyObject* pData;*/
    PyGILState_STATE gstate;
    
    gstate = PyGILState_Ensure();
    PyErr_SetString(PyExc_RuntimeError, "This has not yet been implemented");
    PyGILState_Release(gstate);

    return self;
}

PyObject* 
writewii(PyObject* self, PyObject* args)
{
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    PyErr_SetString(PyExc_RuntimeError, "This has not yet been implemented");
    PyGILState_Release(gstate);
    return Py_None;
}

PyObject* 
commandwii(PyObject* self, PyObject* args)
{
    //Python types
    PyObject* pyself;
    PyObject* pycommand;
    PyObject* pyflags;
    PyObject* pyMote;
    //C types
    enum cwiid_command command;
    uint8_t flags;
    cwiid_wiimote_t* theMote;

    PyGILState_STATE gstate;

    gstate = PyGILState_Ensure();
    PyArg_UnpackTuple(args, "command", 3, 3, &pyself, &pycommand, &pyflags);
    if(!(PyInt_Check(pycommand) && PyInt_Check(pyflags)))
    {
        PyErr_SetString(PyExc_TypeError, "command and flags must be ints");
    }

    //marshal everything over
    command = (enum cwiid_command) PyInt_AsLong(pycommand);
    flags = (uint8_t) PyInt_AsLong(pyflags);
    pyMote = PyObject_GetAttrString(pyself, "wiimote");
    theMote = (cwiid_wiimote_t*) PyCObject_AsVoidPtr(pyMote);

    //finally, send the command to the wiimote
    cwiid_command(theMote, command, flags);
    PyGILState_Release(gstate);

    Py_XINCREF(Py_None);
    return Py_None;
}

PyObject* 
disconnectwii(PyObject* self, PyObject* args)
{
    return self;
}

void 
callbackBridge(int id, int mesg_count, union cwiid_mesg* mesg[])
{
    PyObject* mesglist; //List of message tuples
    PyObject* amesg; //A single message (type, [arguments])
    PyObject* mesgVal; //Dictionary of arguments for a message
    PyGILState_STATE gstate;

    int i;

    gstate = PyGILState_Ensure(); //Let's lock this baby down
    mesglist = PyList_New(0);
    Py_XINCREF(mesglist);
    for (i = 0; i < mesg_count; i++)
    {

        mesgVal = PyDict_New();
        Py_XINCREF(mesgVal);
        switch (mesg[i]->type) {
            case CWIID_MESG_STATUS:
                PyDict_SetItemString(mesgVal, "battery",
                    Py_BuildValue("B", mesg[i]->status_mesg.battery));
                switch (mesg[i]->status_mesg.extension)
                {
                    case CWIID_EXT_NONE:
                        PyDict_SetItemString(mesgVal, "extension",
                            Py_BuildValue("s","none"));
                        break;
                    case CWIID_EXT_NUNCHUK:
                        PyDict_SetItemString(mesgVal, "extension", 
                            Py_BuildValue("s","nunchuck"));
                        break;
                    case CWIID_EXT_CLASSIC:
                        PyDict_SetItemString(mesgVal, "extension", 
                            Py_BuildValue("s","classic"));
                        break;
                    default:
                        break;
                }
                break;
            case CWIID_MESG_BTN:
                PyDict_SetItemString(mesgVal, "buttons", 
                    Py_BuildValue("H", mesg[i]->btn_mesg.buttons));
                break;
            case CWIID_MESG_ACC:
                PyDict_SetItemString(mesgVal, "x", 
                    Py_BuildValue("B", mesg[i]->acc_mesg.x));
                PyDict_SetItemString(mesgVal, "y", 
                    Py_BuildValue("B", mesg[i]->acc_mesg.y));
                PyDict_SetItemString(mesgVal, "z", 
                    Py_BuildValue("B", mesg[i]->acc_mesg.z));
                break;
            case CWIID_MESG_IR:
                break;
            case CWIID_MESG_NUNCHUK:
                break;
            case CWIID_MESG_CLASSIC:
                break;
            case CWIID_MESG_ERROR:
                switch(mesg[i]->error_mesg.error)
                {
                    case CWIID_ERROR_DISCONNECT:
                        PyDict_SetItemString(mesgVal, "error",
                            Py_BuildValue("s", 
                                "Wiimote was disconnected"));
                        break;
                    case CWIID_ERROR_COMM:
                        PyDict_SetItemString(mesgVal, "error",
                            Py_BuildValue("s", 
                                "Communication error occurred"));
                        break;
                    default:
                        PyDict_SetItemString(mesgVal, "error",
                            Py_BuildValue("s","An Unknown error occurred"));
                        break;
                }
                break;
            default:
                PyDict_SetItemString(mesgVal, "error",
                    Py_BuildValue("s","Unknown message arrived"));
                break;
        }

        //Finally Put the type next to the message in a tuple and
        //append them to the list of messages
        amesg = Py_BuildValue("(iO)", mesg[i]->type, mesgVal);
        Py_XINCREF(amesg);
        PyList_Append(mesglist, amesg);
    }
    
    //Put id and the list of messages as the arguments to the callback
    PyObject_CallFunction(pyMesgCallback,"(iO)",id,mesglist);
    PyGILState_Release(gstate);
}



