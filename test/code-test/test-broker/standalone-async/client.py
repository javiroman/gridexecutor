#!/usr/bin/env python
# **********************************************************************
#
# Copyright (c) 2003-2013 ZeroC, Inc. All rights reserved.
#
# This copy of Ice is licensed to you under the terms described in the
# ICE_LICENSE file included in this distribution.
#
# **********************************************************************

# https://docs.python.org/2.6/library/threading.html

import sys
import os
import traceback
import threading
import Ice

Ice.loadSlice('contract.ice')
import RemoteExecution

class Callback(Ice.Object):
    def __init__(self, application):
        self.app_reference = application

    def response(self, result, other):
        self.app_reference.cond.acquire()
        try:
                print "Terminada operacion con return [%s]" % result
                print "Terminada operacion con out params [%s]" % other
                self.app_reference.jobs -= 1
                if self.app_reference.jobs == 0:
                        self.app_reference.cond.notify()
        finally:
                self.app_reference.cond.release()

    def exception(self, ex):
        try:
                raise ex
        except Ice.LocalException, e:
                print "interpolate failed: " + str(e)
        except:
                self.app_reference.cond.acquire()
                try:
                        print "excepcion --- "
                        self.app_reference.jobs -= 1
                        if self.app_reference.jobs == 0:
                                self.app_reference.cond.notify()
                finally:
                        self.app_reference.cond.release()
                raise ex

class Client(Ice.Application):
        def __init__(self):
            print "constructor cliente"
            self.jobs = 0
            self.cond = threading.Condition()

        def launchCommand(self, count):
            ic = self.communicator()

            remote = RemoteExecution.RemoteCommandPrx.checkedCast(self.communicator().propertyToProxy('Remote.Proxy'))

            if not remote:
                print(args[0] + ": invalid proxy")
                return 1

            for i in range(count):
                try:
                    self.cond.acquire()
                    try:
                        self.jobs += 1

                        string = ""
                        cb = Callback(self)
                        r = remote.begin_sendGridCommand(10, cb.response, cb.exception)
                        print "async job launched ... %d" % self.jobs

                    finally:
                        self.cond.release()

                    self.cond.acquire()
                except:
                        traceback.print_exc()
                        return False

            # Waits for jobs termination.(AMI+AMD feature)
            self.cond.acquire()
            try:
                    while self.jobs:
                            self.cond.wait()
            finally:
                    self.cond.release()

            return True

        def run(self, args):
            ic = self.communicator()

            self.launchCommand(2)

            if (ic):
                try:
                    self.communicator().destroy()
                except:
                    traceback.print_exc()
                    status = 1

app = Client()

sys.exit(app.main(sys.argv, "config.client"))
