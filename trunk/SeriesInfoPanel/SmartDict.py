"""
Copyright (C) 2010 Ricardo Pescuma Domenecci

This is free software; you can redistribute it and/or
modify it under the terms of the GNU Library General Public
License as published by the Free Software Foundation; either
version 2 of the License, or (at your option) any later version.

This is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Library General Public License for more details.

You should have received a copy of the GNU Library General Public
License along with this file; see the file license.txt.  If
not, write to the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.
"""

class SmartDict:
	def __init__(self, other=None):
		if other:
			self._objects = list(other._objects)
			self._dict = other._dict.copy()
		else:
			self._objects = []
			self._dict = {}
	
	def addAttributes(self, obj):
		self._objects.append(obj)

	def get(self, key, default = None):
		if key in self._dict:
			return self._dict[key]
		
		for obj in self._objects:
			val = getattr(obj, key, None)
			if not val is None:
				return val
		
		return default
	
	def set(self, key, value):
		self._dict[key] = value
	
	def keys(self):
		fields = set(self._dict.keys())
		
		for obj in self._objects:
			if callable(getattr(obj, '__dir__')):
				members = obj.__dir__()
			else:
				members = dir(obj)
			
			for m in members:
				if m[0] == '_':
					continue
				if m in fields:
					continue
				if not hasattr(obj, m):
					continue
				if callable(getattr(obj, m)):
					continue
				fields.add(m)
		
		return list(fields)
	
	def values(self):
		ret = []
		for key in self.keys():
			ret.append(self.get(key))
		return ret
	
	def items(self):
		ret = []
		for key in self.keys():
			ret.append([ key, self.get(key) ])
		return ret
	
	def update(self, other):
		self._dict.update(other)
	
	def has_key(self, key):
		return key in self.keys()
	
	def clear(self):
		self._objects.clear()
		self._dict.clear()
	
	def copy(self):
		return SmartDict(self)
	
	def __getitem__(self, key):
		ret = self.get(key, None)
		if ret is None:
			raise KeyError, key
		return ret
	
	def __setitem__(self, key, value):
		return self.set(key, value)
	
	def __contains__(self, key):
		return self.has_key(key)
	
	def __len__(self):
		return len(self.keys())
	
	# TODO
	
	def iterkeys(self):
		return self.keys()
	def itervalues(self):
		return self.values()
	def iteritems(self):
		return self.items()
	


