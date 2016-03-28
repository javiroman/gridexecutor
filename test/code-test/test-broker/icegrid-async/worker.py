#!/usr/bin/env python
# **********************************************************************
#
# Copyright (c) 2003-2013 ZeroC, Inc. All rights reserved.
#
# This copy of Ice is licensed to you under the terms described in the
# ICE_LICENSE file included in this distribution.
#
# **********************************************************************

import sys
import os
import traceback
import threading
import Ice
import time
import socket

Ice.loadSlice('contract.ice')
import RemoteExecution

class WorkerJobThread(threading.Thread):
    def __init__(self, cb, lock):
        threading.Thread.__init__(self)
        self._cb = cb
        self._workers_lock = lock
        self.start()

    def run(self):
        ######### REAL WORK HERE #######
        print("real work running (%s) with jobid:") % os.geteuid()
        print "sleeping ..."
        sys.stdout.flush()
        os.system("sleep 5")
        # return value of method in contract
        return_string = "job run in node: %s" % socket.gethostname()
        # out parameter in the method call - worker hostname
        out_string  = socket.gethostname()
        self._cb.cb.ice_response(return_string, out_string)
        ######### RETURN RESULTS #########

        self._workers_lock.release()

class CallbackEntry(object):
    def __init__(self, cb, jobid, ips):
        self.cb = cb
        self.jobid = jobid
        self.ips = ips

class WorkQueue(threading.Thread):
    def __init__(self, ic, properties):
        threading.Thread.__init__(self)

        self.nworkers = properties.getPropertyAsInt("NumberWorkers")
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

        # 1. ACQUIRE the condition
        self._cond.acquire()

        try:
            while not self._done:
                print "callbacks pending %i" % len(self._callbacks)
                sys.stdout.flush()
                if len(self._callbacks) == 0:
                    print "######## WorkQueue thread waiting for jobs ########"
                    sys.stdout.flush()
                    # 2. WAITS for condigion: blocks until condition is notified
                    self._cond.wait()
                else:
                    print "callbacks (jobs) pending -> %i" % len(self._callbacks)

                if not self._done:
                    # If nworkers are full acquired the thread block here
                    # waiting for semaphore is released by one.
                    self._run_lock.acquire()

                    try:
                        WorkerJobThread(self._callbacks[0], self._run_lock)
                    except:
                        traceback.print_exc()

                    del self._callbacks[0]

            for i in range(0, len(self._callbacks)):
                self._callbacks[i].cb.ice_exception(RemoteExecution.RequestCanceledException())
        finally:
            # 3. RELEASE the condition
            print "3. RELEASE condition"
            sys.stdout.flush()
            self._cond.release()

    def add(self, cb, jobid, ips):
        # the producer
        self._cond.acquire()

        try:
            if not self._done:
                #
                # Here we pass the relevant data for
                # the job, jobid, ip target list, and
                # so forth.
                #
                sys.stdout.flush()
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
        print "job_enqueue add job (parameter: %s)" % i
        print "and remote device IP list:"
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
        print "shutdown"
        sys.stdout.flush()
        serv_thread.gracefulShutdown()

        return 0

    def interruptCallback(self, sig):
        print "interruptCallback"
        sys.stdout.flush()
        self._workQueue.destroyWorkQueue()
        try:
            self._communicator.destroy()
        except:
            traceback.print_exc()

def main():
    app = Server()
    return(app.main(sys.argv))

if __name__ == "__main__":
    sys.exit(main())

