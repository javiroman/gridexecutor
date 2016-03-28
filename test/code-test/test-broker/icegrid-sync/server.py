#!/usr/bin/env python

import sys
import Ice
import time
import socket

Ice.loadSlice("contract.ice")
import HelloGrid

VERSION = "0.0.1"


class InterfaceServant1I(HelloGrid.InterfaceServant1):
    def __init__(self):
        print "InterfaceServant_1 constructor"

    def doMethod1(self, current=None):
        cad = "doMethod_1: sleeping 5 seconds in %s" % socket.gethostname()
        time.sleep(5)
        return cad

    def doMethod2(self, current=None):
        cad = "doMethod_2: sleeping 5 seconds in %s" % socket.gethostname()
        time.sleep(5)
        return cad


class InterfaceServant2I(HelloGrid.InterfaceServant2):
    def __init__(self):
        print "InterfaceServant_2 constructor"

    def doMethod3(self, current=None):
        cad = "doMethod_3: sleeping 5 seconds in %s" % socket.gethostname()
        time.sleep(5)
        return cad


class ApplicationServer(Ice.Application):
    def __init__(self, service_name="Servidor"):
        print "ApplicationServer constructor"
        self.service_name = service_name

    def run(self, args):
        ic = self.communicator()
        adapter = ic.createObjectAdapter("HelloAdapter")

        serv_thread1 = InterfaceServant1I()
        ident1 = ic.stringToIdentity("ObjectIdentity1")
        adapter.add(serv_thread1, ident1)

        serv_thread2 = InterfaceServant2I()
        ident2 = ic.stringToIdentity("ObjectIdentity2")
        adapter.add(serv_thread2, ident2)

        adapter.activate()

        self.communicator().waitForShutdown()


def main():
    print "-------------------------------------------------------"
    print "launched Servant server_uno %s" % VERSION
    print "-------------------------------------------------------"

    app = ApplicationServer()

    return(app.main(sys.argv))

if __name__=="__main__":
    sys.exit(main())
