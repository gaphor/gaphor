/* vim:sw=4
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

/* include this first, before NO_IMPORT_PYGOBJECT is defined */
#include <pygobject.h>
#include <pygtk/pygtk.h>

void pywrapbox_register_classes (PyObject *d);

extern PyMethodDef pywrapbox_functions[];

DL_EXPORT(void)
initwrapbox (void)
{
    PyObject *m, *d;
	
    init_pygobject ();
    init_pygtk ();

    m = Py_InitModule ("gaphor.misc.wrapbox", pywrapbox_functions);
    d = PyModule_GetDict (m);
	
    pywrapbox_register_classes (d);
}
