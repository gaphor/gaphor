export PYTHONPATH="`pwd`:$PYTHONPATH"

test -x "./bin/gaphor" || {
	echo "$0: first configure Gaphor (e.g. './configure')"
	exit 1
}
exec "./bin/gaphor"
