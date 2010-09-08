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

from _utils import *
import re


class DB:
	def __init__(self):
		self.series = {}
	
	def GetSeries(self, name):
		if name in self.series:
			return self.series[name]
		
		s = Series()
		s.name = name
		self.series[name] = s
		return s


class Series:
	def __init__(self):
		self.name = ''
		self.volumes = {}
	
	def GetVolume(self, name):
		if name in self.volumes:
			return self.volumes[name]
		
		v = Volume()
		v.name = name
		self.volumes[name] = v
		return v


class Volume:
	def __init__(self):
		self.name = ''
		self.issues = []
	
	def sort(self):
		# Sort by number
		def _ToFloat(x):
			try:
				return float(re.sub('[^0-9.]', '', x))
			except:
				try:
					return float(re.sub('[^0-9]', '', x))
				except:
					return ToInt(x)
		self.issues = sorted(self.issues, key=lambda book: _ToFloat(book.Number))

	
