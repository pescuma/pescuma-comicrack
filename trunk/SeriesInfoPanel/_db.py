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


class DB:
	def __init__(self):
		self.series = {}
	
	def GetSeries(self, book):
		name = book.Series
		
		if name in self.series:
			return self.series[name]
		
		s = Series()
		s.name = name
		self.series[name] = s
		return s


class Series:
	def __init__(self):
		self.Name = ''
		self.Volumes = {}
	
	def GetVolume(self, book):
		name = book.Volume
		format = book.Format
		tmp = name + ' | ' + format
		
		if tmp in self.Volumes:
			return self.Volumes[tmp]
		
		v = Volume()
		v.Name = name
		v.Format = format
		self.Volumes[tmp] = v
		return v


class Volume:
	def __init__(self):
		self.Name = ''
		self.Format = ''
		self.Issues = []
	
	def sort(self):
		# Sort by number
		self.Issues = sorted(self.Issues, key=lambda book: ToFloat(book.Number))
	
	def StartedReading(self):
		for book in self.Issues:
			if StartedReadingIssue(book):
				return True
		return False
	
	# You must sort before calling this one
	def GetNextIssuesToRead(self):
		ret = []
		
		if len(self.Issues) > 0 and not StartedReadingIssue(self.Issues[0]):
			ret.append(self.Issues[0])
		
		addNext = False
		for book in self.Issues:
			if StartedReadingIssue(book):
				if book.ReadPercentage == 100:
					addNext = True
				else:
					ret.append(book)
					addNext = False
			else:
				if addNext:
					ret.append(book)
					addNext = False
		
		return ret

	def GetIssuesRange(self):
		ret = ''
		
		numIssues = len(self.Issues)
		
		if numIssues < 1:
			return '-'
			
		elif numIssues == 1:
			return self.Issues[0].Number
			
		else:
			firstNum = self.Issues[0].Number
			lastNum = self.Issues[-1].Number
			
			hasMillion = (lastNum == '1000000')
			if hasMillion:
				lastNum = self.Issues[-2].Number
			
			if firstNum != lastNum:
				ret = Translate("IssueRange",  "%(first)s to %(last)s")  % { 'first': firstNum, 'last': lastNum } 
			else:
				ret = firstNum
			
			if hasMillion:
				ret = Translate("AndMillion",  "%(Issues)s and 1.000.000")  % { 'Issues': ret }
			
			return ret

	def GetIssuesCount(self):
		ret = ''
		
		for book in self.Issues:
			if book.Count:
				if ret and ret != book.Count:
					return ''
				ret = book.Count
		
		return ret

	def GetDuplicatedIssues(self):
		nums = set()
		ret = []
		
		for book in self.Issues:
			n = book.Number
			if n in nums:
				ret.append(n)
			else:
				nums.add(n)
		
		return ret

	def GetMissingIssues(self):
		nums = set()
		
		for book in self.Issues:
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

	def GetReadPercentage(self):
		read = 0
		for book in self.Issues:
			read += ToInt(book.ReadPercentage)
		read = float(read) / len(self.Issues)
		
		# Avoid 100% when missing only one page
		if read < 99:
			return int(round(read))
		else:
			return int(read)

	def GetFilesFormat(self):
		ret = set()
		
		for book in self.Issues:
			ret.add(book.FileFormat)
		
		return sorted(ret)

	def GetAvgRating(self, field):
		sum = 0
		count = 0

		for book in self.Issues:
			r = getattr(book, field)
			if r:
				sum += float(r)
				count += 1
		
		if count > 0:
			return "%.1f" % (sum / count)
		else:
			return None

	def GetRating(self):
		return self.GetAvgRating("Rating")
		
	def GetCommunityRating(self):
		return self.GetAvgRating("CommunityRating")

	def GetPublishersImprints(self):
		ret = set()
		
		class PublisherImprint:
			def __init__(self):
				self.Publisher = ''
				self.Imprint = ''
			def __hash__(self):
				return self.Publisher.__hash__() + self.Imprint.__hash__()
			def __cmp__(self, other):
				if self.Publisher != other.Publisher:
					return -1 if self.Publisher < other.Publisher else 1
				if self.Imprint != other.Imprint:
					return -1 if self.Imprint < other.Imprint else 1
				return 0
		
		for book in self.Issues:
			pi = PublisherImprint()
			pi.Publisher = book.Publisher
			pi.Imprint = book.Imprint
			if pi.Publisher or pi.Imprint:
				ret.add(pi)
		
		return sorted(ret)

	def GetPublishers(self):
		ret = set()
		
		for book in self.Issues:
			if book.Publisher:
				ret.add(book.Publisher)
		
		return sorted(ret)

	def GetImprints(self):
		ret = set()
		
		for book in self.Issues:
			if book.Imprint:
				ret.add(book.Imprint)
		
		return sorted(ret)

#	def GetFormats(self):
#		ret = set()
#		
#		for book in self.Issues:
#			if book.Format:
#				ret.add(book.Format)
#			else:
#				ret.add(Translate('Series'))
#		
#		return sorted(ret)

	# Properties
	
	NextIssuesToRead = property(GetNextIssuesToRead)
	IssuesRange = property(GetIssuesRange)
	DuplicatedIssues = property(GetDuplicatedIssues)
	MissingIssues = property(GetMissingIssues)
	ReadPercentage = property(GetReadPercentage)
	FilesFormat = property(GetFilesFormat)
	Rating = property(GetRating)
	CommunityRating = property(GetCommunityRating)
	PublishersImprints = property(GetPublishersImprints)
	Publishers = property(GetPublishers)
	Imprints = property(GetImprints)
	IssuesCount = property(GetIssuesCount)
	
