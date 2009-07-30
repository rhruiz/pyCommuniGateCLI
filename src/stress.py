# -*- coding: utf-8 -*-

import traceback
from threadpool import ThreadPool, WorkRequest
from subprocess import *
import sys


def exception_handler(request, exc_info):
	traceback.print_tb(exc_info[2], file=sys.stderr)
	print "* Exception: %s" % str(exc_info[0])

def print_result(request, result):
	print " ".join(result)

class Helper:
	proc = None
	klass = "com.mobimail.thread.HiddenCC"

	@classmethod
	def start(self):
		cmd = "/usr/bin/java -jar /usr/local/bin/jhelper.jar /etc/jhelper.conf %s" % Helper.klass
		Helper.proc = Popen(cmd, shell=True, stdin=PIPE, close_fds=True)

    @classmethod
    def terminate(self):
        Helper.proc.terminate()

def handler(num, frame):
	os.kill(Helper.proc.pid, signal.SIGTERM)
	
def main():
    poolsize = 8
	pool = ThreadPool(poolsize)

    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGQUIT, handler)

    try:
    	Helper.start()
    except Exception, ex:
        Helper.terminate()
    	print "* Terminating: {%s}" % ex.__class__
    	sys.exit(1)
	
	id = 0
	
	while 1:
	    for i in rage(0, poolsize):
	        id = id + 1
	        
            import socket,os

            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.connect("/var/tmp/socket-%s" % Helper.klass)
            s.send("%d FILE /usr/local/bin/message.msg" % id) 
            data = s.recv(1024)
            s.close()
            print 'Received', repr(data)
    	    
    code = os.waitpid(Helper.proc.pid, 0)


if __name__ == '__main__':
    main()
