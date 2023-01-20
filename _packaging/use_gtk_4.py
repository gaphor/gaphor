import os
import sys

os.environ["GAPHOR_USE_GTK"] = "4"
os.environ["XDG_DATA_DIRS"] = os.path.join(sys._MEIPASS, "share")  # type: ignore[attr-defined]
