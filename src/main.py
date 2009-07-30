# -*- coding: utf-8 -*-

import sys
import re
import mobimail.filters
import traceback
from threadpool import ThreadPool, WorkRequest

def exception_handler(request, exc_info):
	traceback.print_tb(exc_info[2], file=sys.stderr)
	print "* Exception: %s" % str(exc_info[0])

def print_result(request, result):
	print " ".join(result)

def main():
	poolsize = 8
	pool = ThreadPool(poolsize)
	while 1:
		line = sys.stdin.readline().strip()
		if not line:
			break
		
		parts = line.split(" ")
		id = parts[0]
		command = parts[1]
		
		quit_re = re.compile(r'^quit$', re.IGNORECASE)
		intf_re = re.compile(r'^intf$', re.IGNORECASE)
		key_re = re.compile(r'^key$', re.IGNORECASE)
		not_file_re = re.compile(r'^file', re.IGNORECASE)
		
		if (quit_re.match(command) != None):
			pool.joinAllDismissedWorkers()
			pool.wait()
			print "%s OK" % id
			continue
		
		if (intf_re.match(command) != None):
			print "%s INTF 3" % id
			continue
			
		if (key_re.match(command) != None):
			print "%s OK" % id
			break
			
		if (not_file_re.match(command) == None):
			print "%s FAILURE" % id
			continue

		file = parts[2]
		
		request = WorkRequest(mobimail.filters.bogus, [id, file], None, None, print_result, exception_handler)
		pool.putRequest(request)
				

if __name__ == '__main__':
	main()