#!/bin/bash

# Check the consistency of the model by setting a value in every field

cat > testlist.py << EOF
from UML import *

testlist = [
`cat ../gaphor/UML/ModelElements.py | grep '^class' | grep -v 'Enumeration_' | sed 's/class \([a-zA-Z_0-9]*\).*/    \1,/g'`
]
EOF

python model-consistency.py

