#!/usr/bin/env python3
# vim:fileencoding=utf-8:ft=python
# file: open.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2014-12-26 11:45:59 +0100
# Last modified: 2015-05-03 21:49:32 +0200
#
# To the extent possible under law, <rsmith@xs4all.nl> has waived all
# copyright and related or neighboring rights to open.py. This work is
# published from the Netherlands. See
# http://creativecommons.org/publicdomain/zero/1.0/

"""Opens the file(s) given on the command line in the approriate program.
Some of the programs are X11 programs."""

from os.path import basename, isdir, isfile
from re import search, IGNORECASE
from subprocess import Popen, check_output
from sys import argv, exit, stderr
import argparse
import logging

__version__ = '1.0.0'

filetypes = {
    '\.(pdf|epub)$': ['mupdf'],
    '\.html$': ['firefox', '-new-tab'],
    '\.xcf$': ['gimp'],
    '\.(e)?ps$': ['gv'],
    '\.(jp(e)?g|png|gif|tif(f)?)$': ['gpicview'],
    '\.(pax|cpio|zip|jar|ar|xar|rpm|7z)$': ['tar', 'tf'],
    '\.(tar\.|t)(z|gz|bz(2)?|xz)$': ['tar', 'tf'],
    '\.(mp4|mkv|avi|flv|mpg|mov)$': ['mpv']
}
othertypes = {'dir': ['rox'], 'txt': ['gvim', '--nofork']}


def matchfile(fdict, odict, fname):
    """For the given filename, returns the matching program.

    Arguments:
        fdict: Handlers for files. A dictionary of regex:(commands)
            representing the file type and the action that is to be taken for
            opening one.
        odict: Handlers for other types. A dictionary of str:(arguments).
        fname: A string containing the name of the file to be opened.

    Returns: A list of commands for subprocess.Open.
    """
    for k, v in fdict.items():
        if search(k, fname, IGNORECASE) is not None:
            return v + [fname]
    try:
        if b'text' in check_output(['file', fname]):
            return odict['txt'] + [fname]
    except CalledProcessError:
        logging.warning("the command 'file {}' failed.".format(fname))
        return None


def main(argv):
    """Entry point for this script.

    Arguments:
        argv: command line arguments; list of strings.
    """
    if argv[0].endswith(('open', 'open.py')):
        del argv[0]
    opts = argparse.ArgumentParser(prog='open', description=__doc__)
    opts.add_argument('-v', '--version', action='version',
                      version=__version__)
    opts.add_argument('--log', default='warning',
                      choices=['info', 'debug', 'warning', 'error'],
                      help="logging level (defaults to 'warning')")
    opts.add_argument("files", metavar='file', nargs='*',
                      help="one or more files to process")
    args = opts.parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log.upper(), None),
                        format='%(levelname)s: %(message)s')
    logging.info('command line arguments = {}'.format(argv))
    logging.info('parsed arguments = {}'.format(args))
    for nm in args.files:
        logging.info("Trying '{}'".format(nm))
        if isdir(nm):
            cmds = othertypes['dir'] + [nm]
        elif isfile(nm):
            cmds = matchfile(filetypes, othertypes, nm)
        else:
            cmds = None
        if not cmds:
            logging.warning("do not know how to open '{}'".format(nm))
            continue
        try:
            Popen(cmds)
        except OSError as e:
            logging.error("opening '{}' failed: {}".format(nm, e))


if __name__ == '__main__':
    main(argv)
