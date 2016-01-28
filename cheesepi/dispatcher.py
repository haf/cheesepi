#!/usr/bin/env python

import os
import time
import math
import sys
import sched
import multiprocessing
import logging

import cheesepi as cp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

start_time = time.time()

dao    = cp.config.get_dao()
config = cp.config.get_config()
logger = cp.config.get_logger(__name__)

# Create scheduler object, use 'real' time
s = sched.scheduler(time.time, time.sleep)
repeat_schedule = True # keep rescheuling?
# list of tasks to perform each schedule (populate later)
schedule_list = []

pool = None # pool must be global, yet instantiated in __main__
pool_size = 5

# Task priority
IMPORTANT  = 1
NORMAL	   = 2

results = []
def log_result(result):
	logging.info("Logging task result..."+str(result))
	results.append(result)
def timestamp(): return (time.time()-start_time)
def print_queue(): logger.debug(s.queue)

# Need to catch Ctrl+C, and so wrap the Interupt as an Exception
def async(task):
	"""Wrapper around asynchronous task execution"""
	try:
		task.run()
	except KeyboardInterrupt:
		pass # probably just user destruction
	except:
		cls, exc, tb = sys.exc_info()
		if issubclass(cls, Exception):
			raise # No worries, pass up the stack
		# Need to wrap the exception with something multiprocessing will recognise
		import traceback
		print "Unhandled exception %s (%s):\n%s" % (cls.__name__, exc, traceback.format_exc())
		logger.error("Unhandled exception %s (%s):\n%s" % (cls.__name__, exc, traceback.format_exc()))
		raise Exception("Unhandled exception: %s (%s)" % (cls.__name__, exc))

# Perform a scheduled Task, and schedule the next
def run(task, spec):
	"""Run this task asychronously, and schedule the next period"""
	logger.info("\nRunning %s @ %f" % (task.spec['taskname'], timestamp()))
	pool.apply_async(async, args=[task], callback=log_result)
	if repeat_schedule:
		schedule_task(spec)


def schedule_task(spec):
	"""Ensure task defiend by specificaiton is executed"""
	task = cp.utils.build_task(dao, spec)
	if task == None:
		logger.error("Task specification not valid: "+str(spec))
		return

	next_period = 1 + math.floor(time.time() / task.spec['period'])
	abs_start = (next_period*task.spec['period']) + task.spec['offset']
	delay = abs_start-time.time()
	#logger.debug("Time calculations: %d\t%f\t%f" % (next_period,abs_start,delay))
	# queue up a task, include spec for next period
	s.enter(delay, NORMAL, run, [task, spec])

def get_queue():
	"""return list of queued task objects"""
	q=[]
	for t in s.queue:
		start_time = t.time
		# extract the dict of the first parameter to the event
		spec = t.argument[0].toDict()
		spec['start_time'] = start_time
		q.append(spec)
	return q

def load_schedule():
	"""Load a schedule of task specifications"""
	#try to get from central server
	tasks = None # cp.config.load_remote_schedule()
	if tasks==None:
		# just use local
		tasks = cp.config.load_local_schedule()
	return tasks

def print_schedule(schedule_list):
	print "Using the following schedule:"
	for t in schedule_list:
		print t


def start():
	schedule_list = load_schedule()
	print_schedule(schedule_list)
	pool = multiprocessing.Pool(processes=pool_size)

	# reschedule all tasks from the schedule specified in config file
	for t in schedule_list:
		schedule_task(t)
	s.run()

	if pool is not None:
		pool.close()
		pool.join()

	# wait for the longest time between tasks
	max_period = 10000
	time.sleep(max_period)

if __name__ == "__main__":
	logger.info("Dispatcher PID: %d" % os.getpid())
	start()


