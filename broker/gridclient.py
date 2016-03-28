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
import time
import sys
import os
import traceback
import threading
import Ice
import json

Ice.loadSlice('broker/contract.ice')
import RemoteExecution
from job import Job

# import view
# import config
# from view import render

# URL structure: Regular expression that matches
# an URL + name of class which will handle the request.
urls = (
    #
    # SGT1 stuff
    #
    '/apagar', 'apagar',
    '/reiniciar', 'reiniciar',
    #
    # General stuff
    #
    '/debug', 'debug',    # get summary of system
    '/status', 'status',  # get status of JobID
    '/abort', 'abort',    # empty runQueue
    '/test', 'test',      # development testing stage
    '/', 'index'          # web front-end for testing, health tests.
)

# Dirty trick for global REST classes
runQueue = None
endDict = None

class apagar:
    def POST(self):
        data = web.input(ip=[])
        j = Job(5, 'apagar dispositivo', data.ip)
        runQueue.put(j)
        return j["jobid"]

class status:
    def GET(self):
        data = web.input()
        print data.jobid
        if endDict.has_key(data.jobid):
            retJson = endDict[data.jobid]
            del endDict[data.jobid]
            return json.dumps(retJson)
        else:
            return "running"

class test:
    def POST(self):
        data = web.input(ip=[])
        for i in data.ip:
            print i
        return 1

class debug:
    def GET(self):
        retJson = {'End Jobs':len(endDict)}
        return json.dumps(retJson)

# Ready for web testing front-end
# class index:
#    def GET(self):
#        i = web.input(name=None)
#        return render.index(i.name)


class Callback(Ice.Object):
    def __init__(self, application):
        self.app_reference = application
        self._job = application._job
        self._endDict = application._endDict

    def response(self, result, other):
        self.app_reference.cond.acquire()
        try:

            self._job["status"] = "ended"
            self._job["endtime"] = time.time()
            self._job["nodename"] = other

            print self._job["jobid"]
            print "return [%s]" % result

            self._endDict[self._job["jobid"]] = self._job

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
        def __init__(self, rqueue, edict):
            print "constructor cliente"
            self.jobs = 0
            global runQueue
            global endDict
            runQueue = rqueue
            self._endDict = edict
            endDict = self._endDict
            self._job = None
            # condition variable
            self.cond = threading.Condition()

        def launchCommand(self, job):
            self._job = job
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
                    #
                    # Real call to Ice remote worker with the
                    # relevant parameter to do the real work
                    # in remote hosts devices.
                    #
                    cb = Callback(self)
                    r = e_servant.begin_sendGridCommand(job["jobid"],
                                                        job["iplist"],
                                                        cb.response,
                                                        cb.exception)
                    self.jobs += 1
                    print 'Processing async job %s: %s' % (job["jobid"],
                                                           job["description"])
                finally:
                    self.cond.release()
            except:
                    traceback.print_exc()
                    return False

            return True

        def run(self, args):
            # WebService entry point.
            webapp = web.application(urls, globals())
            webapp.internalerror = web.debugerror
            # https://github.com/webpy/webpy/issues/21
            web.httpserver.runsimple(webapp.wsgifunc(), ("0.0.0.0", 8888))

        def submitgrid(self, job):
            print "[NEW job]"

            self.launchCommand(job)

