
LIBXML2=1
MINIDOM=2

parser=0

try:
    import libxml2
    del libxml2
    parser = LIBXML2
except ImportError:
    try:
	import xml.sax.expatreader
	del xml.sax.expatreader
	parser = MINIDOM
    except ImportError:
	pass

if parser == LIBXML2:
    from storage_libxml2 import *
    log.debug('Using libxml2...')
elif parser == MINIDOM:
    from storage_minidom import *
    log.debug('Using xml.dom.minidom...')
else:
    raise ImportError, 'No suitable XML reader found'

