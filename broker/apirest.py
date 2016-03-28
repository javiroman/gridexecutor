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


import web
import os
import time
import sys
import Queue
import threading
import Ice

CONFIG_FILE = "broker/gridlocator.cfg"

from jobqueues import ThreadSafeDict
from jobqueues import submitterThread
from gridclient import Client

# Main global Queues
runQueue = Queue.PriorityQueue()
endDict = ThreadSafeDict()
runDict = ThreadSafeDict()

def startrest(args):
    # sumitterThread: Get jobs from REST and submite to grid cluster.
    # This thread is the runQueue consummer.

    iceEngine = Client(runQueue, endDict)
    data = Ice.InitializationData()
    data.properties = Ice.createProperties()
    data.properties.load(CONFIG_FILE)

    submitter = threading.Thread(target=submitterThread,
                                 args=(runQueue,endDict,iceEngine))
    submitter.daemon = True
    submitter.start()

    iceEngine.main(args, CONFIG_FILE, data)

