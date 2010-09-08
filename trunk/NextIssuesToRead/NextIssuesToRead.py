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

import time

from _utils1 import *
from _db1 import *


def GetSeries(book):
	if book.Series:
		return book.Series
	else:
		return book.ShadowSeries
def GetVolume(book):
	if book.Volume:
		return book.Volume
	else:
		return book.ShadowVolume
def GetNumber(book):
	if book.Number:
		return book.Number
	else:
		return book.ShadowNumber


def StartedReading(book):
	return book.OpenedCount > 0 and (book.ReadPercentage > 50 or book.LastPageRead >= book.FrontCoverPageIndex + 3)

def HasStartedReadIssue(volume):
	for issue in volume.issues:
		if StartedReading(issue):
			return True
	return False


#@Name	 Next issues to read
#@Hook	 CreateBookList
#@PCount 0
#@Enabled true
#@Description List next books to read in series that you already started reading
def NextIssuesToRead(books, a, b):
	db = DB()
	
	#print '[NextIssuesToRead] Loading books from db'
	#dt = time.clock()
	
	# Load books
	for book in books:
		series = db.GetSeries(GetSeries(book))
		volume = series.GetVolume(GetVolume(book))
		volume.issues.append(book)
	
	#dt = time.clock() - dt
	#print '[NextIssuesToRead] Loaded in ', dt, 's'
	
	#print '[NextIssuesToRead] Removing not read volumes'
	#dt = time.clock()
	
	# Remove volumes that have not book marked as started read
	for series in db.series.itervalues():
		toremove = []
		
		for volumeKey in series.volumes.iterkeys():
			volume = series.volumes[volumeKey]
			
			if not HasStartedReadIssue(volume):
				toremove.append(volumeKey)
		
		for volumeKey in toremove:
			del series.volumes[volumeKey]
	
	#dt = time.clock() - dt
	#print '[NextIssuesToRead] Removed in ', dt, 's'
	
	#print '[NextIssuesToRead] Sorting issues'
	#dt = time.clock()
	
	# Sort
	for series in db.series.itervalues():
		for volume in series.volumes.itervalues():
			volume.sort()
	
	#dt = time.clock() - dt
	#print '[NextIssuesToRead] Sorted in ', dt, 's'
	
	#print '[NextIssuesToRead] Finding next ones to read'
	#dt = time.clock()

	# Generate list
	ret = []
	for series in db.series.itervalues():
		for volume in series.volumes.itervalues():
			addNext = False
			for book in volume.issues:
				if StartedReading(book):
					if book.ReadPercentage == 100:
						addNext = True
					else:
						ret.append(book)
						addNext = False
				else:
					if addNext:
						ret.append(book)
						addNext = False
	
	#dt = time.clock() - dt
	#print '[NextIssuesToRead] Generated list in ', dt, 's'
	
	return ret
