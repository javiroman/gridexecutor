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

# Example of Queue with maxsize:
# http://agiliq.com/blog/2013/10/producer-consumer-problem-in-python/
import threading
import time
import signal
import random
import sys
import os
import Ice
from gridclient import Client

class ThreadSafeDict(dict) :
    def __init__(self, * p_arg, ** n_arg) :
        dict.__init__(self, * p_arg, ** n_arg)
        self._lock = threading.Lock()

    def __enter__(self) :
        self._lock.acquire()
        return self

    def __exit__(self, type, value, traceback) :
        self._lock.release()

def submitterThread(q, endDict, iceEngine):
    # This thread is the magic for Ice AMI
    # blocking thread.
    while True:
        # block if q es empty
        if q.empty():
            print "[Submitter Thread waiting for jobs in queue ...]"

        next_job = q.get()

        # Send job to cluster
        iceEngine.submitgrid(next_job)

        # The count of unfinished tasks goes up whenever
        # an item is added (put) to the queue. The count
        # goes down whenever a consumer thread calls
        # task_done() to indicate that the item was
        # retrieved and all work on it is complete.
        # When the count of unfinished tasks drops to zero,
        # q.join() unblocks.
        q.task_done()

