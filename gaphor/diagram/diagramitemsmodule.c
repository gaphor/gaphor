#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

/* include this first, before NO_IMPORT_PYGOBJECT is defined */
#include <pygobject.h>
#include <pygtk/pygtk.h>

void pydiagramitems_register_classes (PyObject *d);

extern PyMethodDef pydiagramitems_functions[];

PyObject *UML_module = NULL;

DL_EXPORT(void)
initdiagramitems (void)
{
	PyObject *m, *d;

	init_pygobject ();
	init_pygtk ();

	m = Py_InitModule ("diagramitems", pydiagramitems_functions);
	d = PyModule_GetDict (m);

	pydiagramitems_register_classes (d);

	UML_module = PyImport_ImportModule("UML");
	if (UML_module == NULL)
		Py_FatalError ("could not import UML");

	if (PyErr_Occurred ())
		Py_FatalError ("can't initialise module diagram");
}

