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

import time
import signal
import random

class Job(dict):
    def __init__(self, priority, description, ips):
        dict.__init__(self)
        ctime = time.time()

        self.priority = priority
        self.ips = ips

        self["jobid"] = "JID-%s.%i" % (ctime, random.randint(1, 10000))
        self["creationtime"] = ctime
        self["enquedtime"] = -1
        self["startrunningtime"] = -1
        self["endtime"] = -1
        self["priority"] = priority
        self["nodename"] = ""
        self["description"] = description
        self["iplist"] = ips
        self["status"] = ""
        self["stdout"] = ""
        self["stderr"] = ""
        return
    def __cmp__(self, other):
        return cmp(self.priority, other.priority)
