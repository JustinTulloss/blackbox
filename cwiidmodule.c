/*
 * Copyright (C) 2007 Justin M. Tulloss <jmtulloss@gmail.com>
 *
 * Interface from Python to libcwiid
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, 
 * Boston, MA  02110-1301  USA
 *
 * ChangeLog:
 * 2007-04-26 Justin M. Tulloss <jmtulloss@gmail.com>
 * * Updated for new libcwiid API
 *
 * 2007-04-24 Justin M. Tulloss <jmtulloss@gmail.com>
 * * Initial Changelog
 */


//Standard Includes
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <limits.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <pthread.h>

//Interesting includes
#include "Python.h"
#include "cwiid.h"
#include "structmember.h"

//Python Function declarations
void initcwiidmodule(void);
static int constructorwii(PyObject* self, PyObject* args);
PyObject* readwii(PyObject* self, PyObject* args);
PyObject* writewii(PyObject* self, PyObject* args);
PyObject* commandwii(PyObject* self, PyObject* args);
PyObject* disconnectwii(PyObject* self, PyObject* args);
PyObject* enablewii(PyObject* self, PyObject* args);
PyObject* disablewii(PyObject* self, PyObject* args);
PyObject* get_mesgwii(PyObject* self, PyObject* args);
PyObject* set_callbackwii(PyObject* self, PyObject* args);
PyObject* get_statewii(PyObject* self, PyObject* args);


//Types

typedef struct {
    PyObject_HEAD
    cwiid_wiimote_t* wiimote;
    PyObject* callback;
}cwiidmodule;

//Type private functions
static void cwiidmodule_dealloc(cwiidmodule* self);
static PyObject*
    cwiidmodule_new(PyTypeObject *type, PyObject *args, PyObject *kwds);

//Helper functions
void callbackBridge(cwiid_wiimote_t* wiimote,
    int mesg_count, union cwiid_mesg mesg[]);
static PyObject* processMesgs(int mesg_count, union cwiid_mesg mesg[]);
static int wiiStart(cwiidmodule* self, int flags);
static PyObject* notImplemented();

static bdaddr_t btAddr;


//Associates cwiid functions with python ones
static PyMethodDef modMethods[] = 
{
    {NULL, NULL}
};

//Our type methods
static PyMethodDef cwiidMethods[] =
{

    //{"__init__", constructorwii, METH_VARARGS, "cwiid(function)"},
    {"read", readwii, METH_VARARGS, "read from wiimote"},
    {"write", writewii, METH_VARARGS, "write to wiimote"},
    {"command", commandwii, METH_VARARGS, "send wiimote command"},
    {"enable", enablewii, METH_VARARGS, "enable flags on wiimote"},
    {"disable", disablewii, METH_VARARGS, "disable flags on wiimote"},
    {"get_mesg", get_mesgwii, METH_VARARGS, "blocking call to get messages"},
    {"set_callback", set_callbackwii, METH_VARARGS, "setup a mesg processing callback"},
    {"get_state", get_statewii, METH_VARARGS, "polling interface"},
    {"disconnect", disconnectwii, METH_VARARGS, "disconnect wiimote"},
    {NULL, NULL}
};

static PyMemberDef cwiidMembers[] = {
    {"_wiimote", T_OBJECT_EX, offsetof(cwiidmodule, wiimote), 0, "wiimote"},
    {"_callback", T_OBJECT_EX,offsetof(cwiidmodule, callback),0,"callback"},
    {NULL}
};


//Defines a new type in python
static PyTypeObject cwiidmoduleType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "cwiidmodule.cwiidmodule", /*tp_name*/
    sizeof(cwiidmodule),       /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)cwiidmodule_dealloc, /*tp_dealloc*/
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
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "cwiid c-python interface",/* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    cwiidMethods,              /* tp_methods */
    cwiidMembers,              /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)constructorwii,  /* tp_init */
    0,                         /* tp_alloc */
    cwiidmodule_new,                 /* tp_new */
};

//Allocate and deallocate functions
static void
cwiidmodule_dealloc(cwiidmodule* self)
{
    cwiid_disconnect(self->wiimote);
    Py_XDECREF(self->callback);
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject*
cwiidmodule_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    cwiidmodule* self;

    self = (cwiidmodule*) type->tp_alloc(type, 0);

    return (PyObject*) self;
}

PyMODINIT_FUNC
initcwiidmodule(void)
{
    PyObject* m;

    if (PyType_Ready(&cwiidmoduleType) <0 )
        return;

    //Open the cwiid library
    dlopen("libcwiid.so", RTLD_LAZY);
    if (!(m = Py_InitModule3("cwiidmodule", modMethods, 
      "Module for accessing the wiimote through cwiid")))
        return;

    Py_INCREF(&cwiidmoduleType);
    PyModule_AddObject(m, "cwiidmodule", (PyObject*)&cwiidmoduleType);

}

int
wiiStart(cwiidmodule* self, int flags)
{
    cwiid_wiimote_t* theMote;
    btAddr = *BDADDR_ANY;

    //Set up wiimote 
    if(!(theMote = cwiid_connect(&btAddr, flags)))
    {
        return -1;
    }
    cwiid_set_data(theMote,(void*)self); //keep pyobject with wiimote
    self->wiimote = theMote; //keep wiimote with pyobject
    self->callback = Py_None;
    return 0;
}

static int
constructorwii(PyObject* self, PyObject* args)
{
    PyObject* pyFlags;

    //Get out parameters
    if (PyArg_UnpackTuple(args, "constructor", 1, 1, &pyFlags))
    {
        if (!PyInt_Check(pyFlags))
        {
            PyErr_SetString(PyExc_TypeError, "Parameter must be int");
            return 0;
        }
    }

    if(wiiStart((cwiidmodule*)self, PyInt_AsLong(pyFlags))<0)
    {
        PyErr_SetString(PyExc_IOError, "Could not connect to wiimote");
    }
    PyEval_InitThreads();
    
    return 0;
}


PyObject* 
readwii(PyObject* self, PyObject* args)
{
    return notImplemented();
}

PyObject* 
writewii(PyObject* self, PyObject* args)
{
    return notImplemented();
}

PyObject* 
commandwii(PyObject* self, PyObject* args)
{
    //Python types
    PyObject* pycommand;
    PyObject* pyflags;

    //C types
    enum cwiid_command command;
    uint8_t flags;

    PyGILState_STATE gstate;

    gstate = PyGILState_Ensure();
    PyArg_UnpackTuple(args, "command", 2, 2, &pycommand, &pyflags);
    if(!(PyInt_Check(pycommand) && PyInt_Check(pyflags)))
    {
        PyErr_SetString(PyExc_TypeError, "command and flags must be ints");
    }

    //marshal everything over
    command = (enum cwiid_command) PyInt_AsLong(pycommand);
    flags = (uint8_t) PyInt_AsLong(pyflags);

    //finally, send the command to the wiimote
    cwiid_command(((cwiidmodule*)self)->wiimote, command, flags);
    PyGILState_Release(gstate);

    Py_RETURN_NONE;
}

PyObject* 
disconnectwii(PyObject* self, PyObject* args)
{
    return notImplemented();
}

PyObject* 
enablewii(PyObject* self, PyObject* args)
{
    return notImplemented();
}

PyObject* 
disablewii(PyObject* self, PyObject* args)
{
    return notImplemented();
}

PyObject* 
get_mesgwii(PyObject* self, PyObject* args)
{
    union cwiid_mesg** mesgs;
    int mesg_count;
    
    //get the messages from Mr. Wiimote
    cwiid_get_mesg(((cwiidmodule*)self)->wiimote, &mesg_count, mesgs);

    return processMesgs(mesg_count, *mesgs);
}

PyObject* 
set_callbackwii(PyObject* self, PyObject* args)
{
    PyObject* pyCallback;

    PyArg_UnpackTuple(args, "set_callback", 1, 1, &pyCallback);
    if (!PyCallable_Check(pyCallback))
    {
        PyErr_SetString(PyExc_TypeError, "callback must be callable!");
    }

    //Set this callback as an attribute in the class
    if (((cwiidmodule*)self)->callback== Py_None)//wasn't a callback before
    {
        cwiid_set_mesg_callback(((cwiidmodule*)self)->wiimote, 
            (cwiid_mesg_callback_t*) callbackBridge);
    }
    ((cwiidmodule*)self)->callback = pyCallback;

    Py_RETURN_NONE;
}

PyObject* 
get_statewii(PyObject* self, PyObject* args)
{
    return notImplemented();
}

static PyObject*
notImplemented()
{
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    PyErr_SetString(PyExc_NotImplementedError, "This has not yet been implemented");
    PyGILState_Release(gstate);
    
    Py_RETURN_NONE;
}

void 
callbackBridge(cwiid_wiimote_t* wiimote, 
    int mesg_count, union cwiid_mesg mesg[])
{
    PyObject* argTuple;
    PyObject* pyself;
    //PyObject* pyCallback;
    PyGILState_STATE gstate;
    
    gstate = PyGILState_Ensure();

    argTuple = processMesgs(mesg_count, mesg);

    //Put id and the list of messages as the arguments to the callback
    pyself = (PyObject*) cwiid_get_data(wiimote);
    if (PyMethod_Check(((cwiidmodule*)pyself)->callback))
    {
        //Sorry for the ugliness here.
        //After determining that the callback is a method in a class,
        //this line calls that function object with self and the argtuple
        //as arguments.
        PyObject_CallFunction(
            PyMethod_Function(((cwiidmodule*)pyself)->callback),"(OO)",
            PyMethod_Class(((cwiidmodule*)pyself)->callback), argTuple
            );
    }
    else
        PyObject_CallFunction(((cwiidmodule*)pyself)->callback, 
            "(O)",argTuple);

    Py_XDECREF(argTuple); //actually need to decref the entire structure
    PyGILState_Release(gstate);
}

/* This is the function responsible for marshaling the cwiid messages from
 * C to python. It's rather complicated since it uses a complex C union
 * to store the data and multiple enumerations to figure out what data is
 * actually being sent. Neither of these common C types really translate
 * well into Python. I've done my best to translate it to python as follows:
 *
 * Python callback takes arg (mesgs). The mesgs is a list of
 * mesg tuples which contain the mesg type and a dict of the arguments.
 * 
 * Ex:
 * mesgs =>[(CWIID_BTN_MESG,{"buttons":btnMask}), 
 *          (CWIID_ACC_MESG,{"x":xVal, "y":yVal, "z":zVal})]
 */
static PyObject* 
processMesgs(int mesg_count, union cwiid_mesg mesg[])
{
    PyObject* mesglist; //List of message tuples
    PyObject* amesg; //A single message (type, [arguments])
    PyObject* mesgVal; //Dictionary of arguments for a message

    int i;

    mesglist = PyList_New(0);
    Py_XINCREF(mesglist);
    for (i = 0; i < mesg_count; i++)
    {

        mesgVal = PyDict_New();
        Py_XINCREF(mesgVal);
        switch (mesg[i].type) {
            case CWIID_MESG_STATUS:
                PyDict_SetItemString(mesgVal, "battery",
                    Py_BuildValue("B", mesg[i].status_mesg.battery));
                switch (mesg[i].status_mesg.ext_type)
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
                    Py_BuildValue("H", mesg[i].btn_mesg.buttons));
                break;
            case CWIID_MESG_ACC:
                PyDict_SetItemString(mesgVal, "x", 
                    Py_BuildValue("B", mesg[i].acc_mesg.acc[0]));
                PyDict_SetItemString(mesgVal, "y", 
                    Py_BuildValue("B", mesg[i].acc_mesg.acc[1]));
                PyDict_SetItemString(mesgVal, "z", 
                    Py_BuildValue("B", mesg[i].acc_mesg.acc[2]));
                break;
            case CWIID_MESG_IR:
                break;
            case CWIID_MESG_NUNCHUK:
                break;
            case CWIID_MESG_CLASSIC:
                break;
            case CWIID_MESG_ERROR:
                switch(mesg[i].error_mesg.error)
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
        amesg = Py_BuildValue("(iO)", mesg[i].type, mesgVal);
        Py_XINCREF(amesg);
        PyList_Append(mesglist, amesg);
    }

    return mesglist;
}
