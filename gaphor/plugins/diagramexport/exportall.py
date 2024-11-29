import logging
from pathlib import Path

from gaphor.core.modeling import Diagram
from gaphor.diagram.export import escape_filename

log = logging.getLogger(__name__)


def pkg2dir(package):
    """Return directory path from package class."""
    name: list[str] = []
    while package:
        name.insert(0, package.name)
        package = package.package
    return "/".join(name)


def export_all(factory, path, save_fn, suffix, name_re=None, underscore=None):
    for diagram in factory.select(Diagram):
        odir = f"{path}/{pkg2dir(diagram.owner)}"
        # just diagram name
        dname = escape_filename(diagram.name)
        # full diagram name including package path
        pname = f"{odir}/{dname}"

        if underscore:
            log.info("replacing underscores")
            odir = odir.replace(" ", "_")
            dname = dname.replace(" ", "_")

        if name_re and not name_re.search(pname):
            log.debug("skipping %s", pname)
            continue

        outfilename = f"{odir}/{dname}.{suffix}"

        if not Path(odir).exists():
            log.debug("creating dir %s", odir)
            Path(odir).mkdir(parents=True)

        log.info("rendering: %s -> %s...", pname, outfilename)

        save_fn(outfilename, diagram)
