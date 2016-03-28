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


# Fabric doesn't support running arbitrary python code on a remote host.
# Fabric mostly runs by invoking shell commands over SSH (for remote machines).
# The remote machine doesn't even need python installed for Fabric to work.
import sys
from fabric import tasks
from fabric.api import run
from fabric.api import env
from fabric.api import execute
from fabric.api import output
from fabric.network import disconnect_all
from fabfile import host_type, exec_sync, exec_async, waitsForCompletion
import random
import time

VERSION = "0.0.1"

env.hosts = [
    'sgt2-slave1',
    'sgt2-slave2',
    ]

class RemoteExecutor():
    def __init__(self):
        print "RemoteExecutor constructor"
        random.seed()

    def _handlePolling(self, ids):
        return tasks.execute(waitsForCompletion, ids)

    def execSyncCmd(self, cmd):
        tasks.execute(exec_sync, cmd)

    def execAsyncCmd(self, cmd, ids):
        tasks.execute(exec_async, cmd, ids)
        return self._handlePolling(ids)

    def generateSessionID(self):
        return "%s.%i" % (time.time(), random.randint(1, 1000))

