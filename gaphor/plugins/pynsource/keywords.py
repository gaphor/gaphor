"""
Definitions of python, java and delphi keywords
so that pynsource can skip these and not treat them like you are
creating an instance of a locally defined class.
"""

pythonbuiltinfunctions_txt = """
ArithmeticError
AssertionError
AttributeError
DeprecationWarning
EOFError
EnvironmentError
Exception
FloatingPointError
FutureWarning
IOError
ImportError
IndentationError
IndexError
KeyError
KeyboardInterrupt
LookupError
MemoryError
NameError
NotImplementedError
OSError
OverflowError
OverflowWarning
PendingDeprecationWarning
ReferenceError
RuntimeError
RuntimeWarning
StandardError
StopIteration
SyntaxError
SyntaxWarning
SystemError
SystemExit
TabError
TypeError
UnboundLocalError
UnicodeError
UserWarning
ValueError
Warning
WindowsError
ZeroDivisionError
Ellipsis
False
None
NotImplemented
True
UnicodeDecodeError
UnicodeEncodeError
UnicodeTranslateError
__debug__
__import__
abs
apply
basestring
bool
buffer
callable
chr
classmethod
cmp
coerce
compile
complex
copyright
credits
delattr
dict
dir
divmod
enumerate
eval
execfile
exit
file
filter
float
getattr
globals
hasattr
hash
help
hex
id
input
int
intern
isinstance
issubclass
iter
len
license
list
locals
long
map
max
min
object
oct
open
ord
pow
property
quit
range
raw_input
reduce
reload
repr
round
setattr
slice
staticmethod
str
sum
super
tuple
type
unichr
unicode
vars
xrange
zip
__base__
__bases__
__basicsize__
__class__
__dict__
__dictoffset__
__doc__
__flags__
__itemsize__
__module__
__mro__
__name__
__self__
__weakrefoffset__
__abs__
__add__
__and__
__call__
__cmp__
__coerce__
__complex__
__contains__
__del__
__delattr__
__delitem__
__delslice__
__div__
__divmod__
__eq__
__float__
__floordiv__
__ge__
__get__
__getattribute__
__getitem__
__getnewargs__
__getslice__
__gt__
__hash__
__hex__
__iadd__
__iand__
__idiv__
__ifloordiv__
__ilshift__
__imod__
__imul__
__init__
__int__
__invert__
__ior__
__ipow__
__irshift__
__isub__
__iter__
__itruediv__
__ixor__
__le__
__len__
__long__
__lshift__
__lt__
__mod__
__mul__
__ne__
__neg__
__new__
__nonzero__
__oct__
__or__
__pos__
__pow__
__radd__
__rand__
__rdiv__
__rdivmod__
__reduce__
__reduce_ex__
__repr__
__rfloordiv__
__rlshift__
__rmod__
__rmul__
__ror__
__rpow__
__rrshift__
__rshift__
__rsub__
__rtruediv__
__rxor__
__setattr__
__setitem__
__setslice__
__str__
__sub__
__subclasses__
__truediv__
__xor__
append
capitalize
center
clear
close
conjugate
copy
count
decode
encode
endswith
expandtabs
extend
fileno
find
flush
fromkeys
get
has_key
index
indices
insert
isalnum
isalpha
isatty
isdecimal
isdigit
islower
isnumeric
isspace
istitle
isupper
items
iteritems
iterkeys
itervalues
join
keys
ljust
lower
lstrip
mro
next
pop
popitem
read
readinto
readline
readlines
remove
replace
reverse
rfind
rindex
rjust
rstrip
seek
setdefault
sort
split
splitlines
startswith
strip
swapcase
tell
title
translate
truncate
update
upper
values
write
writelines
xreadlines
zfill
closed
co_argcount
co_cellvars
co_code
co_consts
co_filename
co_firstlineno
co_flags
co_freevars
co_lnotab
co_name
co_names
co_nlocals
co_stacksize
co_varnames
f_back
f_builtins
f_code
f_exc_traceback
f_exc_type
f_exc_value
f_globals
f_lasti
f_lineno
f_locals
f_restricted
f_trace
func_closure
func_code
func_defaults
func_dict
func_doc
func_globals
func_name
gi_frame
gi_running
im_class
im_func
im_self
imag
mode
name
newlines
real
softspace
start
step
stop
BooleanType
BufferType
BuiltinFunctionType
BuiltinMethodType
ClassType
CodeType
ComplexType
DictProxyType
DictType
DictionaryType
EllipsisType
FileType
FloatType
FrameType
FunctionType
GeneratorType
InstanceType
IntType
LambdaType
ListType
LongType
MethodType
ModuleType
NoneType
NotImplementedType
ObjectType
SliceType
StringType
StringTypes
TracebackType
TupleType
TypeType
UnboundMethodType
UnicodeType
XRangeType
__builtins__
__file__
"""
pythonbuiltinfunctions = pythonbuiltinfunctions_txt.split()

javakeywords_txt =  """
abstract
boolean
break
byte
case
catch
char
class
continue
default
delegate
do
double
else
extends
false
final
finally
float
for
if
implements
import
instanceof
int
interface
long
native
new
null
package
private
protected
public
return
short
static
super
switch
synchronized
this
throw
throws
transient
true
try
void
volatile
while
goto
const
strictfp
"""
javakeywords = javakeywords_txt.split()





delphikeywords_txt =  """
And
Array
As
Begin
Case
Class
Const
Constructor
Destructor
Div
Do
DownTo
Else
End
Except
File
Finally
For
System
Goto
If
Implementation
In
Inherited
Interface
System
Is
Mod
Not
System
Of
On
Or
Packed
System
System
System
Raise
Record
Repeat
Set
Shl
Shr
Then
ThreadVar
To
Try
Type
Unit
Until
Uses
Var
While
With
Xor
"""
delphikeywords = delphikeywords_txt.split()
delphikeywords = [ x.lower() for x in delphikeywords ]  # delphi is case insensitive, so convert everything to lowercase for comparisons

# See Token.py in \python2x\Lib

TOKEN_MEANINGS_FORDOCO_ONLY = """
AMPER = 19
AMPEREQUAL = 42
AT = 50
BACKQUOTE = 25
CIRCUMFLEX = 33
CIRCUMFLEXEQUAL = 44
COLON = 11
COMMA = 12
COMMENT = 53
DEDENT = 6
DOT = 23
DOUBLESLASH = 48
DOUBLESLASHEQUAL = 49
DOUBLESTAR = 36
DOUBLESTAREQUAL = 47
ENDMARKER = 0
EQEQUAL = 28
EQUAL = 22
ERRORTOKEN = 52
GREATER = 21
GREATEREQUAL = 31
INDENT = 5
LBRACE = 26
LEFTSHIFT = 34
LEFTSHIFTEQUAL = 45
LESS = 20
LESSEQUAL = 30
LPAR = 7
LSQB = 9
MINEQUAL = 38
MINUS = 15
NAME = 1
NEWLINE = 4
NL = 54
NOTEQUAL = 29
NT_OFFSET = 256
NUMBER = 2
N_TOKENS = 55
OP = 51
PERCENT = 24
PERCENTEQUAL = 41
PLUS = 14
PLUSEQUAL = 37
RBRACE = 27
RIGHTSHIFT = 35
RIGHTSHIFTEQUAL = 46
RPAR = 8
RSQB = 10
SEMI = 13
SLASH = 17
SLASHEQUAL = 40
STAR = 16
STAREQUAL = 39
STRING = 3
TILDE = 32
VBAR = 18
VBAREQUAL = 43
"""

