PyNSource
http://www.atug.com/andypatterns/pynsource.htm

(c) 2003, 2004, 2005, 2006 Andy Bulka
License: Free to use as long as acknowledgement is made in source code.
abulka@netspace.net.au
http://www.atug.com/andypatterns


Version 1.4c
- Fixed some parsing bugs.
- Parsing now more correct under python 2.4 (python changed token.py !!)
- Unit tests now all pass


Version 1.4b
- Added wxpython 2.5 compatibility (thanks Thomas Margraf!)


Version 1.4a

GUI changes:
- Right Click on a node to delete it.
- Run Layout anytime from menu.
- Left click on background will deselect any selected shapes

Version 1.4

- Fixed indentation error causing more output than normal in text ouput
- Module level functions not treated as classes any more
- Smarter detection of composition relationships, as long as classname 
  and variable name are the same (ignoring case) then PyNSource will detect e.g.

  class Cat:
    pass

  class A:
    def __init__(self, cat):
      self.cats.append(Cat())  # always has worked, composition detected.
      self.cats.append(cat)    # new 1.4 feature, composition detected here too.


Version 1.3a

A reverse engineering tool for Python source code
 - UML diagram models that you can layout, arrange and print out.
 - UML text diagrams, which you can paste into your source code for documentation purposes.
 - Java or Delphi code (which can be subsequently imported into more sophisticated UML 
   modelling tools, like Enterprise Architect or ESS-Model (free).)

Features
 - Resilient: doesn't import the python files, thus will never get "stuck" when syntax is wrong. 
 - Fast
 - Recognises inheritance and composition  relationships
 - Detects the cardinality of associations e.g. one to one or 1..*  etc
 - Optionally treat modules as classes - creating a pseudo class for each 
   module - module variables and functions are  treated as attributes and methods of a class
 - Has been developed using unit tests (supplied) so that you can trust it just that little bit more ;-)


GUI FRONT END
-------------

The PyNSource Gui is started in two ways:
   * By running the standalone pynsourceGui.exe via the shortcut created by the standalone installer.   or
   * By running pynsourceGui.py ( you need wxpython installed. See http://www.wxpython.org )
     e.g. \Python22\python.exe  \Python22\Lib\site-packages\pynsource\pyNsourceGui.py

The PyNSource command line tool is pynsource.py

Command line Usage
------------------

 pynsource -v -m [-j outdir] sourceDirOrListOfPythonFiles...   

   no options - generate Ascii UML
-j generate java files, specify output folder for java files
-d generate pascal files, specify output folder for pascal files
-v verbose
-m create psuedo class for each module,
   module attrs/defs etc treated as class attrs/defs

Examples

e.g.
   \python22\python.exe  \Python22\Lib\site-packages\pynsource\pynsource.py  -d c:\delphiouputdir c:\pythoninputdir\*.py

The above line will scan all the files in c:\pythoninputdir and generate 
a bunch of delphi files in the folder c:\delphiouputdir

BASIC ASCII UML OUTPUT from PYTHON - EXAMPLES
e.g. pynsource Test/testmodule01.py
e.g. pynsource -m Test/testmodule03.py

GENERATE JAVA FILES from PYTHON - EXAMPLES
e.g. pynsource -j c:/try c:/try
e.g. pynsource -v -m -j c:/try c:/try
e.g. pynsource -v -m -j c:/try c:/try/s*.py
e.g. pynsource -j c:/try c:/try/s*.py Tests/u*.py
e.g. pynsource -v -m -j c:/try c:/try/s*.py Tests/u*.py c:\cc\Devel\Client\w*.py

GENERATE DELPHI  FILES from PYTHON - EXAMPLE
e.g. pynsource -d c:/delphiouputdir c:/pythoninputdir/*.py



see http://www.atug.com/andypatterns/pynsource.htm for more documentation.

Bugs to abulka@netspace.net.au 
