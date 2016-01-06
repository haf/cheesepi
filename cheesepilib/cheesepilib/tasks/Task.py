import json

# To be subclassed by explicit measurement tasks
class Task:

	def __init__(self, dao, spec):
		self.dao                = dao
		self.spec               = {}
		self.spec['taskname']   = "Superclass"
		self.spec['cycle']      = 0 # deprecated
		self.spec['period']     = 3600 # hourly
		self.spec['offset']     = 0
		self.spec['downloaded'] = 1 # bytes, placeholder
		self.spec['uploaded']   = 1 # bytes, placeholder
		# overwrite defauls:
		for s in spec.keys():
			self.spec[s] = spec[s]

	def toDict(self):
		return self.spec

	def toJson(self):
		return json.dumps(self.toDict())

	# this will be overridden by subclasses
	def run(self):
		print "Task not doing anything..."