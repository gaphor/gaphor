#!/bin/bash
#
# Generate documentation pages for a model

M=$1

H1="=================================================="
H2="--------------------------------------------------"

if test "$M" == "core"
then
  cat > models/"$M".rst << EOF
Modeling Language Core
$H1

.. image:: $M/Core/main.svg

EOF
exit
elif test "$M" == "uml"
then
  cat > models/"$M".rst << EOF
Unified Modeling Language
$H1

.. image:: $M/00._Overview.svg

.. toctree::
  :caption: Packages
  :maxdepth: 1

EOF
elif test "$M" == "sysml/Profiles/SysML"
then
  cat > "models/$(basename "$M").rst" << EOF
Systems Modeling Language
$H1

.. image:: $M/SysML.svg

.. toctree::
  :caption: Packages
  :maxdepth: 1

EOF
elif test "$M" == "raaml/Profiles/RAAML"
then
  cat > "models/$(basename "$M").rst" << EOF
Risk Analysis and Assessment Modeling Language
$H1

.. image:: $M/RAAML_diagram.svg

.. toctree::
  :caption: Packages
  :maxdepth: 1

EOF
elif test "$M" == "c4model"
then
  cat > "models/$(basename "$M").rst" << EOF
C4 Model
$H1

.. image:: $M/Overview.svg

.. toctree::
  :caption: Packages
  :maxdepth: 1

EOF
else
  echo "*** Unknown model $M"
  exit 1
fi

find "models/${M}" -mindepth 1 -maxdepth 1 -type d -printf "%P\n" | sort | while read -r PACKAGE
do
  echo " models/$M/$PACKAGE..."
  echo "  ${M}/${PACKAGE}" >> "models/$(basename "$M").rst"

  {
    echo "${PACKAGE//_/ }"
    echo $H1
    echo
    find "models/${M}/${PACKAGE}" -mindepth 1 -type f -printf "%P\n" | sort | while read -r DIAGRAM
    do
      name=${DIAGRAM%.svg}
      if test "$name" != "$PACKAGE"
      then
        echo "${name//_/ }"
        echo $H2
        echo
      fi
      echo ".. thumbnail:: ${PACKAGE}/${DIAGRAM}"
      echo "  :group: ${PACKAGE}"
      echo
    done
  } > "models/$M/${PACKAGE}.rst"
done
