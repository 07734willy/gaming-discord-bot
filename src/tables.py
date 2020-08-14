from collections import UserDict
import pickle
import os

class KVStore(UserDict):
	def __init__(self, path):
		super().__init__()
		self.path = path
		self.read()

	def __setitem__(self, key, value):
		super().__setitem__(key, value)
		self.write()

	def read(self):
		if os.path.exists(self.path):
			with open(self.path, 'rb') as f:
				self.data = pickle.load(f)

	def write(self):
		with open(self.path, 'wb') as f:
			pickle.dump(self.data, f)

ROLE_JOIN_MSGS = KVStore('./tables/role-joins.pkl')
