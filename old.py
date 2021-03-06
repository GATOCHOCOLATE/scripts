#!/usr/bin/env python3
# file: old.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2014-2017 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2014-02-10T22:02:02+01:00
# Last modified: 2018-07-07T15:00:35+0200
"""
Renames a directory by prefixing the name with 'old-'.

If the directory name starts with a period, it removes the period and prefixes
it with 'old-dot'.
"""

from datetime import datetime
import logging
import os
import sys

__version__ = '1.1.0'


def main(argv):
    """
    Entry point for old.

    Arguments:
        argv: command line arguments.
    """
    if len(argv) < 2:
        binary = os.path.basename(argv[0])
        print(f"{binary} ver. {__version__}", file=sys.stderr)
        print(f"Usage: {binary} directory ...", file=sys.stderr)
        sys.exit(1)
    logging.basicConfig(format='%(levelname)s: %(message)s')
    for dirname in argv[1:]:
        if not os.path.isdir(dirname):
            logging.warning(f"'{dirname}' is not a directory. Skipping.")
            continue
        if dirname.endswith(os.sep):
            dirname = dirname[:-1]
        dt = datetime.now().strftime('-%Y%m%dT%H%M')
        if dirname.startswith('.'):
            newname = ''.join(['old-dot', dirname[1:], dt])
        else:
            newname = ''.join(['old-', dirname, dt])
        if os.path.exists(newname):
            logging.warning(f"'{newname}' already exists. Skipping rename of '{dirname}'.")
            continue
        os.rename(dirname, newname)


if __name__ == '__main__':
    main(sys.argv)
