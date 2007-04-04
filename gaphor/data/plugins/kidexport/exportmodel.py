import time
import gaphor
from gaphor import UML
import kid

class KidExport(object):
    template = "/home/jeroen/OpenSource/gaphor/data/plugins/kidexport/xmi.kid"
    
    def export(self, filename):
        """Export the loaded Gaphor model with the specific template."""
        template = kid.Template(file=self.template)
        isinstance(template, kid.XMLSerializer)
        f = open(filename, 'w')
        f.write(template.serialize())
        f.close()