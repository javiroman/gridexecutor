#!/usr/bin/env python
# **********************************************************************
#
# Copyright (c) 2003-2013 ZeroC, Inc. All rights reserved.
#
# This copy of Ice is licensed to you under the terms described in the
# ICE_LICENSE file included in this distribution.
#
# **********************************************************************

import sys, os, traceback, threading, Ice, time

Ice.loadSlice('contract.ice')
import RemoteExecution

class CallbackEntry(object):
    def __init__(self, cb):
        self.cb = cb

class WorkQueue(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._callbacks = []
        self._done = False
        self._cond = threading.Condition()

    def run(self):
        print "WorkQueue thread running"
        print "------------------------"
        self._cond.acquire()

        try:
            while not self._done:
                print "callbacks pending %i" % len(self._callbacks)
                if len(self._callbacks) == 0:
                    print "WorkQueue thread ready for jobs"
                    self._cond.wait()

                if not self._done:
                    print("Sleeping 2 seconds")
                    time.sleep(2)
                    return_string = "return value del metodo"
                    out_string  = "parametros con out en el metodo"
                    self._callbacks[0].cb.ice_response(return_string, out_string)
                    del self._callbacks[0]

            for i in range(0, len(self._callbacks)):
                self._callbacks[i].cb.ice_exception(RemoteExecution.RequestCanceledException())
        finally:
            self._cond.release()

    def add(self, cb):
        self._cond.acquire()

        try:
            if not self._done:
                entry = CallbackEntry(cb)
                if len(self._callbacks) == 0:
                    self._cond.notify()
                self._callbacks.append(entry)
            else:
               cb.ice_exception(RemoteExecution.RequestCanceledException())
        finally:
            self._cond.release()

    def destroy(self):
        self._cond.acquire()

        try:
            self._done = True
            self._cond.notify()
        finally:
            self._cond.release()

class RemoteCommandI(RemoteExecution.RemoteCommand):
    def __init__(self, workQueue):
        self._workQueue = workQueue

    def sendGridCommand_async(self, cb, i, current=None):
        print "enqueue job (parameter: %i)" % i
        self._workQueue.add(cb)

    def shutdown(self, current=None):
        self._workQueue.destroy()
        current.adapter.getCommunicator().shutdown();

class Server(Ice.Application):
    def run(self, args):
        if len(args) > 1:
            print(self.appName() + ": too many arguments")
            return 1

        self.callbackOnInterrupt()

        adapter = self.communicator().createObjectAdapter("Remote")

        self._workQueue = WorkQueue()

        adapter.add(RemoteCommandI(self._workQueue),
                    self.communicator().stringToIdentity("ObjectIdentity"))

        self._workQueue.start()
        adapter.activate()

        self.communicator().waitForShutdown()
        self._workQueue.join()
        return 0

    def interruptCallback(self, sig):
        self._workQueue.destroy()
        self._communicator.shutdown()

app = Server()
sys.exit(app.main(sys.argv, "config.server"))
