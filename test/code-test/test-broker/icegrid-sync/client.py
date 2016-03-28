#!/usr/bin/env python
import sys
import traceback
import Ice
# import IceGrid
import os
# import time
# import threading

Ice.loadSlice("contract.ice")
import HelloGrid

CONFIG_FILE = "client.cfg"
VERSION = "0.0.1"


class ApplicationClient(Ice.Application):
    def __init__(self):
        print "constructor cliente"

    def run(self, args):
        ic = self.communicator()

        try:
            e_servant1 = HelloGrid.InterfaceServant1Prx. \
                checkedCast(ic.stringToProxy("ObjectIdentity1"))
            e_servant2 = HelloGrid.InterfaceServant2Prx. \
                checkedCast(ic.stringToProxy("ObjectIdentity2"))
        except Ice.NotRegisteredException:
            print "Execpcion no registrado!!!"
            traceback.print_exc()
            return -1

        print "executing ObjectIdentity1->doMethod1"
        ret = e_servant1.doMethod1()
        print "Server response -> %s" % ret

        print "executing ObjectIdentity1->doMethod2"
        ret = e_servant1.doMethod2()
        print "Server response -> %s" % ret

        print "executing ObjectIdentity2->doMethod3"
        ret = e_servant2.doMethod3()
        print "Server response -> %s" % ret

        if (ic):
            try:
                    self.communicator().destroy()
            except:
                    traceback.print_exc()
                    status = 1
        return 0


def main():

        version = Ice.stringVersion()

        print "-----------------------------------------------"
        print "launched Client client_uno %s over Ice %s" % (VERSION, version)
        print "-----------------------------------------------"

        app = ApplicationClient()

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
