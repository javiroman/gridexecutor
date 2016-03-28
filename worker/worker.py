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

import sys
import os
import traceback
import threading
import Ice
import time
import socket
from fabric import tasks
from fabric.api import run
from fabric.api import env
from fabric.api import execute
from fabric.api import output
from fabric.network import disconnect_all
from fabfile import host_type, exec_sync, exec_async, waitsForCompletion
import random

Ice.loadSlice('contract.ice')
import RemoteExecution
from fabexecutor import RemoteExecutor

env.hosts = []

class WorkerJobThread(threading.Thread):
    def __init__(self, cb, lock):
        threading.Thread.__init__(self)
        self._cb = cb
        self._workers_lock = lock
        self.start()

    def run(self):
        print("real work running (%s) with jobid:") % os.geteuid()
        print self._cb.jobid
        sys.stdout.flush()

        env.hosts = self._cb.ips

        app = RemoteExecutor()
        # app.execSyncCmd("/tmp/remote.sh")
        ret = app.execAsyncCmd("/home/jromanes/remote.sh",
                                self._cb.jobid)
        print ret
        print("remote work done")
        sys.stdout.flush()

        disconnect_all()

        # return value of method in contract
        return_string = "job run in node: %s" % socket.gethostname()
        # out parameter in the method call - worker hostname
        out_string  = socket.gethostname()
        self._cb.cb.ice_response(return_string, out_string)

        self._workers_lock.release()

class CallbackEntry(object):
    def __init__(self, cb, jobid, ips):
        self.cb = cb
        self.jobid = jobid
        self.ips = ips

class WorkQueue(threading.Thread):
    def __init__(self, ic, properties):
        threading.Thread.__init__(self)

        self.nworkers = properties.getPropertyAsInt("WorkerNumber")
        print "workers number: %i" % self.nworkers
        sys.stdout.flush()

        self._callbacks = []
        self._done = False

        # A condition represents some kind of state change in the application,
        # and a thread can wait for a given condition, or signal that the
        # condition has happened. The condition is asociated with some kind
        # of lock. The thread aquire the lock with "acquire". The "wait" method
        # release the lock and blocks until it is awakened by a "nofify" in the
        # same condition in other thread.
        # the typical programming style using condition variables uses the lock
        # to synchronize access to some shared state; threads that are
        # interested in a particular change of state call wait() repeatedly
        # until they see the desired state, while threads that modify the state
        # call notify() or notifyAll() when they change the state in such a way
        # that it could possibly be a desired state for one of the waiters.
        self._cond = threading.Condition()

        # Semaphore: the counter is decremented when the semaphore is acquired, and
        # incremented when the semaphore is released. If the counter reaches
        # zero when acquired, the acquiring thread will block. When the
        # semaphore is incremented again, one of the blocking threads (if any)
        # will run. With this semaphore we are controlling the concurrent fab
        # jobs running in the node.
        self._run_lock = threading.Semaphore(self.nworkers)

    def run(self):
        print "WorkQueue thread running"
        print "------------------------"
        sys.stdout.flush()

        # 1-acquire condition
        self._cond.acquire()

        try:
            while not self._done:
                print "callbacks pending %i" % len(self._callbacks)
                sys.stdout.flush()
                if len(self._callbacks) == 0:
                    print "[WorkQueue thread ready for jobs]"
                    sys.stdout.flush()
                    # 1-wait blocks until condition change with notify
                    self._cond.wait()
                else:
                    print "callbacks (jobs) pending -> %i" % len(self._callbacks)
                    sys.stdout.flush()

                if not self._done:
                    # If nworkers are full acquired the thread block here
                    # waiting for semaphore is released by one worker ending.
                    self._run_lock.acquire()

                    try:
                        WorkerJobThread(self._callbacks[0], self._run_lock)
                    except:
                        traceback.print_exc()

                    del self._callbacks[0]

            for i in range(0, len(self._callbacks)):
                self._callbacks[i].cb.ice_exception(RemoteExecution.RequestCanceledException())
        finally:
            # 1-release the condition.
            self._cond.release()

    def add(self, cb, jobid, ips):
        # this is the job producer
        self._cond.acquire()

        try:
            if not self._done:
                #
                # Here we pass the relevant data for
                # the job, jobid, ip target list, and
                # so forth.
                #
                entry = CallbackEntry(cb, jobid, ips)
                if len(self._callbacks) == 0:
                    self._cond.notify()
                self._callbacks.append(entry)
            else:
               cb.ice_exception(RemoteExecution.RequestCanceledException())
        finally:
            self._cond.release()

    def destroyWorkQueue(self):
        print "destroy WorkQueue"
        sys.stdout.flush()
        self._cond.acquire()

        try:
            self._done = True
            self._cond.notify()
        finally:
            self._cond.release()

class RemoteCommandI(RemoteExecution.RemoteCommand):
    def __init__(self, ic):
        properties = ic.getProperties()

        self._job_queue = WorkQueue(ic, properties)
        self._job_queue.start()

    def sendGridCommand_async(self, cb, i, ips, current=None):
        print "enqueue job (parameter: %s)" % i
        print "Remote device IP list:"
        print ips
        sys.stdout.flush()
        #
        # We have to pass relevant data for real work here
        # this is the connection with the client data.
        #
        self._job_queue.add(cb, i, ips)

    def gracefulShutdown(self, current=None):
        print "ice engine shutdown"
        sys.stdout.flush()
        self._job_queue.destroyWorkQueue()

class Server(Ice.Application):
    def __init__(self):
        print "Server constructor"
        sys.stdout.flush()

    def run(self, args):

        self.callbackOnInterrupt()

        ic = self.communicator()

        properties = ic.getProperties()
        print properties.getProperty("Ice.ThreadPool.Server.Size")
        sys.stdout.flush()

        adapter = ic.createObjectAdapter("RemoteAdapter")

        serv_thread = RemoteCommandI(ic)
        ident = ic.stringToIdentity("ObjectIdentity")
        adapter.add(serv_thread, ident)
        adapter.activate()

        self.communicator().waitForShutdown()
        serv_thread.gracefulShutdown()

        return 0

    def interruptCallback(self, sig):
        print "interruptCallback"
        try:
            self._communicator.destroy()
        except:
            traceback.print_exc()

def main():
    app = Server()
    return(app.main(sys.argv))

if __name__ == "__main__":
    sys.exit(main())

