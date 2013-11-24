#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# $Date$
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to foto4lb.py. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Shrink fotos to a size suitable for use in my logbook and other
   documents."""

from __future__ import division, print_function

__version__ = '$Revision$'[11:-2]

import os
import sys
import subprocess
from multiprocessing import Pool, Lock
from os import utime
from time import mktime
from datetime import datetime
import argparse

globallock = Lock()


def checkfor(args, rv=0):
    """Make sure that a program necessary for using this script is
    available.

    :param args: String or list of strings of commands. A single string may
    not contain spaces.
    :param rv: Expected return value from evoking the command.
    """
    if isinstance(args, str):
        if ' ' in args:
            raise ValueError('no spaces in single command allowed')
        args = [args]
    try:
        with open(os.devnull, 'w') as bb:
            rc = subprocess.call(args, stdout=bb, stderr=bb)
        if rc != rv:
            raise OSError
    except OSError as oops:
        outs = "Required program '{}' not found: {}."
        print(outs.format(args[0], oops.strerror))
        sys.exit(1)


def getexifdict(name):
    args = ['exiftool', '-CreateDate', '-Comment', '-Copyright', name]
    data = subprocess.check_output(args)
    lines = data.splitlines()
    ld = {}
    for l in lines:
        key, val = l.split(':', 1)
        key = key.replace(' ', '')
        val = val.strip()
        if key == 'CreateDate':
            val = val.replace(' ', ':')
        ld[key] = val
    return ld


def processfile(args):
    name, width = args
    try:
        ed = getexifdict(name)
        fields = ed['CreateDate'].split(':')
        dt = datetime(int(fields[0]), int(fields[1]), int(fields[2]),
                      int(fields[3]), int(fields[4]), int(fields[5]))
    except:
        ed = {}
        cds = '{}:{}:{} {}:{}:{}'
        dt = datetime.today()
        ed['CreateDate'] = cds.format(dt.year, dt.month, dt.day,
                                      dt.hour, dt.minute, dt.second)
    args = ['mogrify', '-strip', '-resize', str(width), '-units',
            'PixelsPerInch', '-density', '300', '-quality', '90', name]
    rv = subprocess.call(args)
    errstr = "Error when processing file '{}'"
    if rv != 0:
        globallock.acquire()
        print(errstr.format(name))
        globallock.release()
        return
    args = ['exiftool']
    args += ['-{}="{}"'.format(k, ed[k]) for k in ed.keys()]
    args += ['-q', '-overwrite_original', name]
    rv = subprocess.call(args)
    if rv == 0:
        modtime = mktime((dt.year, dt.month, dt.day, dt.hour,
                         dt.minute, dt.second, 0, 0, -1))
        utime(name, (modtime, modtime))
        globallock.acquire()
        print("File '{}' processed".format(name))
        globallock.release()
    else:
        globallock.acquire()
        print(errstr.format(name))
        globallock.release()


def main(argv):
    """Main program.

    Keyword arguments:
    argv -- command line arguments
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-w', '--width', default=886, type=int,
                        help='width of the images in pixels (default 886)')
    parser.add_argument('-v', '--version', action='version',
                        version=__version__)
    parser.add_argument('file', nargs='*')
    args = parser.parse_args(argv)
    if not args.file:
        parser.print_help()
        sys.exit(0)
    checkfor(['exiftool',  '-ver'])
    checkfor('mogrify')
    p = Pool()
    mapargs = [(fn, args.width) for fn in args.file]
    p.map(processfile, mapargs)
    p.close()


if __name__ == '__main__':
    main(sys.argv[1:])
