#!/bin/sh

run () {
	echo "Doing '$*'..."
	$*
	RC=$?
	if test ${RC} != 0
	then
		echo "Exit with error (${RC})"
		exit 1
	fi
}

ACLOCAL=`type aclocal | awk '{ print $3 }'`
LIBTOOLIZE=`type libtoolize | awk '{ print $3 }'`
AUTOMAKE=`type automake | awk '{ print $3 }'`
AUTOCONF=`type autoconf | awk '{ print $3 }'`

if test ! -x "${ACLOCAL}" \
|| test ! -x "${LIBTOOLIZE}" \
|| test ! -x "${AUTOMAKE}" \
|| test ! -x "${AUTOCONF}"
then
	echo "You should have installed automake and libtool packages!"
	exit 1
fi

if test -z "${ACLOCAL_FLAGS}"; then
	run "${ACLOCAL}"
else
	run "${ACLOCAL} ${ACLOCAL_FLAGS}"
fi
run "${LIBTOOLIZE}" -c -f
test -f './py-compile' && rm ./py-compile
run "${AUTOMAKE}" -c -a
run "${AUTOCONF}"

run ./configure --enable-maintainer-mode $*

echo
echo "Now enter 'make' to compile"
echo
