export PYTHONPATH="`pwd`:$PYTHONPATH"
export GAPHOR_DATADIR="`pwd`/data"

test -x "./bin/gaphor" || {
	echo "$0: first configure Gaphor (e.g. './configure')"
	exit 1
}
exec "./bin/gaphor"
