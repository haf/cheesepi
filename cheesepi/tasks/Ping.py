import sys
import time
import os
import re
import logging
import socket
from subprocess import Popen, PIPE

sys.path.append("/usr/local/")
import cheesepi.utils
import Task

class Ping(Task.Task):

	# construct the process and perform pre-work
	def __init__(self, dao, spec):
		Task.Task.__init__(self, dao, spec)
		self.spec['taskname']    = "ping"
		if not 'ping_count'  in self.spec: self.spec['ping_count']  = 10
		if not 'packet_size' in self.spec: self.spec['packet_size'] = 64
		socket.gethostbyname(self.spec['landmark']) # we dont care, just populate the cache

	# actually perform the measurements, no arguments required
	def run(self):
		print "Pinging: %s @ %f, PID: %d" % (self.spec['landmark'], time.time(), os.getpid())
		self.measure()

	# measure and record funtion
	def measure(self):
		start_time = cheesepi.utils.now()
		op_output = self.perform(self.spec['landmark'], self.spec['ping_count'], self.spec['packet_size'])
		end_time = cheesepi.utils.now()
		#print op_output

		parsed_output = self.parse_output(op_output, self.spec['landmark'],
			start_time, end_time, self.spec['packet_size'], self.spec['ping_count'])
		self.dao.write_op(self.spec['taskname'], parsed_output)

	#ping function
	def perform(self, landmark, ping_count, packet_size):
		packet_size -= 8 # change packet size to payload length!
		execute = "ping -c %s -s %s %s"%(ping_count, packet_size, landmark)
		logging.info("Executing: "+execute)
		print execute
		result = Popen(execute ,stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
		ret = result.stdout.read()
		result.stdout.flush()
		return ret

	#read the data from ping and reformat for database entry
	def parse_output(self, data, landmark, start_time, end_time, packet_size, ping_count):
		self.spec["start_time"]  = start_time
		self.spec["end_time"]    = end_time
		delays=[]

		lines = data.split("\n")
		first_line = lines.pop(0).split()
		self.spec["destination_domain"]  = first_line[1]
		self.spec["destination_address"] = re.sub("[()]", "", str(first_line[2]))

		delays = [-1.0] * ping_count# initialise storage
		for line in lines:
			if "time=" in line: # is this a PING return line?
				# does the following string wrangling always hold? what if not "X ms" ?
				# also need to check whether we are on linux-like or BSD-like ping
				if "icmp_req" in line: # BSD counts from 1
					sequence_num = int(re.findall('icmp_.eq=[\d]+ ',line)[0][9:-1]) -1
				elif "icmp_seq" in line: # Linux counts from 0
					sequence_num = int(re.findall('icmp_.eq=[\d]+ ',line)[0][9:-1])
				else:
					logging.error("ping parse error:"+line)
					exit(1)
				delay = re.findall('time=.*? ms',line)[0][5:-3]
				# only save returned pings!
				delays[sequence_num-1]=float(delay)
			elif "packet loss" in line:
				loss = re.findall('[\d]+% packet loss',line)[0][:-13]
				self.spec["packet_loss"] = float(loss)
			elif "min/avg/max/" in line:
				fields = line.split()[3].split("/")
				self.spec["minimum_RTT"] = float(fields[0])
				self.spec["average_RTT"] = float(fields[1])
				self.spec["maximum_RTT"] = float(fields[2])
				self.spec["stddev_RTT"]  = float(fields[3])

		self.spec['delays']     = str(delays)
		self.spec['uploaded']   = self.spec['packet_size'] * self.spec['ping_count']
		self.spec['downloaded'] = 8 * self.spec['ping_count']
		return self.spec

if __name__ == "__main__":
	#general logging here? unable to connect etc
	dao = cheesepi.config.get_dao()

	#parameters = {'landmark':'google.com','ping_count':10,'packet_size':64}
	spec = {'landmark':'google.com'}
	ping_task = Ping(dao, spec)
	ping_task.run()
	print ping_task.spec

