import os
import pprint
import sys
import traceback

os.environ["GAPHOR_USE_GTK"] = "4"
print("XDG_DATA_DIRS", os.environ["XDG_DATA_DIRS"])
pprint.pprint(sys.modules)

traceback.print_stack()
