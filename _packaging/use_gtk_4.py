import logging
import os
import sys

os.environ["GAPHOR_USE_GTK"] = "4"

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
log.warning("XDG_DATA_DIRS %s", os.getenv("XDG_DATA_DIRS") or "<empty>")
for n, m in sys.modules.items():
    log.warning("sys modules %s: %s", n, m)
