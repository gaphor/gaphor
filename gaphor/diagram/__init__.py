# All model items...

from actor import *
from klass import *
from comment import *
from commentline import *
from usecase import *
from package import *
from relationship import *
from dependency import *
from generalization import *
from association import *

from diagramitemfactory import *

# Register diagram items with the diagram item factory

import gaphor.UML as UML

f = GaphorResource(DiagramItemFactory)
f.register (ActorItem, UML.Actor)
f.register (ClassItem, UML.Class)
f.register (CommentItem, UML.Comment)
f.register (UseCaseItem, UML.UseCase)
f.register (PackageItem, UML.Package)

del f
del UML

