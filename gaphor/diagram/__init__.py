# All model items...

from actor import *
from comment import *
from commentline import *
from usecase import *
from relationship import *
from dependency import *
from generalization import *

from diagramitemfactory import *

#  Register diagram items with the diagram item factory

import gaphor.UML as UML

f = DiagramItemFactory()
f.register (ActorItem, UML.Actor)
f.register (CommentItem, UML.Comment)
f.register (UseCaseItem, UML.UseCase)

del f
del UML

