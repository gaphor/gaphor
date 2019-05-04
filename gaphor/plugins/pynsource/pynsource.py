"""
PyNSource
Version 1.4c
(c) Andy Bulka 2004-2006
abulka@netspace.net.au
http://www.atug.com/andypatterns/pynsource.htm

A python source code scanner that generates
 - UML pictures (as text)
 - Java code (which can be imported into UML modeling tools.)
 - UML diagrams in wxpython (see associated module pyNsourceGui.py)


GUI FRONT END
-------------

Simply run
     C:\Python22\Lib\site-packages\pynsource\pyNsourceGui.py

you need wxpython installed.  See http://www.wxpython.org

SOURCE GENERATOR
----------------

Example Usage: C:\Python22\Lib\site-packages\pynsource\pynsource -v -m -j outdir sourcedirorpythonfiles...

-j generate java files, specify output folder for java files
-v verbose
-m create psuedo class for each module,
   module attrs/defs etc treated as class attrs/defs

BASIC EXAMPLES
e.g. pynsource Test/testmodule01.py
e.g. pynsource -m Test/testmodule03.py
JAVA EXAMPLES
e.g. pynsource -j c:/try c:/try
e.g. pynsource -v -m -j c:/try c:/try
e.g. pynsource -v -m -j c:/try c:/try/s*.py
e.g. pynsource -j c:/try c:/try/s*.py Tests/u*.py
e.g. pynsource -v -m -j c:/try c:/try/s*.py Tests/u*.py c:\cc\Devel\Client\w*.py
DELPHI EXAMPLE
e.g. pynsource -d c:/delphiouputdir c:/pythoninputdir/*.py

INSTALLATION
-------------

python setup.py install

or run the windows .exe installer.

JBUILDER TIPS
-------------
Consider some folder e.g. .../Tests/ and create a jbuilder project based off there called
PythonToJavaTest01 which will
actually create a folder called PythonToJavaTest01 plus
subfolders called src and classes etc.  The Borland project file

will also live in .../Tests/PythonToJavaTest01/ with a name PythonToJavaTest01.jpx

Run pynsource so that it dumps the output into the src folder

e.g. assuming the batch file is in the PythonToJavaTest01 folder and the python source is in
    .../Tests/PythonToJavaTest01/pythoninput01
then the command is
    pynsource -j src pythoninput01\*.py

"""

from functools import cmp_to_key
import os
import pprint
import token
import tokenize

from gaphor.plugins.pynsource.keywords import (
    pythonbuiltinfunctions,
    javakeywords,
    delphikeywords,
)

DEBUG_DUMPTOKENS = False


class AndyBasicParseEngine:
    def __init__(self):
        self.meat = 0
        self.tokens = None
        self.isfreshline = 1
        self.indentlevel = 0

    def _ReadAllTokensFromFile(self, file):
        fp = open(file, "r")
        try:
            self.tokens = [x[0:2] for x in tokenize.generate_tokens(fp.readline)]
        finally:
            fp.close()
        if DEBUG_DUMPTOKENS:
            pprint.pprint(self.tokens)

    def Parse(self, file):
        self._ReadAllTokensFromFile(file)
        self.meat = 0
        self._ParseLoop()

    def _ParseLoop(self):
        maxtokens = len(self.tokens)
        for i in range(0, maxtokens):

            tokentype, token = self.tokens[i]
            if tokentype == 5:
                self.indentlevel += 1
                continue
            elif tokentype == 6:
                self.indentlevel -= 1
                self.On_deindent()
                continue

            if tokentype == 0:  # End Marker.
                break

            assert token, (
                "Not expecting blank token, once have detected in & out dents. tokentype=%d, token=%s"
                % (tokentype, token)
            )

            self.tokentype, self.token = tokentype, token
            if i + 1 < maxtokens:
                self.nexttokentype, self.nexttoken = self.tokens[i + 1]
            else:
                self.nexttokentype, self.nexttoken = (0, None)

            if self._Isblank():
                continue
            else:
                # print 'MEAT', self.token
                self._Gotmeat()

    def On_deindent(self):
        pass

    def On_newline(self):
        pass

    def On_meat(self):
        pass

    def _Gotmeat(self):
        self.meat = 1
        self.On_meat()
        self.isfreshline = 0  # must be here, at the end.

    def _Isblank(self):
        if self._Isnewline():
            return 1
        if self._Ispadding():
            return 1
        return 0

    def _Isnewline(self):
        if self.token == "\n" or self.tokentype == token.N_TOKENS:
            if self.tokentype == token.N_TOKENS:
                assert "#" in self.token
            self.meat = 0
            self.isfreshline = 1
            self.On_newline()
            return 1
        else:
            return 0

    def _Ispadding(self):
        if not self.token.strip():
            self.meat = 0
            return 1
        else:
            return 0


class ClassEntry:
    def __init__(self):
        self.defs = []
        self.attrs = []
        self.classdependencytuples = []
        self.classesinheritsfrom = []
        self.ismodulenotrealclass = 0

    def FindAttribute(self, attrname):
        """
        Return
           boolean hit, index pos
        """
        for attrobj in self.attrs:
            if attrname == attrobj.attrname:
                return 1, attrobj
        return 0, None

    def AddAttribute(self, attrname, attrtype):
        """
        If the new info is different to the old, and there is more info
        in it, then replace the old entry.
        e.g. oldattrtype may be ['normal'
             and new may be     ['normal', 'many']
        """
        haveEncounteredAttrBefore, attrobj = self.FindAttribute(attrname)
        if not haveEncounteredAttrBefore:
            self.attrs.append(Attribute(attrname, attrtype))
        else:
            # See if there is more info to add re this attr.
            if len(attrobj.attrtype) < len(attrtype):
                attrobj.attrtype = attrtype  # Update it.

        # OLD CODE
        # if not self.FindAttribute(attrname):
        #    self.attrs.append(Attribute(attrname, attrtype))


class Attribute:
    def __init__(self, attrname, attrtype="normal"):
        self.attrname = attrname
        self.attrtype = attrtype


class HandleClasses(AndyBasicParseEngine):
    def __init__(self):
        AndyBasicParseEngine.__init__(self)
        self.currclasslist = []
        self._currclass = None
        self.nexttokenisclass = 0
        self.classlist = {}
        self.modulemethods = []
        self.optionModuleAsClass = 0
        self.inbetweenClassAndFirstDef = 0

    def On_deindent(self):
        if self.currclassindentlevel and self.indentlevel <= self.currclassindentlevel:
            ##            print 'popping class', self.currclass, 'from', self.currclasslist
            self.PopCurrClass()

    ##        print
    ##        print 'deindent!!', self.indentlevel, 'class indentlevel =', self.currclassindentlevel

    def _DeriveNestedClassName(self, currclass):
        if not self.currclasslist:
            return currclass
        else:
            classname, indentlevel = self.currclasslist[-1]
            return (
                classname + "_" + currclass
            )  # Cannot use :: since java doesn't like this name, nor does the file system.

    def PushCurrClass(self, currclass):
        # print 'pushing currclass', currclass, 'self.currclasslist', self.currclasslist
        currclass = self._DeriveNestedClassName(currclass)
        self.currclasslist.append((currclass, self.indentlevel))
        # print 'result of pushing = ', self.currclasslist

    def PopCurrClass(self):
        # __import__("traceback").print_stack(limit=6)
        self.currclasslist.pop()

    def GetCurrClassIndentLevel(self):
        if not self.currclasslist:
            return None
        currclassandindentlevel = self.currclasslist[-1]
        return currclassandindentlevel[1]

    def GetCurrClass(self):
        if not self.currclasslist:
            return None
        currclassandindentlevel = self.currclasslist[-1]
        return currclassandindentlevel[0]

    currclass = property(GetCurrClass)

    currclassindentlevel = property(GetCurrClassIndentLevel)

    def _JustThenGotclass(self):
        self.PushCurrClass(self.token)
        self.nexttokenisclass = 0
        if self.currclass not in self.classlist:
            self.classlist[self.currclass] = ClassEntry()
        # print 'class', self.currclass
        self.inbetweenClassAndFirstDef = 1

    def On_newline(self):
        pass

    def On_meat(self):
        if self.token == "class":
            ##            print 'meat found class', self.token
            self.nexttokenisclass = 1
        elif self.nexttokenisclass:
            ##            print 'meat found class name ', self.token
            self._JustThenGotclass()


class HandleInheritedClasses(HandleClasses):
    def __init__(self):
        HandleClasses.__init__(self)
        self._ClearwaitingInheriteClasses()

    def _JustThenGotclass(self):
        HandleClasses._JustThenGotclass(self)
        self.currsuperclass = ""
        self.nexttokenisBracketOpenOrColon = 1

    def _ClearwaitingInheriteClasses(self):
        self.nexttokenisBracketOpenOrColon = 0
        self.nexttokenisSuperclass = 0
        self.nexttokenisComma = 0

    def On_newline(self):
        self._ClearwaitingInheriteClasses()

    def On_meat(self):
        HandleClasses.On_meat(self)
        if self.nexttokenisBracketOpenOrColon and self.token == "(":
            assert (
                self.tokentype == token.OP
            )  # unecessary, just practicing refering to tokens via names not numbers
            self.nexttokenisBracketOpen = 0
            self.nexttokenisSuperclass = 1

        elif self.nexttokenisBracketOpenOrColon and self.token == ":":
            self._ClearwaitingInheriteClasses()

        elif self.nexttokenisSuperclass and self.token == ")":
            self._ClearwaitingInheriteClasses()

        elif self.nexttokenisSuperclass:
            self.currsuperclass += self.token
            if self.token == "." or self.nexttoken == ".":
                # print 'processing multi part superclass detected!', self.token, self.nexttoken
                self.nexttokenisSuperclass = 1
            else:
                self.nexttokenisSuperclass = 0
                self.nexttokenisComma = 1
                self.classlist[self.currclass].classesinheritsfrom.append(
                    self.currsuperclass
                )

        elif self.nexttokenisComma and self.token == ",":
            self.nexttokenisSuperclass = 1
            self.nexttokenisComma = 0


class HandleDefs(HandleInheritedClasses):
    def __init__(self):
        HandleInheritedClasses.__init__(self)
        self.currdef = None
        self.nexttokenisdef = 0

    def _Gotdef(self):
        self.currdef = self.token
        self.nexttokenisdef = 0
        # print 'ADDING    def', self.currdef, 'to', self.currclass
        ##        if self.currclass and self.indentlevel == 1:
        if self.currclass:
            self.classlist[self.currclass].defs.append(self.currdef)
        elif self.optionModuleAsClass and self.indentlevel == 0:
            assert self.moduleasclass
            assert self.classlist[self.moduleasclass]
            self.classlist[self.moduleasclass].defs.append(self.currdef)
        else:
            self.modulemethods.append(self.currdef)
        self.inbetweenClassAndFirstDef = 0

    def On_meat(self):
        HandleInheritedClasses.On_meat(self)

        ##        if self.token == 'def' and self.indentlevel == 1:
        if self.token == "def":
            ##            print 'DEF FOUND AT LEVEL', self.indentlevel
            self.nexttokenisdef = 1
        elif self.nexttokenisdef:
            self._Gotdef()


##        self.meat = 1


class HandleClassAttributes(HandleDefs):
    def __init__(self):
        HandleDefs.__init__(self)
        self.attrslist = []
        self._Clearwaiting()

    def On_newline(self):
        HandleInheritedClasses.On_newline(self)
        self._Clearwaiting()

    def _Clearwaiting(self):
        self.waitingfordot = 0
        self.waitingforsubsequentdot = 0
        self.waitingforvarname = 0
        self.waitingforequalsymbol = 0
        self.currvarname = None
        self.lastcurrvarname = None
        self.waitforappendopenbracket = 0
        self.nextvarnameisstatic = 0
        self.nextvarnameismany = 0

    def JustGotASelfAttr(self, selfattrname):
        pass

    def On_meat(self):
        HandleDefs.On_meat(self)

        if self.isfreshline and self.token == "self" and self.nexttoken == ".":
            self.waitingfordot = 1

        elif self.waitingfordot and self.token == ".":
            self.waitingfordot = 0
            self.waitingforvarname = 1

        elif self.waitingforvarname:
            # We now have the possible class attribute name. :-)
            self.waitingforvarname = 0
            self.currvarname = self.token
            """
            At this point we have the x in the expression   self.x

            A. We could find   self.x =             in which case we have a valid class attribute.
            B. We could find   self.x.append(       in which case we have a valid class attribute list/vector.
            C. We could find   self.__class__.x =   in which case we have a valid STATIC class attribute.

            D. We could find   self.x.y =           in which case we skip.
            E. We could find   self.x.y.append(     in which case we skip.
            F. We could find   self.x.y.Blah(       in which case we skip.

            G. We could find   self.numberOfFlags = read16(fp)    - skip cos read16 is a module function.
            """
            if self.nexttoken == "=":
                self.waitingforequalsymbol = 1  # Case A
            elif self.nexttoken == ".":
                self.waitingforsubsequentdot = 1  # Cases B,C, D,E,F  pending

        elif self.waitingforsubsequentdot and self.token == ".":
            self.waitingfordot = 0
            self.waitingforsubsequentdot = 0
            self.waitingforequalsymbol = 0
            if self.nexttoken.lower() in ("append", "add", "insert"):  # Case B
                # keep the class attribute name we have, wait till bracket
                self.waitforappendopenbracket = 1
            elif self.currvarname in ("__class__",):  # Case C
                self.currvarname = None
                self.waitingforvarname = 1
                self.nextvarnameisstatic = 1
            else:
                # Skip cases D, E, F
                self._Clearwaiting()

        elif self.waitforappendopenbracket and self.token == "(":
            self.waitforappendopenbracket = 0
            self.nextvarnameismany = 1
            self._AddAttribute()
            self._Clearwaiting()

        elif self.waitingforequalsymbol and self.token == "=":
            self.waitingforequalsymbol = 0
            self._AddAttribute()
            self._Clearwaiting()

    def _AddAttribute(self):
        classentry = self.classlist[self.currclass]
        if self.nextvarnameisstatic:
            attrtype = ["static"]
        else:
            attrtype = ["normal"]

        if self.nextvarnameismany:
            attrtype.append("many")

        classentry.AddAttribute(self.currvarname, attrtype)
        # print '       ATTR  ', self.currvarname
        self.JustGotASelfAttr(self.currvarname)


class HandleComposites(HandleClassAttributes):
    def __init__(self):
        HandleClassAttributes.__init__(self)
        self._ClearwaitingOnComposites()
        self.dummy = ClassEntry()
        self.dummy2 = [()]

    def JustGotASelfAttr(self, selfattrname):
        assert selfattrname != "self"
        self.lastselfattrname = selfattrname
        self.waitingforclassname = 1
        self.waitingforOpenBracket = 0
        self.possibleclassname = None
        self.dontdoanythingnow = 1

    def _ClearwaitingOnComposites(self):
        self.lastselfattrname = None
        self.waitingforclassname = 0
        self.possibleclassname = None
        self.waitingforOpenBracket = 0
        self.dontdoanythingnow = 0

    def On_newline(self):
        HandleClassAttributes.On_newline(self)
        self._ClearwaitingOnComposites()

    def On_meat(self):
        self.dontdoanythingnow = 0
        HandleClassAttributes.On_meat(self)

        # At this point we may have had a "self.blah = " encountered, and blah is saved in self.lastselfattrname

        if self.dontdoanythingnow:
            pass

        elif (
            self.waitingforclassname
            and self.token not in ("(", "[")
            and self.token not in pythonbuiltinfunctions
            and self.tokentype not in (token.NUMBER, token.STRING)
            and self.token not in self.modulemethods
        ):
            self.possibleclassname = self.token
            self.waitingforclassname = 0
            self.waitingforOpenBracket = 1

        elif self.waitingforOpenBracket and self.token == "(":
            self.waitingforclassname = 0
            self.waitingforOpenBracket = 0

            dependency = (self.lastselfattrname, self.possibleclassname)
            self.classlist[self.currclass].classdependencytuples.append(dependency)
            # print '*** dependency - created instance of', self.possibleclassname, 'assigned to', self.lastselfattrname

        elif self.waitingforOpenBracket and self.token == ")":
            """
            New - we haven't got a class being created but instead have a variable.
            Note that the above code detects
              self.flag.append(Flag())   # notice instance creation inside append
            but the following code detects
              self.flag.append(flag)   # and assumes flag variable is an instance of Flag class
            """
            # we don't have class being created but have a variable name instead
            variablename = self.possibleclassname

            # try to find a class with the same name.
            correspondingClassName = variablename[0].upper() + variablename[1:]  # HACK
            # print 'correspondingClassName', correspondingClassName

            dependency = (self.lastselfattrname, correspondingClassName)
            self.classlist[self.currclass].classdependencytuples.append(dependency)

        else:
            self._ClearwaitingOnComposites()


class HandleClassStaticAttrs(HandleComposites):
    def __init__(self):
        HandleComposites.__init__(self)
        self.__Clearwaiting()

    def __Clearwaiting(self):
        self.__waitingforequalsymbol = 0
        self.__staticattrname = ""

    def On_meat(self):
        HandleComposites.On_meat(self)

        if (
            self.isfreshline
            and self.currclass
            and self.inbetweenClassAndFirstDef
            and self.tokentype == 1
            and self.indentlevel != 0
            and self.nexttoken == "="
        ):
            self.__waitingforequalsymbol = 1
            self.__staticattrname = self.token

        elif self.__waitingforequalsymbol and self.token == "=":
            self.__waitingforequalsymbol = 0
            # print 'have static level attr', self.__staticattrname
            self.__AddAttrModuleLevel()
            self.__Clearwaiting()

    def __AddAttrModuleLevel(self):
        # Should re-use the logic in HandleClassAttributes for both parsing
        # (getting more info on multiplicity but not static - cos static not relevant?) and
        # also should be able to reuse most of _AddAttr()
        #
        classentry = self.classlist[self.currclass]
        attrtype = ["static"]

        classentry.AddAttribute(self.__staticattrname, attrtype)
        # print '       STATIC ATTR  ', self.__staticattrname


class HandleModuleLevelDefsAndAttrs(HandleClassStaticAttrs):
    def __init__(self):
        HandleClassStaticAttrs.__init__(self)
        self.moduleasclass = ""
        self.__Clearwaiting()

    def __Clearwaiting(self):
        self.waitingforequalsymbolformoduleattr = 0
        self.modulelevelattrname = ""

    def Parse(self, file):
        self.moduleasclass = "Module_" + os.path.splitext(os.path.basename(file))[0]
        if self.optionModuleAsClass:
            self.classlist[self.moduleasclass] = ClassEntry()
            self.classlist[self.moduleasclass].ismodulenotrealclass = 1

        HandleComposites.Parse(self, file)

    def On_meat(self):
        HandleClassStaticAttrs.On_meat(self)

        if (
            self.isfreshline
            and self.tokentype == 1
            and self.indentlevel == 0
            and self.nexttoken == "="
        ):
            self.waitingforequalsymbolformoduleattr = 1
            self.modulelevelattrname = self.token

        elif self.waitingforequalsymbolformoduleattr and self.token == "=":
            self.waitingforequalsymbolformoduleattr = 0
            # print 'have module level attr', self.modulelevelattrname
            self._AddAttrModuleLevel()
            self.__Clearwaiting()

    def On_newline(self):
        HandleClassStaticAttrs.On_newline(self)
        self.__Clearwaiting()

    def _AddAttrModuleLevel(self):
        if not self.optionModuleAsClass:
            return

        # Should re-use the logic in HandleClassAttributes for both parsing
        # (getting more info on multiplicity but not static - cos static not relevant?) and
        # also should be able to reuse most of _AddAttr()
        #
        classentry = self.classlist[self.moduleasclass]
        attrtype = ["normal"]

        ##        if self.nextvarnameisstatic:
        ##            attrtype = ['static']
        ##        else:
        ##            attrtype = ['normal']
        ##
        ##        if self.nextvarnameismany:
        ##            attrtype.append('many')

        classentry.AddAttribute(self.modulelevelattrname, attrtype)
        # print '       ATTR  ', self.currvarname
        # self.JustGotASelfAttr(self.currvarname)


class PySourceAsText(HandleModuleLevelDefsAndAttrs):
    def __init__(self):
        HandleModuleLevelDefsAndAttrs.__init__(self)
        self.listcompositesatend = 0
        self.embedcompositeswithattributelist = 1
        self.result = ""
        self.aclass = None
        self.classentry = None
        self.staticmessage = ""
        self.manymessage = ""
        self.verbose = 0

    def GetCompositeClassesForAttr(self, classname, classentry):
        resultlist = []
        for dependencytuple in classentry.classdependencytuples:
            if dependencytuple[0] == classname:
                resultlist.append(dependencytuple[1])
        return resultlist

    def _GetCompositeCreatedClassesFor(self, classname):
        return self.GetCompositeClassesForAttr(classname, self.classentry)

    def _DumpAttribute(self, attrobj):
        compositescreated = self._GetCompositeCreatedClassesFor(attrobj.attrname)
        if compositescreated and self.embedcompositeswithattributelist:
            self.result += "%s %s <@>----> %s" % (
                attrobj.attrname,
                self.staticmessage,
                str(compositescreated),
            )
        else:
            self.result += "%s %s" % (attrobj.attrname, self.staticmessage)
        self.result += self.manymessage
        self.result += "\n"

    def _DumpCompositeExtraFooter(self):
        if self.classentry.classdependencytuples and self.listcompositesatend:
            for dependencytuple in self.classentry.classdependencytuples:
                self.result += "%s <*>---> %s\n" % dependencytuple
            self.result += "-" * 20 + "\n"

    def _DumpClassNameAndGeneralisations(self):
        self._Line()
        if self.classentry.ismodulenotrealclass:
            self.result += "%s  (file)\n" % (self.aclass,)
        else:
            self.result += "%s  --------|> %s\n" % (
                self.aclass,
                self.classentry.classesinheritsfrom,
            )
        self._Line()

    def _DumpAttributes(self):
        for attrobj in self.classentry.attrs:
            self.staticmessage = ""
            self.manymessage = ""
            if "static" in attrobj.attrtype:
                self.staticmessage = " static"
            if "many" in attrobj.attrtype:
                self.manymessage = " 1..*"
            self._DumpAttribute(attrobj)

    def _DumpMethods(self):
        for adef in self.classentry.defs:
            self.result += adef + "\n"

    def _Line(self):
        self.result += "-" * 20 + "\n"

    def _DumpClassHeader(self):
        self.result += "\n"

    def _DumpClassFooter(self):
        self.result += "\n"
        self.result += "\n"

    def _DumpModuleMethods(self):
        if self.modulemethods:
            self.result += "  ModuleMethods = %s\n" % repr(self.modulemethods)

    ##        self.result += '\n'

    def __str__(self):
        self.result = ""
        self._DumpClassHeader()
        self._DumpModuleMethods()

        optionAlphabetic = 0
        classnames = list(self.classlist.keys())
        if optionAlphabetic:
            classnames.sort()
        else:

            def cmpfunc(a, b):
                if a.find("Module_") != -1:
                    return -1
                else:
                    if a < b:
                        return -1
                    elif a == b:
                        return 0
                    else:
                        return 1

            classnames.sort(key=cmp_to_key(cmpfunc))
        for self.aclass in classnames:
            self.classentry = self.classlist[self.aclass]

            ##        for self.aclass, self.classentry in self.classlist.items():
            self._DumpClassNameAndGeneralisations()
            self._DumpAttributes()
            self._Line()
            self._DumpMethods()
            self._Line()
            self._DumpCompositeExtraFooter()
            self._DumpClassFooter()
        return self.result


class PySourceAsJava(PySourceAsText):
    def __init__(self, outdir=None):
        PySourceAsText.__init__(self)
        self.outdir = outdir
        self.fp = None

    def _DumpClassFooter(self):
        self.result += "}\n"

        if self.fp:
            self.fp.write(self.result)
            self.fp.close()
            self.fp = None
            self.result = ""

    def _DumpModuleMethods(self):
        self.result += "/*\n"
        PySourceAsText._DumpModuleMethods(self)
        self.result += "*/\n"

    def _OpenNextFile(self):
        filepath = "%s\\%s.java" % (self.outdir, self.aclass)
        self.fp = open(filepath, "w")

    def _NiceNameToPreventCompilerErrors(self, attrname):
        """
        Prevent compiler errors on the java side by checking and modifying attribute name
        """
        # only emit the rhs of a multi part name e.g. undo.UndoItem will appear only as UndoItem
        if attrname.find(".") != -1:
            attrname = attrname.split(".")[-1]  # take the last
        # Prevent compiler errors on the java side by avoiding the generating of java keywords as attribute names
        if attrname in javakeywords:
            attrname = "_" + attrname
        return attrname

    def _DumpAttribute(self, attrobj):
        compositescreated = self._GetCompositeCreatedClassesFor(attrobj.attrname)
        if compositescreated:
            compositecreated = compositescreated[0]
        else:
            compositecreated = None

        # Extra processing on the attribute name, to avoid java compiler errors
        attrname = self._NiceNameToPreventCompilerErrors(attrobj.attrname)

        if compositecreated and self.embedcompositeswithattributelist:
            self.result += "    public %s %s %s = new %s();\n" % (
                self.staticmessage,
                compositecreated,
                attrname,
                compositecreated,
            )
        else:
            ##            self.result +=  "    public %s void %s;\n" % (self.staticmessage, attrobj.attrname)
            ##            self.result +=  "    public %s int %s;\n" % (self.staticmessage, attrname)
            self.result += "    public %s variant %s;\n" % (
                self.staticmessage,
                attrname,
            )

        """
        import java.util.Vector;

        private java.util.Vector lnkClass4;

        private Vector lnkClass4;
        """

    def _DumpCompositeExtraFooter(self):
        pass

    def _DumpClassNameAndGeneralisations(self):
        if self.verbose:
            print("  Generating Java class", self.aclass)
        self._OpenNextFile()

        self.result += "// Generated by PyNSource http://www.atug.com/andypatterns/pynsource.htm \n\n"

        ##        self.result +=  "import javax.swing.Icon;     // Not needed, just testing pyNSource's ability to generate import statements.\n\n"    # NEW package support!

        self.result += "public class %s " % self.aclass
        if self.classentry.classesinheritsfrom:
            self.result += "extends %s " % self._NiceNameToPreventCompilerErrors(
                self.classentry.classesinheritsfrom[0]
            )
        self.result += "{\n"

    def _DumpMethods(self):
        for adef in self.classentry.defs:
            self.result += "    public void %s() {\n    }\n" % adef

    def _Line(self):
        pass


def unique(s):
    """ Return a list of the elements in list s in arbitrary order, but without duplicates """
    n = len(s)
    if n == 0:
        return []
    u = {}
    try:
        for x in s:
            u[x] = 1
    except TypeError:
        del u  # move onto the next record
    else:
        return list(u.keys())

    raise KeyError("uniqueness algorithm failed .. type more of it in please")


class PySourceAsDelphi(PySourceAsText):
    """
    Example Delphi source file:

      unit test000123;

      interface

      uses
        SysUtils, Windows, Messages, Classes, Graphics, Controls,
        Forms, Dialogs;

      type
        TDefault1 = class (TObject)
        private
          field0012: Variant;
        public
          class var field0123434: Variant;
          procedure Member1;
          class procedure Member2;
        end;


      procedure Register;

      implementation

      procedure Register;
      begin
      end;

      {
      ********************************** TDefault1 ***********************************
      }
      procedure TDefault1.Member1;
      begin
      end;

      class procedure TDefault1.Member2;
      begin
      end;


      end.

    """

    def __init__(self, outdir=None):
        PySourceAsText.__init__(self)
        self.outdir = outdir
        self.fp = None

    def _DumpClassFooter(self):
        self.result += "\n\n"

        self.result += "implementation\n\n"

        self.DumpImplementationMethods()

        self.result += "\nend.\n\n"

        if self.fp:
            self.fp.write(self.result)
            self.fp.close()
            self.fp = None
            self.result = ""

    def _DumpModuleMethods(self):
        self.result += "(*\n"
        PySourceAsText._DumpModuleMethods(self)
        self.result += "*)\n\n"

    def _OpenNextFile(self):
        filepath = "%s\\unit_%s.pas" % (self.outdir, self.aclass)
        self.fp = open(filepath, "w")

    def _NiceNameToPreventCompilerErrors(self, attrname):
        """
        Prevent compiler errors on the java side by checking and modifying attribute name
        """
        # only emit the rhs of a multi part name e.g. undo.UndoItem will appear only as UndoItem
        if attrname.find(".") != -1:
            attrname = attrname.split(".")[-1]  # take the last

        # Prevent compiler errors on the Delphi side by avoiding the generating of delphi keywords as attribute names
        if (
            attrname.lower() in delphikeywords
        ):  # delphi is case insensitive, so convert everything to lowercase for comparisons
            attrname = "_" + attrname

        return attrname

    def _DumpAttribute(self, attrobj):
        """
        Figure out what type the attribute is only in those cases where
        we are later going to assign to these variables using .Create() in the constructor.
        The rest we make Variants.
        """
        compositescreated = self._GetCompositeCreatedClassesFor(attrobj.attrname)
        if compositescreated:
            compositecreated = compositescreated[0]
        else:
            compositecreated = None

        # Extra processing on the attribute name, to avoid delphi compiler errors
        attrname = self._NiceNameToPreventCompilerErrors(attrobj.attrname)

        self.result += "    "
        if self.staticmessage:
            self.result += "class var"

        if compositecreated:
            vartype = compositecreated
        else:
            vartype = "Variant"
        self.result += "%s : %s;\n" % (attrname, vartype)

        # generate more complex stuff in the implementation section...

    ##        if compositecreated and self.embedcompositeswithattributelist:
    ##            self.result +=  "    public %s %s %s = new %s();\n" % (self.staticmessage, compositecreated, attrname, compositecreated)
    ##        else:
    ##            self.result +=  "%s : Variant;\n"%attrname

    def _DumpCompositeExtraFooter(self):
        pass

    def _DumpClassNameAndGeneralisations(self):
        if self.verbose:
            print("  Generating Delphi class", self.aclass)
        self._OpenNextFile()

        self.result += "// Generated by PyNSource http://www.atug.com/andypatterns/pynsource.htm \n\n"

        self.result += "unit unit_%s;\n\n" % self.aclass
        self.result += "interface\n\n"

        uses = unique(self.GetUses())
        if uses:
            self.result += "uses\n    "
            self.result += ", ".join(uses)
            self.result += ";\n\n"

        self.result += "type\n\n"
        self.result += "%s = class" % self.aclass
        if self.classentry.classesinheritsfrom:
            self.result += "(%s)" % self._NiceNameToPreventCompilerErrors(
                self.classentry.classesinheritsfrom[0]
            )
        self.result += "\n"
        self.result += "public\n"

    def _DumpMethods(self):
        if self.classentry.attrs:  # if there were any atributes...
            self.result += (
                "\n"
            )  # a little bit of a separator between attributes and methods.

        for adef in self.classentry.defs:
            if adef == "__init__":
                self.result += "    constructor Create;\n"
            else:
                ##                self.result +=  "    function %s(): void; virtual;\n" % adef
                self.result += "    procedure %s(); virtual;\n" % adef

        self.result += "end;\n"  # end of class

    def DumpImplementationMethods(self):
        for adef in self.classentry.defs:
            if adef == "__init__":
                self.result += (
                    "constructor %s.Create;\n" % self.aclass
                )  # replace __init__ with the word 'Create'
            else:
                ##                self.result +=  "function %s.%s(): void;\n" % (self.aclass, adef)
                self.result += "procedure %s.%s();\n" % (self.aclass, adef)
            self.result += "begin\n"
            if adef == "__init__":
                self.CreateCompositeAttributeClassCreationAndAssignmentInImplementation()
            self.result += "end;\n\n"

    def CreateCompositeAttributeClassCreationAndAssignmentInImplementation(self):
        # Only do those attributes that are composite and need to create an instance of something
        for attrobj in self.classentry.attrs:
            compositescreated = self._GetCompositeCreatedClassesFor(attrobj.attrname)
            if (
                compositescreated and self.embedcompositeswithattributelist
            ):  # latter variable always seems to be true! Never reset!?
                compositecreated = compositescreated[0]
                self.result += "    %s := %s.Create();\n" % (
                    attrobj.attrname,
                    compositecreated,
                )

    def GetUses(self):
        result = []
        for attrobj in self.classentry.attrs:
            compositescreated = self._GetCompositeCreatedClassesFor(attrobj.attrname)
            if (
                compositescreated and self.embedcompositeswithattributelist
            ):  # latter variable always seems to be true! Never reset!?
                compositecreated = compositescreated[0]
                result.append(compositecreated)

        # Also use any inherited calss modules.
        if self.classentry.classesinheritsfrom:
            result.append(
                self._NiceNameToPreventCompilerErrors(
                    self.classentry.classesinheritsfrom[0]
                )
            )

        return ["unit_" + u for u in result]

    def _Line(self):
        pass


class PythonToJava:
    def __init__(self, directories, treatmoduleasclass=0, verbose=0):
        self.directories = directories
        self.optionModuleAsClass = treatmoduleasclass
        self.verbose = verbose

    def _GenerateAuxilliaryClasses(self):
        classestocreate = (
            "variant",
            "unittest",
            "list",
            "object",
            "dict",
        )  # should add more classes and add them to a jar file to avoid namespace pollution.
        for aclass in classestocreate:
            fp = open(os.path.join(self.outpath, aclass + ".java"), "w")
            fp.write(self.GenerateSourceFileForAuxClass(aclass))
            fp.close()

    def GenerateSourceFileForAuxClass(self, aclass):
        return "\npublic class %s {\n}\n" % aclass

    def ExportTo(self, outpath):
        self.outpath = outpath

        self._GenerateAuxilliaryClasses()

        for directory in self.directories:
            if "*" in directory or "." in directory:
                filepath = directory
            else:
                filepath = os.path.join(directory, "*.py")
            if self.verbose:
                print("Processing directory", filepath)
            globbed = glob.glob(filepath)
            # print 'Java globbed is', globbed
            for f in globbed:
                self._Process(f)

    def _Process(self, filepath):
        if self.verbose:
            padding = " "
        else:
            padding = ""
        thefile = os.path.basename(filepath)
        if thefile[0] == "_":
            print("  ", "Skipped", thefile, "cos begins with underscore.")
            return
        print("%sProcessing %s..." % (padding, thefile))
        p = self._CreateParser()
        p.Parse(filepath)
        str(p)  # triggers the output.

    def _CreateParser(self):
        p = PySourceAsJava(self.outpath)
        p.optionModuleAsClass = self.optionModuleAsClass
        p.verbose = self.verbose
        return p


class PythonToDelphi(PythonToJava):
    def _GenerateAuxilliaryJavaClasses(self):
        pass

    def _CreateParser(self):
        p = PySourceAsDelphi(self.outpath)
        p.optionModuleAsClass = self.optionModuleAsClass
        p.verbose = self.verbose
        return p

    def _GenerateAuxilliaryClasses(self):
        # Delphi version omits the class 'object' and 'variant' since these already are pre-defined in Delphi.
        classestocreate = ("unittest", "list", "dict")  # should add more classes
        for aclass in classestocreate:
            fp = open(os.path.join(self.outpath, "unit_" + aclass + ".pas"), "w")
            fp.write(self.GenerateSourceFileForAuxClass(aclass))
            fp.close()

    def GenerateSourceFileForAuxClass(self, aclass):
        template = """
unit unit_%s;

interface

type

    %s = class
    public
    end;

implementation

end.
       """
        return template % (aclass, aclass)


def run():
    # FILE = 'testmodule01.py'
    # FILE = 'C:\\Documents and Settings\\Administrator\\Desktop\\try\\PyutXmlV6.py'
    # FILE = 'testmodule02.py'
    # FILE = 'andyparse9.py'
    FILE = "c:\\cc\devel\storyline\\battle.py"
    # FILE = "c:\\cc\devel\storyline\\battleresult.py"
    # FILE = "c:\\cc\devel\storyline\\battlestabs.py"

    p = PySourceAsText()
    # p = JavaDumper("c:\\try")

    p.Parse(FILE)

    print("*" * 20, "parsing", FILE, "*" * 20)
    print(p)
    print("Done.")


if __name__ == "__main__":
    # run()
    import sys, glob, getopt

    SIMPLE = 0
    globbed = []

    optionVerbose = 0
    optionModuleAsClass = 0
    optionExportToJava = 0
    optionExportToDelphi = 0
    optionExportTo_outdir = ""

    if SIMPLE:
        params = sys.argv[1]
        globbed = glob.glob(params)
    else:
        listofoptionvaluepairs, params = getopt.getopt(sys.argv[1:], "mvj:d:")
        print(listofoptionvaluepairs, params)

        def EnsurePathExists(outdir, outlanguagemsg):
            assert outdir, "Need to specify output folder for %s output - got %s." % (
                outlanguagemsg,
                outdir,
            )
            if not os.path.exists(outdir):
                raise RuntimeError(
                    "Output directory %s for %s file output does not exist."
                    % (outdir, outlanguagemsg)
                )

        for optionvaluepair in listofoptionvaluepairs:
            if "-m" == optionvaluepair[0]:
                optionModuleAsClass = 1
            if "-v" == optionvaluepair[0]:
                optionVerbose = 1
            if optionvaluepair[0] in ("-j", "-d"):
                if optionvaluepair[0] == "-j":
                    optionExportToJava = 1
                    language = "Java"
                else:
                    optionExportToDelphi = 1
                    language = "Delphi"
                optionExportTo_outdir = optionvaluepair[1]
                EnsurePathExists(optionExportTo_outdir, language)

        for param in params:
            files = glob.glob(param)
            globbed += files

    if globbed:
        if optionExportToJava or optionExportToDelphi:
            if optionExportToJava:
                u = PythonToJava(
                    globbed,
                    treatmoduleasclass=optionModuleAsClass,
                    verbose=optionVerbose,
                )
            else:
                u = PythonToDelphi(
                    globbed,
                    treatmoduleasclass=optionModuleAsClass,
                    verbose=optionVerbose,
                )
            u.ExportTo(optionExportTo_outdir)
        else:
            p = PySourceAsText()
            p.optionModuleAsClass = optionModuleAsClass
            p.verbose = optionVerbose
            for f in globbed:
                p.Parse(f)
            print(p)
    else:
        print(
            """Usage: pynsource -v -m -j outdir sourcedirorpythonfiles...

-j generate java files, specify output folder for java files
-v verbose
-m create psuedo class for each module,
   module attrs/defs etc treated as class attrs/defs

BASIC EXAMPLES
e.g. pynsource Test/testmodule01.py
e.g. pynsource -m Test/testmodule03.py
JAVA EXAMPLES
e.g. pynsource -j c:/try c:/try
e.g. pynsource -v -m -j c:/try c:/try
e.g. pynsource -v -m -j c:/try c:/try/s*.py
e.g. pynsource -j c:/try c:/try/s*.py Tests/u*.py
e.g. pynsource -v -m -j c:/try c:/try/s*.py Tests/u*.py c:\cc\Devel\Client\w*.py
DELPHI EXAMPLE
e.g. pynsource -d c:/delphiouputdir c:/pythoninputdir/*.py
"""
        )
