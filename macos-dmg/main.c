/*

Startup script used by py2app.

 */
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <pwd.h>
#include <dlfcn.h>
#include <mach-o/dyld.h>
#include <CoreFoundation/CoreFoundation.h>
#include <ApplicationServices/ApplicationServices.h>
#include <locale.h>
#include <sys/utsname.h>

/*
    Typedefs
*/

typedef int PyObject;
typedef PyObject* (*Py_BuildValuePtr)(const char*, ...);
#if 0
typedef void (*Py_SetPathPtr)(const wchar_t*);
#endif
typedef int (*PySys_SetObjectPtr)(const char*, PyObject*);
typedef void (*Py_SetProgramNamePtr)(const char *);
typedef void (*Py_InitializePtr)(void);
typedef int (*PyRun_SimpleFilePtr)(FILE *, const char *);
typedef void (*Py_FinalizePtr)(void);
typedef PyObject *(*PySys_GetObjectPtr)(const char *);
typedef int *(*PySys_SetArgvPtr)(int argc, char **argv);
typedef PyObject *(*PyObject_GetAttrStringPtr)(PyObject *, const char *);
typedef wchar_t* (*_Py_DecodeUTF8_surrogateescapePtr)(const char *s, ssize_t size, ssize_t* outsize);


typedef CFTypeRef id;
typedef const char * SEL;
typedef signed char BOOL;
#define NSAlertAlternateReturn 0

/*
    Forward declarations
*/
static int report_error(const char *);
static CFTypeRef py2app_getKey(const char *key);

/*
    Strings
*/
static const char *ERR_REALLYBADTITLE = "The application could not be launched.";
static const char *ERR_TITLEFORMAT = "%@ has encountered a fatal error, and will now terminate.";
static const char *ERR_NONAME = "The Info.plist file must have values for the CFBundleName or CFBundleExecutable strings.";
static const char *ERR_PYRUNTIMELOCATIONS = "The Info.plist file must have a PyRuntimeLocations array containing string values for preferred Python runtime locations.  These strings should be \"otool -L\" style mach ids; \"@executable_stub\" and \"~\" prefixes will be translated accordingly.";
static const char *ERR_NOPYTHONRUNTIME = "A Python runtime not could be located.  You may need to install a framework build of Python, or edit the PyRuntimeLocations array in this application's Info.plist file.";
static const char *ERR_NOPYTHONSCRIPT = "A main script could not be located in the Resources folder.;";
static const char *ERR_LINKERRFMT = "An internal error occurred while attempting to link with:\r\r%s\r\rSee the Console for a detailed dyld error message";
static const char *ERR_PYTHONEXCEPTION = "An uncaught exception was raised during execution of the main script.\r\rThis may mean that an unexpected error has occurred, or that you do not have all of the dependencies for this application.\r\rSee the Console for a detailed traceback.";
static const char *ERR_COLONPATH = "Python applications can not currently run from paths containing a '/' (or ':' from the Terminal).";
static const char *ERR_DEFAULTURLTITLE = "Visit Website";
static const char *ERR_CONSOLEAPP = "Console.app";
static const char *ERR_CONSOLEAPPTITLE = "Open Console";
static const char *ERR_TERMINATE = "Terminate";

/*
    Globals
*/
static CFMutableArrayRef py2app_pool;

#define USES(NAME) static __typeof__(&NAME) py2app_ ## NAME
/* ApplicationServices */
USES(LSOpenFSRef);
USES(LSFindApplicationForInfo);
/* CoreFoundation */
USES(CFArrayRemoveValueAtIndex);
USES(CFStringCreateFromExternalRepresentation);
USES(CFStringAppendCString);
USES(CFStringCreateMutable);
USES(kCFTypeArrayCallBacks);
USES(CFArrayCreateMutable);
USES(CFRetain);
USES(CFRelease);
USES(CFBundleGetValueForInfoDictionaryKey);
USES(CFArrayGetCount);
USES(CFStringCreateWithCString);
USES(CFArrayGetValueAtIndex);
USES(CFArrayAppendValue);
USES(CFStringFind);
USES(CFBundleCopyPrivateFrameworksURL);
USES(CFURLCreateWithFileSystemPathRelativeToBase);
USES(CFStringCreateWithSubstring);
USES(CFStringGetLength);
USES(CFURLGetFileSystemRepresentation);
USES(CFURLCreateWithFileSystemPath);
USES(CFShow);
USES(CFBundleCopyResourcesDirectoryURL);
USES(CFURLCreateFromFileSystemRepresentation);
USES(CFURLCreateFromFileSystemRepresentationRelativeToBase);
USES(CFStringGetCharacterAtIndex);
USES(CFURLCreateWithString);
USES(CFStringGetCString);
USES(CFStringCreateByCombiningStrings);
USES(CFDictionaryGetValue);
USES(CFBooleanGetValue);
USES(CFNumberGetValue);
USES(CFStringCreateArrayBySeparatingStrings);
USES(CFArrayAppendArray);
USES(CFStringCreateByCombiningStrings);
USES(CFStringCreateWithFormat);
USES(CFBundleCopyResourceURL);
USES(CFBundleCopyAuxiliaryExecutableURL);
USES(CFURLCreateCopyDeletingLastPathComponent);
USES(CFURLCreateCopyAppendingPathComponent);
USES(CFURLCopyLastPathComponent);
USES(CFStringGetMaximumSizeForEncoding);
#undef USES

/*
    objc
*/

static id (*py2app_objc_getClass)(const char *name);
static SEL (*py2app_sel_getUid)(const char *str);
static id (*py2app_objc_msgSend)(id self, SEL op, ...);

/*
    Cocoa
*/
static void (*py2app_NSLog)(CFStringRef format, ...);
static BOOL (*py2app_NSApplicationLoad)(void);
static int (*py2app_NSRunAlertPanel)(CFStringRef title, CFStringRef msg, CFStringRef defaultButton, CFStringRef alternateButton, CFStringRef otherButton, ...);

/*
    Functions
*/

static int bind_objc_Cocoa_ApplicationServices(void) {
    static Boolean bound = false;
    if (bound) return 0;
    bound = true;
    void* cf_dylib;
    cf_dylib = dlopen("/usr/lib/libobjc.dylib", RTLD_LAZY);
    if (!cf_dylib) return -1;

#define LOOKUP(NAME) do { \
    py2app_ ## NAME = (__typeof__(py2app_ ## NAME))dlsym( \
        cf_dylib, #NAME); \
        if (!py2app_ ## NAME) return -1; \
    } while (0)

    LOOKUP(objc_getClass);
    LOOKUP(sel_getUid);
    LOOKUP(objc_msgSend);

    cf_dylib = dlopen(
        "/System/Library/Frameworks/Cocoa.framework/Cocoa",
        RTLD_LAZY);
    if (!cf_dylib) return -1;
    LOOKUP(NSLog);
    LOOKUP(NSApplicationLoad);
    LOOKUP(NSRunAlertPanel);

    cf_dylib = dlopen(
        "/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices",
        RTLD_LAZY);
    if (!cf_dylib) return -1;

    LOOKUP(LSOpenFSRef);
    LOOKUP(LSFindApplicationForInfo);
#undef LOOKUP
    return 0;
}

static int bind_CoreFoundation(void) {
    static Boolean bound = false;
    void *cf_dylib;
    if (bound) return 0;
    bound = true;
    cf_dylib = dlopen(
        "/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation",
        RTLD_LAZY);
    if (!cf_dylib) return -1;

#define LOOKUP(NAME) do { \
    py2app_ ## NAME = (__typeof__(py2app_ ## NAME))dlsym( \
        cf_dylib, #NAME); \
        if (!py2app_ ## NAME) return -1; \
    } while (0)

    LOOKUP(CFArrayRemoveValueAtIndex);
    LOOKUP(CFStringCreateFromExternalRepresentation);
    LOOKUP(CFStringAppendCString);
    LOOKUP(CFStringCreateMutable);
    LOOKUP(kCFTypeArrayCallBacks);
    LOOKUP(CFArrayCreateMutable);
    LOOKUP(CFRetain);
    LOOKUP(CFRelease);
    LOOKUP(CFBundleGetValueForInfoDictionaryKey);
    LOOKUP(CFArrayGetCount);
    LOOKUP(CFStringCreateWithCString);
    LOOKUP(CFArrayGetValueAtIndex);
    LOOKUP(CFArrayAppendValue);
    LOOKUP(CFStringFind);
    LOOKUP(CFBundleCopyPrivateFrameworksURL);
    LOOKUP(CFURLCreateWithFileSystemPathRelativeToBase);
    LOOKUP(CFStringCreateWithSubstring);
    LOOKUP(CFStringGetLength);
    LOOKUP(CFURLGetFileSystemRepresentation);
    LOOKUP(CFURLCreateWithFileSystemPath);
    LOOKUP(CFShow);
    LOOKUP(CFBundleCopyResourcesDirectoryURL);
    LOOKUP(CFURLCreateFromFileSystemRepresentation);
    LOOKUP(CFURLCreateFromFileSystemRepresentationRelativeToBase);
    LOOKUP(CFStringGetCharacterAtIndex);
    LOOKUP(CFURLCreateWithString);
    LOOKUP(CFStringGetCString);
    LOOKUP(CFStringCreateByCombiningStrings);
    LOOKUP(CFDictionaryGetValue);
    LOOKUP(CFBooleanGetValue);
    LOOKUP(CFNumberGetValue);
    LOOKUP(CFStringCreateArrayBySeparatingStrings);
    LOOKUP(CFArrayAppendArray);
    LOOKUP(CFStringCreateByCombiningStrings);
    LOOKUP(CFStringCreateWithFormat);
    LOOKUP(CFBundleCopyResourceURL);
    LOOKUP(CFBundleCopyAuxiliaryExecutableURL);
    LOOKUP(CFURLCreateCopyDeletingLastPathComponent);
    LOOKUP(CFURLCreateCopyAppendingPathComponent);
    LOOKUP(CFURLCopyLastPathComponent);
    LOOKUP(CFStringGetMaximumSizeForEncoding);

#undef LOOKUP

    return 0;
}

#define AUTORELEASE(obj) ((obj == NULL) ? NULL : ( \
    py2app_CFArrayAppendValue(py2app_pool, (const void *)obj), \
    py2app_CFRelease(obj), \
    obj))

#define py2app_CFSTR(s) AUTORELEASE( \
    py2app_CFStringCreateWithCString(NULL, s, kCFStringEncodingUTF8))

static int py2app_openConsole(void) {
    OSStatus err;
    FSRef consoleRef;
    err = py2app_LSFindApplicationForInfo(
        kLSUnknownCreator,
        NULL,
        py2app_CFSTR(ERR_CONSOLEAPP),
        &consoleRef,
        NULL);
    if (err != noErr) return err;
    return py2app_LSOpenFSRef((const FSRef *)&consoleRef, NULL);
}

static CFTypeRef py2app_getKey(const char *key) {
    CFTypeRef rval;
    CFStringRef cfKey = py2app_CFStringCreateWithCString(NULL,
        key, kCFStringEncodingUTF8);
    if (!cfKey) return NULL;
    rval = py2app_CFBundleGetValueForInfoDictionaryKey(
        CFBundleGetMainBundle(),
        cfKey);
    py2app_CFRelease(cfKey);
    return rval;
}

static CFStringRef py2app_getApplicationName(void) {
    static CFStringRef name = NULL;
    if (name) return name;
    name = (CFStringRef)py2app_getKey("CFBundleName");
    if (!name) name = (CFStringRef)py2app_getKey("CFBundleExecutable");
    if (!name) name = py2app_CFSTR("py2app stub executable");
    return AUTORELEASE(name);
}


static CFStringRef py2app_getErrorTitle(CFStringRef applicationName) {
    CFStringRef res;
    if (!applicationName) return py2app_CFSTR(ERR_REALLYBADTITLE);
    res = py2app_CFStringCreateWithFormat(
        NULL, NULL, py2app_CFSTR(ERR_TITLEFORMAT), applicationName);
    (void)AUTORELEASE(res);
    return res;
}

static void ensureGUI(void) {
    ProcessSerialNumber psn;
    id app = ((id(*)(id, SEL))py2app_objc_msgSend)(py2app_objc_getClass("NSApplication"), py2app_sel_getUid("sharedApplication"));
    py2app_NSApplicationLoad();
    ((void(*)(id, SEL, BOOL))py2app_objc_msgSend)(app, py2app_sel_getUid("activateIgnoringOtherApps:"), 1);
}

static int report_error(const char *error) {
    int choice;
    id releasePool;

    if (bind_objc_Cocoa_ApplicationServices()) {
        fprintf(stderr, "%s\n", error);
        return -1;
    }
    releasePool = ((id(*)(id, SEL))py2app_objc_msgSend)(
		    ((id(*)(id, SEL))py2app_objc_msgSend)(
			    py2app_objc_getClass("NSAutoreleasePool"),
			    py2app_sel_getUid("alloc")),
		    py2app_sel_getUid("init"));
    py2app_NSLog(py2app_CFSTR("%@"), py2app_CFSTR(error));

    if (!py2app_NSApplicationLoad()) {
        py2app_NSLog(py2app_CFSTR("NSApplicationLoad() failed"));
    } else {
        ensureGUI();
        choice = py2app_NSRunAlertPanel(
            py2app_getErrorTitle(py2app_getApplicationName()),
            py2app_CFSTR("%@"),
            py2app_CFSTR(ERR_TERMINATE),
            py2app_CFSTR(ERR_CONSOLEAPPTITLE),
            NULL,
            py2app_CFSTR(error));
        if (choice == NSAlertAlternateReturn) py2app_openConsole();
    }
    ((void(*)(id, SEL))py2app_objc_msgSend)(releasePool, py2app_sel_getUid("release"));
    return -1;
}

static CFStringRef pathFromURL(CFURLRef anURL) {
    UInt8 buf[PATH_MAX];
    py2app_CFURLGetFileSystemRepresentation(anURL, true, buf, sizeof(buf));
    return py2app_CFStringCreateWithCString(NULL, (char *)buf, kCFStringEncodingUTF8);
}

static CFStringRef pyStandardizePath(CFStringRef pyLocation) {
    CFRange foundRange;
    CFURLRef fmwkURL;
    CFURLRef locURL;
    CFStringRef subpath;
    static CFStringRef prefix = NULL;
    if (!prefix) prefix = py2app_CFSTR("@executable_path/");
    foundRange = py2app_CFStringFind(pyLocation, prefix, 0);
    if (foundRange.location == kCFNotFound || foundRange.length == 0) {
        return NULL;
    }
    fmwkURL = py2app_CFBundleCopyPrivateFrameworksURL(CFBundleGetMainBundle());
    foundRange.location = foundRange.length;
    foundRange.length = py2app_CFStringGetLength(pyLocation) - foundRange.length;
    subpath = py2app_CFStringCreateWithSubstring(NULL, pyLocation, foundRange);
    locURL = py2app_CFURLCreateWithFileSystemPathRelativeToBase(
        NULL,
        subpath,
        kCFURLPOSIXPathStyle,
        false,
        fmwkURL);
    py2app_CFRelease(subpath);
    py2app_CFRelease(fmwkURL);
    subpath = pathFromURL(locURL);
    py2app_CFRelease(locURL);
    return subpath;
}

static Boolean doesPathExist(CFStringRef path) {
    struct stat st;
    CFURLRef locURL;
    UInt8 buf[PATH_MAX];
    locURL = py2app_CFURLCreateWithFileSystemPath(
        NULL, path, kCFURLPOSIXPathStyle, false);
    py2app_CFURLGetFileSystemRepresentation(locURL, true, buf, sizeof(buf));
    py2app_CFRelease(locURL);
    return (stat((const char *)buf, &st) == -1 ? false : true);
}

static CFStringRef py2app_findPyLocation(CFArrayRef pyLocations) {
    CFIndex i;
    CFIndex cnt = py2app_CFArrayGetCount(pyLocations);
    for (i = 0; i < cnt; i++) {
        CFStringRef newLoc;
        CFStringRef pyLocation = py2app_CFArrayGetValueAtIndex(pyLocations, i);
        newLoc = pyStandardizePath(pyLocation);
        if (!newLoc) {
		newLoc = pyLocation;
		py2app_CFRetain(newLoc);
	}
        if (doesPathExist(newLoc)) {
            return newLoc;
        }
        if (newLoc) py2app_CFRelease(newLoc);
    }
    return NULL;
}

static CFStringRef tildeExpand(CFStringRef path) {
    CFURLRef pathURL;
    char buf[PATH_MAX];
    CFURLRef fullPathURL;
    struct passwd *pwnam;
    char tmp;
    char *dir = NULL;


    py2app_CFStringGetCString(path, buf, sizeof(buf), kCFStringEncodingUTF8);

    int i;
    if (buf[0] != '~') {
        return py2app_CFStringCreateWithCString(
            NULL, buf, kCFStringEncodingUTF8);
    }
    /* user in path */
    i = 1;
    while (buf[i] != '\0' && buf[i] != '/') {
        i++;
    }
    if (i == 1) {
        dir = getenv("HOME");
    } else {
        tmp = buf[i];
        buf[i] = '\0';
        pwnam = getpwnam((const char *)&buf[1]);
        if (pwnam) dir = pwnam->pw_dir;
        buf[i] = tmp;
    }
    if (!dir) {
        return py2app_CFStringCreateWithCString(NULL, buf, kCFStringEncodingUTF8);
    }
    pathURL = py2app_CFURLCreateFromFileSystemRepresentation(
        NULL, (const UInt8*)dir, strlen(dir), false);
    fullPathURL = py2app_CFURLCreateFromFileSystemRepresentationRelativeToBase(
        NULL, (const UInt8*)&buf[i + 1], strlen(&buf[i + 1]), false, pathURL);
    py2app_CFRelease(pathURL);
    path = pathFromURL(fullPathURL);
    py2app_CFRelease(fullPathURL);
    return path;
}

static void setcfenv(char *name, CFStringRef value) {
    char buf[PATH_MAX];
    py2app_CFStringGetCString(value, buf, sizeof(buf), kCFStringEncodingUTF8);
    setenv(name, buf, 1);
}

static void py2app_setPythonPath(void) {
    CFMutableArrayRef paths;
    CFURLRef resDir;
    CFStringRef resPath;
    CFArrayRef resPackages;
    CFDictionaryRef options;

    paths = py2app_CFArrayCreateMutable(NULL, 0, py2app_kCFTypeArrayCallBacks);
    resDir = py2app_CFBundleCopyResourcesDirectoryURL(CFBundleGetMainBundle());

    resPath = pathFromURL(resDir);
    py2app_CFArrayAppendValue(paths, resPath);
    py2app_CFRelease(resPath);

    resPackages = py2app_getKey("PyResourcePackages");
    if (resPackages) {
        int i;
        int cnt = py2app_CFArrayGetCount(resPackages);
        for (i = 0; i < cnt; i++) {
            resPath = tildeExpand(py2app_CFArrayGetValueAtIndex(resPackages, i));
            if (py2app_CFStringGetLength(resPath)) {
                if (py2app_CFStringGetCharacterAtIndex(resPath, 0) != '/') {
                    CFURLRef absURL = py2app_CFURLCreateWithString(
                        NULL, resPath, resDir);
                    py2app_CFRelease(resPath);
                    resPath = pathFromURL(absURL);
                    py2app_CFRelease(absURL);
                }
                py2app_CFArrayAppendValue(paths, resPath);
            }
            py2app_CFRelease(resPath);
        }
    }

    py2app_CFRelease(resDir);

    options = py2app_getKey("PyOptions");
    if (options) {
        CFBooleanRef use_pythonpath;
	CFNumberRef optimize;
        use_pythonpath = py2app_CFDictionaryGetValue(
            options, py2app_CFSTR("use_pythonpath"));
        if (use_pythonpath && py2app_CFBooleanGetValue(use_pythonpath)) {
            char *ppath = getenv("PYTHONPATH");
            if (ppath) {
                CFArrayRef oldPath;
                oldPath = py2app_CFStringCreateArrayBySeparatingStrings(
                    NULL, py2app_CFSTR(ppath), py2app_CFSTR(":"));
                if (oldPath) {
                    CFRange rng;
                    rng.location = 0;
                    rng.length = py2app_CFArrayGetCount(oldPath);
                    py2app_CFArrayAppendArray(paths, oldPath, rng);
                    py2app_CFRelease(oldPath);
                }
            }
        }

	optimize = py2app_CFDictionaryGetValue(
		options, py2app_CFSTR("optimize"));
	if (optimize) {
		int v = 0;
		char buf[32];
		py2app_CFNumberGetValue(optimize, kCFNumberIntType, &v);
		snprintf(buf, 31, "%d", v);
		setenv("PYTHONOPTIMIZE", buf, 1);
	}
    }

    if (py2app_CFArrayGetCount(paths)) {
        resPath = py2app_CFStringCreateByCombiningStrings(NULL, paths, py2app_CFSTR(":"));
        setcfenv("PYTHONPATH", resPath);
        py2app_CFRelease(resPath);
    } else {
	 if (getenv("PYTHONPATH") != NULL) {
	     unsetenv("PYTHONPATH");
	 }
    }

    py2app_CFRelease(paths);
}



static void setResourcePath(void) {
    CFURLRef resDir;
    CFStringRef resPath;
    resDir = py2app_CFBundleCopyResourcesDirectoryURL(CFBundleGetMainBundle());
    resPath = pathFromURL(resDir);
    py2app_CFRelease(resDir);
    setcfenv("RESOURCEPATH", resPath);
    py2app_CFRelease(resPath);
}

static void setExecutablePath(void) {
    char executable_path[PATH_MAX+1];
    uint32_t bufsize = PATH_MAX;
    memset(executable_path, '\0', PATH_MAX+1);
    if (_NSGetExecutablePath(executable_path, &bufsize) == 0) {
        setenv("EXECUTABLEPATH", executable_path, 1);
    }
}

static CFStringRef getMainScript(void) {
    CFMutableArrayRef possibleMains;
    CFBundleRef bndl;
    CFStringRef e_py, e_pyc, e_pyo, path;
    int i, cnt;
    possibleMains = py2app_CFArrayCreateMutable(NULL, 0, py2app_kCFTypeArrayCallBacks);
    CFArrayRef firstMains = py2app_getKey("PyMainFileNames");
    if (firstMains) {
        CFRange rng;
        rng.location = 0;
        rng.length = py2app_CFArrayGetCount(firstMains);
        py2app_CFArrayAppendArray(possibleMains, firstMains, rng);
    }
    py2app_CFArrayAppendValue(possibleMains, py2app_CFSTR("__main__"));
    py2app_CFArrayAppendValue(possibleMains, py2app_CFSTR("__realmain__"));
    py2app_CFArrayAppendValue(possibleMains, py2app_CFSTR("Main"));

    e_py = py2app_CFSTR("py");
    e_pyc = py2app_CFSTR("pyc");
    e_pyo = py2app_CFSTR("pyo");

    cnt = py2app_CFArrayGetCount(possibleMains);
    bndl = CFBundleGetMainBundle();
    path = NULL;
    for (i = 0; i < cnt; i++) {
        CFStringRef base;
        CFURLRef resURL;
        base = py2app_CFArrayGetValueAtIndex(possibleMains, i);
        resURL = py2app_CFBundleCopyResourceURL(bndl, base, e_py, NULL);
        if (resURL == NULL) {
            resURL = py2app_CFBundleCopyResourceURL(bndl, base, e_pyc, NULL);
        }
        if (resURL == NULL) {
            resURL = py2app_CFBundleCopyResourceURL(bndl, base, e_pyo, NULL);
        }
        if (resURL != NULL) {
            path = pathFromURL(resURL);
            py2app_CFRelease(resURL);
            break;
        }
    }
    py2app_CFRelease(possibleMains);
    return path;
}

static int report_linkEdit_error(void) {
    CFStringRef errString;
    const char *errorString;
    char* buf;
    errorString = dlerror();
    fputs(errorString, stderr);
    errString = py2app_CFStringCreateWithFormat(
        NULL, NULL, py2app_CFSTR(ERR_LINKERRFMT), errorString);
    buf = alloca(py2app_CFStringGetMaximumSizeForEncoding(
            py2app_CFStringGetLength(errString), kCFStringEncodingUTF8));
    py2app_CFStringGetCString(errString, buf, sizeof(buf), kCFStringEncodingUTF8);
    py2app_CFRelease(errString);
    return report_error(buf);
}

static CFStringRef getPythonInterpreter(CFStringRef pyLocation) {
    CFBundleRef bndl;
    CFStringRef auxName;
    CFURLRef auxURL;
    CFStringRef path;

    auxName = py2app_getKey("PyExecutableName");
    if (!auxName) auxName = py2app_CFSTR("python");
    bndl = CFBundleGetMainBundle();
    auxURL = py2app_CFBundleCopyAuxiliaryExecutableURL(bndl, auxName);
    if (auxURL) {
        path = pathFromURL(auxURL);
        py2app_CFRelease(auxURL);
        return path;
    }
    return NULL;
}

static CFStringRef getErrorScript(void) {
    CFMutableArrayRef errorScripts;
    CFBundleRef bndl;
    CFStringRef path;
    int i, cnt;
    errorScripts = py2app_CFArrayCreateMutable(NULL, 0, py2app_kCFTypeArrayCallBacks);
    CFArrayRef firstErrorScripts = py2app_getKey("PyErrorScripts");
    if (firstErrorScripts) {
        CFRange rng;
        rng.location = 0;
        rng.length = py2app_CFArrayGetCount(firstErrorScripts);
        py2app_CFArrayAppendArray(errorScripts, firstErrorScripts, rng);
    }
    py2app_CFArrayAppendValue(errorScripts, py2app_CFSTR("__error__"));
    py2app_CFArrayAppendValue(errorScripts, py2app_CFSTR("__error__.py"));
    py2app_CFArrayAppendValue(errorScripts, py2app_CFSTR("__error__.pyc"));
    py2app_CFArrayAppendValue(errorScripts, py2app_CFSTR("__error__.pyo"));
    py2app_CFArrayAppendValue(errorScripts, py2app_CFSTR("__error__.sh"));

    cnt = py2app_CFArrayGetCount(errorScripts);
    bndl = CFBundleGetMainBundle();
    path = NULL;
    for (i = 0; i < cnt; i++) {
        CFStringRef base;
        CFURLRef resURL;
        base = py2app_CFArrayGetValueAtIndex(errorScripts, i);
        resURL = py2app_CFBundleCopyResourceURL(bndl, base, NULL, NULL);
        if (resURL) {
            path = pathFromURL(resURL);
            py2app_CFRelease(resURL);
            break;
        }
    }
    py2app_CFRelease(errorScripts);
    return path;

}

static CFMutableArrayRef get_trimmed_lines(CFStringRef output) {
    CFMutableArrayRef lines;
    CFArrayRef tmp;
    CFRange rng;
    lines = py2app_CFArrayCreateMutable(NULL, 0, py2app_kCFTypeArrayCallBacks);
    tmp = py2app_CFStringCreateArrayBySeparatingStrings(
        NULL, output, py2app_CFSTR("\n"));
    rng.location = 0;
    rng.length = py2app_CFArrayGetCount(tmp);
    py2app_CFArrayAppendArray(lines, tmp, rng);
    while (true) {
        CFIndex cnt = py2app_CFArrayGetCount(lines);
        CFStringRef last;
        /* Nothing on stdout means pass silently */
        if (cnt <= 0) {
            py2app_CFRelease(lines);
            return NULL;
        }
        last = py2app_CFArrayGetValueAtIndex(lines, cnt - 1);
        if (py2app_CFStringGetLength(last) > 0) break;
        py2app_CFArrayRemoveValueAtIndex(lines, cnt - 1);
    }
    return lines;
}

static int report_script_error(const char *msg) {
    CFStringRef errorScript;
    CFMutableArrayRef lines;
    CFRange foundRange;
    CFStringRef lastLine;
    CFStringRef output = NULL;
    CFIndex lineCount;
    CFURLRef buttonURL = NULL;
    CFStringRef buttonString = NULL;
    CFStringRef title = NULL;
    CFStringRef errmsg = NULL;
    id releasePool;
    int errBinding;
    int status = 0;

    errorScript = getErrorScript();
    if (!errorScript) return report_error(msg);

    errBinding = bind_objc_Cocoa_ApplicationServices();
    if (!errBinding) {
        id task, stdoutPipe, taskData;
        CFMutableArrayRef argv;
        releasePool = ((id(*)(id, SEL))py2app_objc_msgSend)(
		    ((id(*)(id, SEL))py2app_objc_msgSend)(
			    py2app_objc_getClass("NSAutoreleasePool"),
			    py2app_sel_getUid("alloc")),
		    py2app_sel_getUid("init"));
        task = ((id(*)(id, SEL))py2app_objc_msgSend)(
		    ((id(*)(id, SEL))py2app_objc_msgSend)(
			    py2app_objc_getClass("NSTask"),
			    py2app_sel_getUid("alloc")),
		    py2app_sel_getUid("init"));
        stdoutPipe = ((id(*)(id, SEL))py2app_objc_msgSend)(py2app_objc_getClass("NSPipe"), py2app_sel_getUid("pipe"));
        ((void(*)(id, SEL, id))py2app_objc_msgSend)(task, py2app_sel_getUid("setLaunchPath:"), py2app_CFSTR("/bin/sh"));
        ((void(*)(id, SEL, id))py2app_objc_msgSend)(task, py2app_sel_getUid("setStandardOutput:"), stdoutPipe);
        argv = py2app_CFArrayCreateMutable(NULL, 0, py2app_kCFTypeArrayCallBacks);
        py2app_CFArrayAppendValue(argv, errorScript);
        py2app_CFArrayAppendValue(argv, py2app_getApplicationName());
        ((void(*)(id, SEL, id))py2app_objc_msgSend)(task, py2app_sel_getUid("setArguments:"), argv);
        /* This could throw, in theory, but /bin/sh should prevent that */
        ((void(*)(id, SEL))py2app_objc_msgSend)(task, py2app_sel_getUid("launch"));
        ((void(*)(id, SEL))py2app_objc_msgSend)(task, py2app_sel_getUid("waitUntilExit"));
        taskData = ((id(*)(id, SEL))py2app_objc_msgSend)(
            ((id(*)(id, SEL))py2app_objc_msgSend)(stdoutPipe, py2app_sel_getUid("fileHandleForReading")),
            py2app_sel_getUid("readDataToEndOfFile"));
        py2app_CFRelease(argv);

        status = ((int(*)(id, SEL))py2app_objc_msgSend)(task, py2app_sel_getUid("terminationStatus"));
        py2app_CFRelease(task);
        if (!status && taskData) {
            output = py2app_CFStringCreateFromExternalRepresentation(
                NULL, taskData, kCFStringEncodingUTF8);
        }

        ((void(*)(id, SEL))py2app_objc_msgSend)(releasePool, py2app_sel_getUid("release"));
    }

    py2app_CFRelease(errorScript);
    if (status || !output) return report_error(msg);

    lines = get_trimmed_lines(output);
    py2app_CFRelease(output);
    /* Nothing on stdout means pass silently */
    if (!lines) return -1;
    lineCount = py2app_CFArrayGetCount(lines);
    lastLine = py2app_CFArrayGetValueAtIndex(lines, lineCount - 1);
    foundRange = py2app_CFStringFind(lastLine, py2app_CFSTR("ERRORURL: "), 0);
    if (foundRange.location != kCFNotFound && foundRange.length != 0) {
        CFMutableArrayRef buttonArr;
        CFArrayRef tmp;
        CFRange rng;
        buttonArr = py2app_CFArrayCreateMutable(NULL, 0, py2app_kCFTypeArrayCallBacks);
        tmp = py2app_CFStringCreateArrayBySeparatingStrings(
            NULL, lastLine, py2app_CFSTR(" "));
        lineCount -= 1;
        py2app_CFArrayRemoveValueAtIndex(lines, lineCount);
        rng.location = 1;
        rng.length = py2app_CFArrayGetCount(tmp) - 1;
        py2app_CFArrayAppendArray(buttonArr, tmp, rng);
        py2app_CFRelease(tmp);
        while (true) {
            CFStringRef tmpstr;
            if (py2app_CFArrayGetCount(buttonArr) <= 0) break;
            tmpstr = py2app_CFArrayGetValueAtIndex(buttonArr, 0);
            if (py2app_CFStringGetLength(tmpstr) == 0) {
                py2app_CFArrayRemoveValueAtIndex(buttonArr, 0);
            } else {
                break;
            }
        }

        buttonURL = py2app_CFURLCreateWithString(
            NULL, py2app_CFArrayGetValueAtIndex(buttonArr, 0), NULL);
        if (buttonURL) {
            py2app_CFArrayRemoveValueAtIndex(buttonArr, 0);
            while (true) {
                CFStringRef tmpstr;
                if (py2app_CFArrayGetCount(buttonArr) <= 0) break;
                tmpstr = py2app_CFArrayGetValueAtIndex(buttonArr, 0);
                if (py2app_CFStringGetLength(tmpstr) == 0) {
                    py2app_CFArrayRemoveValueAtIndex(buttonArr, 0);
                } else {
                    break;
                }
            }
            if (py2app_CFArrayGetCount(buttonArr) > 0) {
                buttonString = py2app_CFStringCreateByCombiningStrings(
                    NULL, buttonArr, py2app_CFSTR(" "));
            }
            if (!buttonString) buttonString = py2app_CFSTR(ERR_DEFAULTURLTITLE);
        }
        py2app_CFRelease(buttonArr);

    }
    if (lineCount <= 0 || errBinding) {
        py2app_CFRelease(lines);
        return report_error(msg);
    }

    releasePool = ((id(*)(id, SEL))py2app_objc_msgSend)(
		    ((id(*)(id, SEL))py2app_objc_msgSend)(
			    py2app_objc_getClass("NSAutoreleasePool"),
			    py2app_sel_getUid("alloc")),
		    py2app_sel_getUid("init"));

    title = py2app_CFArrayGetValueAtIndex(lines, 0);
    py2app_CFRetain(title);
    (void)AUTORELEASE(title);
    lineCount -= 1;
    py2app_CFArrayRemoveValueAtIndex(lines, lineCount);
    py2app_NSLog(py2app_CFSTR("%@"), title);
    if (lineCount > 0) {
        CFStringRef showerr;
        errmsg = py2app_CFStringCreateByCombiningStrings(
            NULL, lines, py2app_CFSTR("\r"));
        (void)AUTORELEASE(errmsg);
        showerr = ((id(*)(id, SEL, id))py2app_objc_msgSend)(
            ((id(*)(id, SEL, id))py2app_objc_msgSend)(errmsg, py2app_sel_getUid("componentsSeparatedByString:"), py2app_CFSTR("\r")),
            py2app_sel_getUid("componentsJoinedByString:"), py2app_CFSTR("\n"));
        py2app_NSLog(py2app_CFSTR("%@"), showerr);
    } else {
        errmsg = py2app_CFSTR("");
    }

    ensureGUI();
    if (!buttonURL) {
        int choice = py2app_NSRunAlertPanel(
            title, py2app_CFSTR("%@"), py2app_CFSTR(ERR_TERMINATE),
            py2app_CFSTR(ERR_CONSOLEAPPTITLE), NULL, errmsg);
        if (choice == NSAlertAlternateReturn) py2app_openConsole();
    } else {
        int choice = py2app_NSRunAlertPanel(
            title, py2app_CFSTR("%@"), py2app_CFSTR(ERR_TERMINATE),
            buttonString, NULL, errmsg);
        if (choice == NSAlertAlternateReturn) {
            id ws = ((id(*)(id, SEL))py2app_objc_msgSend)(py2app_objc_getClass("NSWorkspace"), py2app_sel_getUid("sharedWorkspace"));
            ((void(*)(id, SEL, id))py2app_objc_msgSend)(ws, py2app_sel_getUid("openURL:"), buttonURL);
        }
    }
    ((void(*)(id, SEL))py2app_objc_msgSend)(releasePool, py2app_sel_getUid("release"));
    py2app_CFRelease(lines);
    return -1;
}

static int py2app_main(int argc, char * const *argv, char * const *envp) {
    CFArrayRef pyLocations;
    CFStringRef pyLocation;
    CFStringRef mainScript;
    CFStringRef pythonInterpreter;
    char *resource_path;
    char buf[PATH_MAX];
    char c_pythonInterpreter[PATH_MAX];
    char c_mainScript[PATH_MAX];
    char **argv_new;
    struct stat sb;
    void *py_dylib;
    int rval;
    FILE *mainScriptFile;
    char* curenv = NULL;
    char* curlocale = NULL;


    if (getenv("PYTHONOPTIMIZE") != NULL) {
        unsetenv("PYTHONOPTIMIZE");
    }
    if (getenv("PYTHONDEBUG") != NULL) {
        unsetenv("PYTHONDEBUG");
    }
    if (getenv("PYTHONDONTWRITEBYTECODE") != NULL) {
        unsetenv("PYTHONDONTWRITEBYTECODE");
    }
    if (getenv("PYTHONIOENCODING") != NULL) {
        unsetenv("PYTHONIOENCODING");
    }
    if (getenv("PYTHONDUMPREFS") != NULL) {
        unsetenv("PYTHONDUMPREFS");
    }
    if (getenv("PYTHONMALLOCSTATS") != NULL) {
        unsetenv("PYTHONMALLOCSTATS");
    }

    /* Ensure that the interpreter won't try to write bytecode files
     * Two reasons:
     * - Apps are often read-only for users
     * - Writing byte-code will be blocked by the sandbox
     *   when running a sandboxed application.
     */
    setenv("PYTHONDONTWRITEBYTECODE", "1", 1);

#ifndef PY2APP_SECONDARY
    /*
     * Force stdout/stderr to be unbuffered, needed when using the ASL
     * output redirection because Python 3's IO library won't use
     * line buffering with that.
     */
    setenv("PYTHONUNBUFFERED", "1", 1);
#endif


    if (!py2app_getApplicationName()) return report_error(ERR_NONAME);
    pyLocations = (CFArrayRef)py2app_getKey("PyRuntimeLocations");
    if (!pyLocations) return report_error(ERR_PYRUNTIMELOCATIONS);
    pyLocation = py2app_findPyLocation(pyLocations);
    if (!pyLocation) return report_error(ERR_NOPYTHONRUNTIME);

    setExecutablePath();
    setResourcePath();
    /* check for ':' in path, not compatible with Python due to Py_GetPath */
    /* XXX: Could work-around by creating something in /tmp I guess */
    resource_path = getenv("RESOURCEPATH");
    if ((resource_path == NULL) || (strchr(resource_path, ':') != NULL)) {
        return report_error(ERR_COLONPATH);
    }
    py2app_setPythonPath();
    setenv("ARGVZERO", argv[0], 1);

    /* Clear unwanted environment variable that could be set
     * by a PyObjC bundle in a parent process. Not clearing causes
     * problems in PyObjC.
     */
    if (getenv("PYOBJC_BUNDLE_ADDRESS") != NULL) {
        unsetenv("PYOBJC_BUNDLE_ADDRESS");
    }
    snprintf(buf, sizeof(buf)-1, "PYOBJC_BUNDLE_ADDRESS%ld", (long)getpid());
    if (getenv(buf) != NULL) {
        unsetenv(buf);
    }

    mainScript = getMainScript();
    if (!mainScript) return report_error(ERR_NOPYTHONSCRIPT);

    pythonInterpreter = getPythonInterpreter(pyLocation);
    py2app_CFStringGetCString(
        pythonInterpreter, c_pythonInterpreter,
        sizeof(c_pythonInterpreter), kCFStringEncodingUTF8);
    py2app_CFRelease(pythonInterpreter);
    if (lstat(c_pythonInterpreter, &sb) == 0) {
        if (!((sb.st_mode & S_IFLNK) == S_IFLNK)) {
            setenv("PYTHONHOME", resource_path, 1);
        }
    }

    py2app_CFStringGetCString(pyLocation, buf, sizeof(buf), kCFStringEncodingUTF8);
    py_dylib = dlopen(buf, RTLD_LAZY);
    if (!py_dylib) return report_linkEdit_error();

#define LOOKUP(NAME) \
	    NAME ## Ptr py2app_ ## NAME = (NAME ## Ptr)dlsym(py_dylib, #NAME); \
	    if (!py2app_ ## NAME) { \
		return report_linkEdit_error(); \
	    }

#define OPT_LOOKUP(NAME) \
	    NAME ## Ptr py2app_ ## NAME = (NAME ## Ptr)dlsym(py_dylib, #NAME);

    LOOKUP(Py_SetProgramName);
    LOOKUP(Py_Initialize);
    LOOKUP(PyRun_SimpleFile);
    LOOKUP(Py_Finalize);
    LOOKUP(PySys_GetObject);
    LOOKUP(PySys_SetArgv);
    LOOKUP(PyObject_GetAttrString);
    LOOKUP(Py_BuildValue);
#if 0
    OPT_LOOKUP(Py_SetPath);
#endif
    OPT_LOOKUP(_Py_DecodeUTF8_surrogateescape);
    LOOKUP(PySys_SetObject);


    int isPy3K = dlsym(py_dylib, "PyBytes_FromString") != NULL;

#undef OPT_LOOKUP
#undef LOOKUP

    if (isPy3K) {
	    /*
	     * When apps are started from the Finder (or anywhere
	     * except from the terminal), the LANG and LC_* variables
	     * aren't set in the environment. This confuses Py_Initialize
	     * when it tries to import the codec for UTF-8,
	     * therefore explicitly set the locale.
	     *
	     * Also set the LC_CTYPE environment variable because Py_Initialize
	     * resets the locale information using the environment :-(
	     */
	    curlocale = setlocale(LC_ALL, NULL);
	    if (curlocale != NULL) {
	      curlocale = strdup(curlocale);
	      if (curlocale == NULL) {
		(void)report_error("cannot save locale information");
		return -1;
	      }
	    }
	    setlocale(LC_ALL, "en_US.UTF-8");

	    curenv = getenv("LC_CTYPE");
	    if (curenv == NULL) {
		setenv("LC_CTYPE", "en_US.UTF-8", 1);
	    }

	    wchar_t w_pythonInterpreter[PATH_MAX+1];
    	    mbstowcs(w_pythonInterpreter, c_pythonInterpreter, PATH_MAX+1);
    	    py2app_Py_SetProgramName((char*)w_pythonInterpreter);


    } else {
	    py2app_Py_SetProgramName(c_pythonInterpreter);
    }

    py2app_Py_Initialize();

    /*
     * Reset the environment and locale information
     */
    if (isPy3K) {
	    if (curenv == NULL) {
		unsetenv("LC_CTYPE");
	    }

	    setlocale(LC_CTYPE, curlocale);
	    free(curlocale);
    }

    py2app_CFStringGetCString(
        mainScript, c_mainScript,
        sizeof(c_mainScript), kCFStringEncodingUTF8);
    py2app_CFRelease(mainScript);

    if (isPy3K) {
       int i;

       argv_new = alloca((argc+1) * sizeof(wchar_t*));
       argv_new[argc] = NULL;
       argv_new[0] = (char*)py2app__Py_DecodeUTF8_surrogateescape(c_mainScript, strlen(c_mainScript), NULL);

       for (i = 1; i < argc; i++) {
	  argv_new[i] = (char*)py2app__Py_DecodeUTF8_surrogateescape(argv[i], strlen(argv[i]), NULL);
       }

    } else {
       argv_new = alloca((argc + 1) * sizeof(char *));
       argv_new[argc] = NULL;
       argv_new[0] = c_mainScript;
       memcpy(&argv_new[1], &argv[1], (argc - 1) * sizeof(char *));
    }
    py2app_PySys_SetArgv(argc, argv_new);

    mainScriptFile = fopen(c_mainScript, "r");
    rval = py2app_PyRun_SimpleFile(mainScriptFile, c_mainScript);
    fclose(mainScriptFile);

    if (rval) {
        rval = report_script_error(ERR_PYTHONEXCEPTION);
    }

    py2app_Py_Finalize();

    return rval;
}

#ifdef REDIRECT_ASL
void
setup_asl(const char* appname)
{
	/*
	 * On Mac OS X 10.8 or later the contents of stdout and stderr
	 * do not end up in de Console.app log (neither in de default
	 * view or some other view).
	 *
	 * This function detects if "asl_log_descriptor" is available
	 * (introduced in 10.8), and if it is configures ASL to redirect
	 * all writes to stdout/stderr to the ASL in such a way that
	 * log lines end up in the default view of Console.app.
	 */

	/* Function definitions, don't use the ASL header because that
	 * doesn't contain all definitions when building the binaries
	 * with PPC support.
	 */
	typedef void* aslclient;
	typedef void* aslmsg;

	aslclient (*do_asl_open)(const char*, const char*, int);
	int (*do_asl_add_log_file)(aslclient, int);
	int (*do_asl_log_descriptor)(aslclient, aslmsg, int, int, uint32_t);
	int (*do_asl_set)(aslmsg, const char*, const char*);
	aslmsg (*do_asl_new)(int);

	/*
	 * Try to resolve the ASL function's we're using.
	 */
        void* sys_dylib;
        sys_dylib = dlopen("/usr/lib/libSystem.dylib", RTLD_LAZY);

	do_asl_open = dlsym(sys_dylib, "asl_open");
	do_asl_add_log_file = dlsym(sys_dylib, "asl_add_log_file");
	do_asl_log_descriptor = dlsym(sys_dylib, "asl_log_descriptor");
	do_asl_set = dlsym(sys_dylib, "asl_set");
	do_asl_new = dlsym(sys_dylib, "asl_new");

	if (do_asl_log_descriptor == NULL) {
		/* asl_log_descriptor is not available: running on OSX 10.7
		 * or earlier, which means we can't set up ASL and don't have to
		 */
		return;
	}

	aslclient cl;
	aslmsg msg;
	int fd2;
	char uidbuf[64];

	cl = do_asl_open(appname, "com.apple.console", 2 /* ASL_OPT_NO_DELAY */);
	if (cl == NULL) {
		return;
	}

	/* Tell ASL to write all log lines to STDERR as well, use a dup-ed file
	 * descriptor because we'll later replace the original one by a file descriptor
	 * from ASL.
	 */
	fd2 = dup(2);
	do_asl_add_log_file(cl, fd2);

	/*
	 * Create an ASL template message for the STDOUT/STDERR redirection.
	 * All keys are required to get log messages into the default view of Console.app
	 * for normal users.
	 */
	snprintf(uidbuf, sizeof(uidbuf), "%d", getuid());
	msg = do_asl_new(0 /* ASL_TYPE_MSG */);
	do_asl_set(msg, "Facility" /* ASL_KEY_FACILITY */, "com.apple.console");
	do_asl_set(msg, "Level" /* ASL_KEY_LEVEL */, "Notice" /* ASL_STRING_NOTICE */);
	do_asl_set(msg, "ReadUID" /* ASL_KEY_READ_UID */, uidbuf /* or "-1" for "All users" */);

	/*
	 * Finally: redirect the STDOUT/STDERR file descriptors to ASL.
	 */
	do_asl_log_descriptor(cl, msg, 4 /* ASL_LEVEL_NOTICE */, 1, 2 /* ASL_LOG_DESCRIPTOR_WRITE */);
	do_asl_log_descriptor(cl, msg, 4 /* ASL_LEVEL_NOTICE */, 2, 2 /* ASL_LOG_DESCRIPTOR_WRITE */);
}
#endif

#ifndef PY2APP_SECONDARY
static int
have_psn_arg(int argc, char* const * argv)
{
	int i;

	for (i = 0; i < argc; i++) {
		if (strncmp(argv[i], "-psn_", 5) == 0) {
			if (isdigit(argv[i][5])) {
				return 1;
			}
		}
	}
	return 0;
}
#endif /* !PY2APP_SECONDARY */


int
main(int argc, char * const *argv, char * const *envp)
{
    int rval;

#ifndef PY2APP_SECONDARY
    /* Running as a GUI app started by launch
     * services, try to redirect stdout/stderr
     * to ASL.
     *
     * NOTE: Detecting application bundles on OSX 10.9
     * is annoyingly hard, the devnull trick is the least
     * worst option I've found yet.
     */
    struct stat st;
    struct utsname uts;
    int is_app_bundle = 1;

    if (uname(&uts) != -1) {
        if (strcmp(uts.release, "13.") <= 0) {
	    /* OSX 10.8 or earlier */
            if (!have_psn_arg(argc, argv)) {
                is_app_bundle = 0;
	    }
	} else {
	    /* OSX 10.9 or later */
            if (fstat(1, &st) != -1) {
		is_app_bundle = 0;
		if (S_ISCHR(st.st_mode)) {
		    if (major(st.st_dev) == 3 && minor(st.st_dev) == 2) {
			/* devnull */
		        is_app_bundle = 1;
		    } else if (major(st.st_dev) != 4 && major(st.st_dev) != 5) {
			/* not pty or tty */
		        is_app_bundle = 1;
		    }
		}
            }
        }
    }


    if (is_app_bundle) {
        const char *bname;
        setenv("_PY2APP_LAUNCHED_", "1", 1);

        bname = strrchr(argv[0], '/');
        if (bname == NULL) {
	    bname = argv[0];
        } else {
	    bname++;
        }

#ifdef REDIRECT_ASL
        setup_asl(bname);
#endif /* REDIRECT_ASL */
    }
#endif /* !PY2APP_SECONDARY */

    if (bind_CoreFoundation()) {
        fprintf(stderr, "CoreFoundation not found or functions missing\n");
        return -1;
    }
    if (!CFBundleGetMainBundle()) {
        fprintf(stderr, "Not bundled, exiting\n");
        return -1;
    }
    py2app_pool = py2app_CFArrayCreateMutable(NULL, 0, py2app_kCFTypeArrayCallBacks);
    if (!py2app_pool) {
        fprintf(stderr, "Couldn't create global pool\n");
        return -1;
    }
    rval = py2app_main(argc, argv, envp);
    py2app_CFRelease(py2app_pool);
    return rval;
}
