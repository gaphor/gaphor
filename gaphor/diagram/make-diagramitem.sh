#!/bin/sh

Name=$1
ParentName=$2

if test "x$ParentName" == "x"; then
	echo "Usage: $0 ChildClass ParentClass"
	exit 1
fi

parent_name=$(echo "$ParentName" | sed -e 's/\([A-Z]\)/_\1/g' -e 's/^_//g' | tr [A-Z] [a-z])

name=$(echo "$Name" | sed -e 's/\([A-Z]\)/_\1/g' -e 's/^_//g' | tr [A-Z] [a-z])

PARENT_NAME=$(echo "$parent_name" | tr [a-z] [A-Z])
NAME=$(echo "$name" | tr [a-z] [A-Z])

filename=$(echo "$name" | sed 's/_//g')
parentfilename=$(echo "$parent_name" | sed 's/_//g')

if test "x$parentfilename" == "xmodelelement"; then
	parentfilename="model-element"
fi

cat diagramitem-template.h | sed "s#@Name@#$Name#g
s#@ParentName@#$ParentName#g
s#@name@#$name#g
s#@parent_name@#$parent_name#g
s#@NAME@#$NAME#g
s#@PARENT_NAME@#$PARENT_NAME#g
s#@filename@#$filename#g
s#@parentfilename@#$parentfilename#g" > $filename.h

cat diagramitem-template.c | sed "s#@Name@#$Name#g
s#@ParentName@#$ParentName#g
s#@name@#$name#g
s#@parent_name@#$parent_name#g
s#@NAME@#$NAME#g
s#@PARENT_NAME@#$PARENT_NAME#g
s#@filename@#$filename#g
s#@parentfilename@#$parentfilename#g" > $filename.c
