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

from fabric.api import run
from fabric.api import hide
from fabric.api import settings
from fabric.api import env
from fabric.contrib.files import exists
from fabric.decorators import task
from fabric.decorators import parallel
from fabric.api import get
from StringIO import StringIO
import time

@task
def host_type():
    # http://docs.fabfile.org/en/latest/api/core/context_managers.html
    with hide('running'):
        run("hostname")
        run("uname -a")

@task
def exec_sync(script):
    run(script)

@task
@parallel
def exec_async(script, idsession):
    with settings(user='jromanes', password='adm'):
        cmd="screen -dmS %s -p 0 %s %s" % (idsession, script, idsession)
        run(cmd, pty=False)

@task
@parallel
def waitsForCompletion(ids):
    print "waits for task completion id: %s" % ids

    with settings(user='jromanes', password='adm'):
        control_file = "/tmp/" + ids
        while True:
            if exists(control_file + "-OK", verbose=False):
                print "OK file found"
                control_file = control_file + "-OK"
                break
            elif exists(control_file + "-KO", verbose=False):
                print "Error file found"
                control_file = control_file + "-KO"
                break
            time.sleep(2)

        fd = StringIO()
        get(control_file, fd)
        content = fd.getvalue()
        run("rm -f %s" % control_file)
        return content

