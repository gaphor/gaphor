#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

/* include this first, before NO_IMPORT_PYGOBJECT is defined */
#include <pygobject.h>
#include <pygtk/pygtk.h>

void pydiagramitems_register_classes (PyObject *d);

extern PyMethodDef pydiagramitems_functions[];

PyObject *UML_module = NULL;
PyObject *UML_factory = NULL;

DL_EXPORT(void)
initdiagramitems (void)
{
	PyObject *m, *d;
	PyObject *uml_d, *uml_type;

	init_pygobject ();
	init_pygtk ();

	m = Py_InitModule ("diagramitems", pydiagramitems_functions);
	d = PyModule_GetDict (m);

	pydiagramitems_register_classes (d);

	UML_module = PyImport_ImportModule("UML");
	if (UML_module == NULL || UML_module == Py_None)
		Py_FatalError ("could not import UML");

	/* uml_d = PyModule_GetDict(UML_module);
	g_assert (uml_d != NULL && uml_d != Py_None);
	uml_type = PyDict_GetItemString(uml_d, "ElementFactory");

	if (PyErr_Occurred ()) {
		PyErr_Print();
		Py_FatalError ("can't initialise module diagram");
	}

	g_assert (uml_type != NULL && uml_type != Py_None);

	UML_factory = PyObject_CallObject (uml_type, NULL); */

	if (PyErr_Occurred ())
		Py_FatalError ("can't initialise module diagram");
}

