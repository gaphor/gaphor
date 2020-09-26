#!/bin/bash
#
# Generate documentation pages for a model

H1="========================================"
H2="----------------------------------------"

cat > models/uml.rst << EOF
Unified Modeling Language
$H1

.. image:: uml/00._Overview.svg

.. toctree::
   :caption: Packages
   :maxdepth: 1

EOF

ls models/uml | while read PACKAGE
do
  if test -d models/uml/$PACKAGE
  then
    echo "   uml/${PACKAGE}" >> models/uml.rst

    {
      echo "${PACKAGE//_/ }"
      echo $H1
      ls models/uml/${PACKAGE} | while read DIAGRAM
      do
        name=${DIAGRAM%.svg}
        echo "${name//_/ }"
        echo $H2
        echo
        echo ".. image:: ${PACKAGE}/${DIAGRAM}"
        echo
      done
    } > models/uml/${PACKAGE}.rst
  fi
done
