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

CONFIG_FILE = "gridlocator.cfg"
VERSION = "1.0.0"

class Callback(Ice.Object):
    def __init__(self, application):
        self.app_reference = application

    def response(self, result, other):
        self.app_reference.cond.acquire()
        try:
                print "return [%s]" % result
                print "out params [%s]" % other
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
            # condition variable
            self.cond = threading.Condition()

        def launchCommand(self):
            ic = self.communicator()

            try:
                # block when no more servants avaliables and
                # wait for available ones. This can be modified
                # with server pool: Ice.ThreadPool.Server.Size
                e_servant = RemoteExecution.RemoteCommandPrx. \
                    checkedCast(ic.stringToProxy("ObjectIdentity"))

            except Ice.NotRegisteredException:
                print "%s: Execpcion no registrado!!!" % self.appName()
                traceback.print_exc()
                return False

            try:
                self.cond.acquire()
                try:
                    cb = Callback(self)
                    r = e_servant.begin_sendGridCommand("JID-11111", ["1", "2"], cb.response, cb.exception)
                    self.jobs += 1
                    print "async job launched ... %d" % self.jobs
                finally:
                    self.cond.release()
            except:
                    traceback.print_exc()
                    return False

            return True

        def run(self, args):
            ic = self.communicator()

            for i in range(int(args[1])):
                self.launchCommand()

            # Waits for jobs termination.(AMI+AMD feature)
            self.cond.acquire()
            try:
                print "waiting for job termination"
                while self.jobs:
                    self.cond.wait()
            finally:
                self.cond.release()

            if (ic):
                try:
                    self.communicator().destroy()
                except:
                    traceback.print_exc()
                    status = 1

def main():
    print "-------------------------------------------------------"
    print "launched Client client_uno %s" % VERSION
    print "-------------------------------------------------------"

    app = Client()

    if not os.path.exists(CONFIG_FILE):
            return(app.main(sys.argv))
    else:
            data = Ice.InitializationData()
            # data.logger = MyLogger()
            data.properties = Ice.createProperties()
            data.properties.load(CONFIG_FILE)

            return(app.main(sys.argv, CONFIG_FILE, data))


if __name__ == "__main__":
    sys.exit(main())

