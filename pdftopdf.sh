#!/bin/sh
# file: pdftopdf.sh
# vim:fileencoding=utf-8:fdm=marker:ft=sh
#
# Copyright © 2014-2016 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2014-02-27T00:15:14+0100
# Last modified: 2018-04-16T22:27:59+0200

if [ $# -lt 1 ]; then
    echo "Usage: $(basename $0) file"
    exit 1
fi

# Check for special programs that are used in this script.
PROGS="gs"
for P in $PROGS; do
    which $P >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "$(basename $0): The program \"$P\" cannot be found."
        exit 1
    fi
done

TMPNAME=$(mktemp)
INNAME=$1

set -e
gs -DNOPAUSE -sDEVICE=pdfwrite \
    -sOutputFile=$TMPNAME $INNAME -c quit >/dev/null 2>&1
mv $INNAME ${INNAME%.pdf}-orig.pdf
cp $TMPNAME $INNAME
rm -f $TMPNAME
