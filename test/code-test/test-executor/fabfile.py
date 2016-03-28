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
    with settings(user='javi', password='adm'):
    #with hide('running'):
        run("hostname")
        run("uname -a")
        run("id")

@task
def exec_sync(script):
    run(script)

@task
@parallel
def exec_async(script, idsession):
    cmd="screen -dmS %s -p 0 %s %s" % (idsession, script, idsession)
    run(cmd, pty=False)

@task
@parallel
def waitsForCompletion(ids):
    print "waits for task completion id: %s" % ids

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

