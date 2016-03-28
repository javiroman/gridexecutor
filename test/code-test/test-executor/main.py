#!/usr/bin/env python
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
    'sgt2-disp1',
    'sgt2-disp2',
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

def main():
    print "----------------------------"
    print "Python Fabric example %s" % VERSION
    print "----------------------------"

    app = RemoteExecutor()

    # app.execSyncCmd("/tmp/remote.sh")
    ret = app.execAsyncCmd("/home/jromanes/remote.sh",
                    app.generateSessionID())

    print ret

    disconnect_all()

if __name__ == "__main__":
    sys.exit(main())
