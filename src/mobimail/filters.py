# -*- coding: utf-8 -*-

import time
import shutil

def inspector(id, file):
	TARGET = "/usr/local/bin/queuefiles"
	shutil.copy(file, TARGET)
	return [id, 'OK']

def bogus(id, file):
	print("* Processing %s" % file)
	time.sleep(1)
	return [id, 'OK']
