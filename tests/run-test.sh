#!/bin/sh
# vim: sw=4
export PYTHONPATH="../build/lib:${PYTHONPATH}"

EXITCODE=0
for TEST in "$@"; do
    if echo "${TEST}" | grep -q '\.py$'; then
	TEST="python ${TEST}"
    else
        TEST="./${TEST}"
    fi
    echo "Running test: ${TEST}"
    if ! eval "${TEST}"; then
	EXITCODE=1
	break;
    fi
done

echo "============="
if test "${EXITCODE}" = "0"; then
	echo " Test passed"
else
	echo " Test failed"
fi
echo "============="

exit ${EXITCODE}
