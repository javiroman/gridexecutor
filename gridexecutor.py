#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015 Javi Roman <jromanes@redhat.com>
#
# This file is part of Gridexecutor Program
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Program Docstring
Docstrings: http://www.python.org/dev/peps/pep-0257/
"""

__version__ = "1.0.0"
__author__ = "Javi Roman <jromanes@redhat.com>"
__copyright__ = "Copyright (C) 2015 Red Hat Inc."

import sys
import optparse
import time
from broker.daemon import Daemon
from broker.apirest import startrest

# Python sanity check: program tested for: 2.7.8,
if sys.hexversion < 0x020400F0:
    print "Sorry, python 2.4 or later is required"
    sys.exit(1)

class Server(Daemon):
    def run(self):
        startrest(self.args)

class AppGridExecutor():
    """docstring for ClassName"""
    def __init__(self):
        self._parse_args()

    def _parse_args(self):
        usage = "usage: %prog [options]"
        version = "Grid Executor version %s" % __version__

        parser = optparse.OptionParser(usage=usage, version=version)
        parser.add_option("-v", "--verbose",
                          action="store_true",
                          dest="verbose",
                          help="set verbosity output")

        parser.add_option("-a", "--attach",
                          action="store_true",
                          dest="attach",
                          help="no daemonize")

        parser.add_option("-s", "--stop",
                          action="store_true",
                          dest="stop",
                          help="stop daemon")

        (self.options, args) = parser.parse_args()

        if self.options.verbose:
            print "Verbose output enabled"

        if self.options.attach:
            print "Daemon attached to console"

        if len(sys.argv) == 1:
            parser.print_help()
            sys.exit(1)

    def run(self):
        if self.options.stop:
            daemon = Server(sys.argv, '/tmp/daemon-example.pid')
            daemon.stop()
            print "Daemon stoped."
            return

        if self.options.attach:
            print "call startrest"
            startrest(sys.argv)
        else:
            daemon = Server(sys.argv, '/tmp/daemon-example.pid')
            print "Daemon started."
            daemon.start()

if __name__ == "__main__":
    app = AppGridExecutor()
    sys.exit(app.run())

# vim: ts=4:sw=4:et:sts=4:ai:tw=80
