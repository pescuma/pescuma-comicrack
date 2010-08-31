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

import sys
import System
import tempita
import time

from _utils import *
from _db import *
from BookWrapper import *



def GenerateHTMLForIssue(book):
	book = BookWrapper(book)
	
	issueTemplate = tempita.HTMLTemplate.from_filename(SCRIPT_DIRECTORY + 'issue.html')
	html = issueTemplate.substitute(book=book, info='')
	
	#print html
	return html




def GetIssuesRange(volume):
	ret = ''
	
	numIssues = len(volume.issues)
	
	if numIssues < 1:
		return '-'
		
	elif numIssues == 1:
		return volume.issues[0].Number
		
	else:
		firstNum = volume.issues[0].Number
		lastNum = volume.issues[-1].Number
		
		hasMillion = (lastNum == '1000000')
		if hasMillion:
			lastNum = volume.issues[-2].Number
		
		if firstNum != lastNum:
			ret = firstNum + ' to ' + lastNum
		else:
			ret = firstNum
		
		if hasMillion:
			ret += ' and 1.000.000'
		
		return ret

def GetDuplicatedIssues(volume):
	nums = set()
	ret = []
	
	for book in volume.issues:
		n = book.Number
		if n in nums:
			ret.append(n)
		else:
			nums.add(n)
	
	return ret

def GetMissingIssues(volume):
	nums = set()
	
	for book in volume.issues:
		nums.add(ToInt(book.Number))
	
	nums.discard(0)
	nums.discard(1000000)
	
	ret = []
	next = 0
	for n in sorted(nums):
		if next != 0 and n > next:
			if n > next + 2:
				ret.append(str(next) + '-' + str(n-1))
			elif n == next + 2:
				ret.append(str(next) + ' ' + str(next + 1))
			else:
				ret.append(str(next))
		next = n + 1
	
	return ret

def GetReadPercentage(volume):
	read = 0
	for book in volume.issues:
		read += ToInt(book.ReadPercentage)
	read = float(read) / len(volume.issues)
	
	# Avoid 100% when missing only one page
	if read < 99:
		return int(round(read))
	else:
		return int(read)

def GetFilesFormat(volume):
	ret = set()
	
	for book in volume.issues:
		ret.add(book.FileFormat)
	
	return sorted(ret)

def GetRating(volume, field):
	sum = 0
	count = 0

	for book in volume.issues:
		r = getattr(book, field)
		if r:
			sum += float(r)
			count += 1
	
	if count > 0:
		return "%.1f" % (sum / count)
	else:
		return None
	
def GenerateHTMLForSeries(books):
	db = DB()
	
	info = []
	
	finishTime = time.clock() + 1
	for book in books:
		book = BookWrapper(book)
		series = db.GetSeries(book.Series)
		volume = series.GetVolume(book.Volume)
		volume.issues.append(book)
		
		# Avoid look forever
		if time.clock() > finishTime:
			info.append('Stoped loading because it took too much time')
			break
	
	allSeries = []
	
	finishTime = time.clock() + 2
	for seriesKey in sorted(db.series.iterkeys()):
		series = db.series[seriesKey]
		
		s = Placeholder()
		allSeries.append(s)
		
		s.Name = series.name
		s.ShowVolumeNames = (series.volumes.keys() != [''])
		s.Volumes = []
		s.NumIssues = 0
		
		for volumeKey in sorted(series.volumes.iterkeys()):
			volume = series.volumes[volumeKey]
			
			v = Placeholder()
			s.Volumes.append(v)
			
			v.Name = volume.name
			v.Cover = volume.issues[0].Cover
			v.NumIssues = len(volume.issues)
			v.Issues = GetIssuesRange(volume)
			v.MissingIssues = GetMissingIssues(volume)
			v.DuplicatedIssues = GetDuplicatedIssues(volume)
			v.ReadPercentage = GetReadPercentage(volume)
			v.FilesFormat = GetFilesFormat(volume)
			v.Rating = GetRating(volume, "Rating")
			v.CommunityRating = GetRating(volume, "CommunityRating")
			
			s.NumIssues += v.NumIssues
		
		# Avoid look forever
		if time.clock() > finishTime:
			info.append('Stoped processing because it took too much time')
			break
	
	seriesTemplate = tempita.HTMLTemplate.from_filename(SCRIPT_DIRECTORY + 'series.html')
	html = seriesTemplate.substitute(allSeries=allSeries, info=info)
	
	#print html
	return html



#@Name Series Info Panel
#@Hook ComicInfoHtml
#@Enabled true
#@Description Show information about selected series
def SeriesHtmlInfoPanel(books):
	InitBookWrapper(ComicRack)
	
	numBooks = len(books)
	if numBooks < 1:
		return ''
	elif numBooks == 1:
		return GenerateHTMLForIssue(books[0])
	else:
		return GenerateHTMLForSeries(books)

