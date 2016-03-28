# Example of Queue with maxsize:
# http://agiliq.com/blog/2013/10/producer-consumer-problem-in-python/
import Queue
import threading
import time
import signal
import random

class ThreadSafeDict(dict) :
    def __init__(self, * p_arg, ** n_arg) :
        dict.__init__(self, * p_arg, ** n_arg)
        self._lock = threading.Lock()

    def __enter__(self) :
        self._lock.acquire()
        return self

    def __exit__(self, type, value, traceback) :
        self._lock.release()

class Job(dict):
    def __init__(self, priority, description):
        dict.__init__(self)
        ctime = time.time()

        self.priority = priority

        self["jobid"] = "JID-%s.%i" % (ctime, random.randint(1, 10000))
        self["creationtime"] = ctime
        self["enquedtime"] = -1
        self["startrunningtime"] = -1
        self["endtime"] = -1
        self["priority"] = priority
        self["nodename"] = ""
        self["description"] = description
        self["status"] = ""
        return
    def __cmp__(self, other):
        return cmp(self.priority, other.priority)


def consumer_job(q):
    while True:
        # block if q es empty
        if q.empty():
            print "waiting for jobs ..."

        next_job = q.get()
        print 'Processing job %s:%s' % (next_job["jobid"], next_job["description"])
        # The count of unfinished tasks goes up whenever
        # an item is added (put) to the queue. The count
        # goes down whenever a consumer thread calls
        # task_done() to indicate that the item was
        # retrieved and all work on it is complete.
        # When the count of unfinished tasks drops to zero,
        # q.join() unblocks.
        q.task_done()
        next_job["status"] = "ended"
        next_job["endtime"] = time.time()
        endDict[next_job["jobid"]] = next_job

def producer1_job(q):
    print "producer"
    while True:
        time.sleep(5)
        q.put(Job(2, 'Mid-level'))
        q.put(Job(2, 'Mid-level'))
        q.put(Job(2, 'Mid-level'))
        q.put(Job(2, 'Mid-level'))

def producer2_job(q):
    print "producer"
    while True:
        time.sleep(10)
        q.put(Job(1, 'Important job'))


q = Queue.PriorityQueue()
endDict = ThreadSafeDict()
runDict = ThreadSafeDict()

def main():
    prod1 = threading.Thread(target=producer1_job, args=(q,))
    prod1.daemon = True
    prod1.start()

    prod2 = threading.Thread(target=producer2_job, args=(q,))
    prod2.daemon = True
    prod2.start()

    q.put(Job(10, 'Mid-level'))
    cons = threading.Thread(target=consumer_job, args=(q,))
    cons.daemon = True
    cons.start()

    try:
        while cons.is_alive():
            # debug
            for i in endDict.keys():
                print i
            cons.join(7)
    except (KeyboardInterrupt, SystemExit):
        print 'Shutting down ...'

if __name__ == '__main__':
    main()
