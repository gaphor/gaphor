/* include this first, before NO_IMPORT_PYGOBJECT is defined */
#include <pygobject.h>
#include <pygtk/pygtk.h>

void pytreemodel_register_classes (PyObject *d);

extern PyMethodDef pytreemodel_functions[];


DL_EXPORT(void)
inittreemodel (void)
{
	PyObject *m, *d;

	init_pygobject ();
	init_pygtk ();

	m = Py_InitModule ("treemodel", pytreemodel_functions);
	d = PyModule_GetDict (m);

	pytreemodel_register_classes (d);

	if (PyErr_Occurred ())
		Py_FatalError ("can't initialise module treemodel");
}

