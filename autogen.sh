#!/bin/sh
#
# TODO: check Automake >= 1.5

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
AUTOMAKE=`type automake | awk '{ print $3 }'`
AUTOCONF=`type autoconf | awk '{ print $3 }'`

if test ! -x "${ACLOCAL}" \
|| test ! -x "${AUTOMAKE}" \
|| test ! -x "${AUTOCONF}"
then
	echo "You should have installed the automake packages!"
	exit 1
fi

if test -z "${ACLOCAL_FLAGS}"; then
	run "${ACLOCAL}"
else
	run "${ACLOCAL} ${ACLOCAL_FLAGS}"
fi
#test -f './py-compile' && rm ./py-compile
run "${AUTOMAKE}" -a
run "${AUTOCONF}"

run ./configure --enable-maintainer-mode $*
