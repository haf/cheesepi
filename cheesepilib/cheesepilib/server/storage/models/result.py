from __future__ import unicode_literals, absolute_import

from cheesepilib.exceptions import UnsupportedResultType

class Result(object):

	@classmethod
	def fromDict(cls, peer_id, dct):
		name = dct['task_name']

		from .PingResult import PingResult
		if name == 'ping': return PingResult.fromDict(peer_id, dct)
		else: raise UnsupportedResultType("Unknown task type '{}'.".format(name))

	def toDict(self):
		raise NotImplementedError("Abstract method 'toDict' not implemented.")

	def get_taskname(self):
		raise NotImplementedError("Abstract method 'taskname' not implemented.")

	def get_target(self):
		raise NotImplementedError("Abstract method 'get_target' not implemented.")