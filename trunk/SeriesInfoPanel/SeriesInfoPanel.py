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

_SCRIPT_DIRECTORY =  __file__[:-len('SeriesInfoPanel.py')] 

import sys
sys.path.append(_SCRIPT_DIRECTORY + 'stdlib')
import clr
clr.AddReference('System.Drawing')

import System
import tempita
import time


# Globals
oldTmpFiles = []
seriesTemplate = tempita.HTMLTemplate.from_filename(_SCRIPT_DIRECTORY + 'series.tmpl')


def DeleteOldTmpFiles():
	global oldTmpFiles
	for file in oldTmpFiles:
		System.IO.File.Delete(file)
	oldTmpFiles = []

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
	
	def GetDuplicatedIssues(self):
		nums = set()
		ret = []
		
		for book in self.issues:
			n = GetNumber(book)
			if n in nums:
				ret.append(n)
			else:
				nums.add(n)
		
		return ret
	
	def GetMissingIssues(self):
		nums = set()
		
		for book in self.issues:
			nums.add(GetNumberInt(book))
		
		nums.discard(0)
		
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
		for book in self.issues:
			read += book.ReadPercentage
		read = float(read) / len(self.issues)
		
		# Avoid 100% when missing only one page
		if read < 99:
			return int(round(read))
		else:
			return int(read)

def GetSeriesName(book):
	ret = book.Series.strip()
	if ret == '':
		ret = book.ShadowSeries.strip()
	if ret == '':
		ret = ''
	return ret

def GetVolumeName(book):
	ret = str(book.Volume)
	if ret == '' or ret == '-1':
		ret = str(book.ShadowVolume)
	if ret == '' or ret == '-1':
		ret = ''
	return ret

def GetNumber(book):
	ret = book.Number.strip()
	if ret == '':
		ret = book.ShadowNumber.strip()
	return ret

def GetNumberInt(book):
	ret = GetNumber(book)
	if ret.isdigit():
		return int(ret)
	else:
		return 0

def ResizeImage(image, height):
	result = System.Drawing.Bitmap(image.Width * height / image.Height, height)
	
	graphics = System.Drawing.Graphics.FromImage(result)
	graphics.CompositingQuality = System.Drawing.Drawing2D.CompositingQuality.HighQuality
	graphics.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.HighQualityBicubic
	graphics.SmoothingMode = System.Drawing.Drawing2D.SmoothingMode.HighQuality
	graphics.DrawImage(image, 0, 0, result.Width, result.Height)
	
	return result

def GetCoverImagePath(book, height):
	global oldTmpFiles
	
	coverIndex = 0 
	if book.FrontCoverPageIndex > 0:
		coverIndex = book.FrontCoverPageIndex
	image = ComicRack.App.GetComicPage(book, coverIndex)
	
	if image is None:
		return ''

	coverFile = System.IO.Path.GetTempFileName()
	oldTmpFiles.append(coverFile)

	# We need a jpg
	coverFile += '.jpg'
	oldTmpFiles.append(coverFile)
	
	#print coverFile
	
	try:
		image = ResizeImage(image, height)
		image.Save(coverFile, System.Drawing.Imaging.ImageFormat.Jpeg)
		return coverFile
	except Exception,e:
		print '[SeriesInfoPanel] Exception when saving image: ', e
		return ''

class Placeholder:
	pass

#@Name Series Info Panel
#@Hook ComicInfoHtml
#@Enabled true
#@Description Show information about selected series
def SeriesHtmlInfoPanel(books):
	# Cleanup old temps. I need to do this better.
	DeleteOldTmpFiles()
	
	db = DB()
	
	info = []
	
	finishTime = time.clock() + 1
	for book in books:
		series = db.GetSeries(GetSeriesName(book))
		volume = series.GetVolume(GetVolumeName(book))
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
		
		s.name = series.name
		s.showVolumeNames = (series.volumes.keys() != [''])
		s.volumes = []
		
		for volumeKey in sorted(series.volumes.iterkeys()):
			volume = series.volumes[volumeKey]
			
			v = Placeholder()
			s.volumes.append(v)
			
			v.name = volume.name
			v.cover = GetCoverImagePath(volume.issues[0], 120)
			
			firstNum = GetNumber(volume.issues[0])
			lastNum = GetNumber(volume.issues[-1])
			if firstNum != lastNum:
				v.issues = firstNum + ' to ' + lastNum
			else:
				v.issues = firstNum
			
			v.missingIssues = volume.GetMissingIssues()
			v.duplicatedIssues = volume.GetDuplicatedIssues()
			v.readPercentage = volume.GetReadPercentage()
		
		# Avoid look forever
		if time.clock() > finishTime:
			info.append('Stoped processing because it took too much time')
			break

	seriesTemplate = tempita.HTMLTemplate.from_filename(_SCRIPT_DIRECTORY + 'series.tmpl')
	html = seriesTemplate.substitute(allSeries=allSeries, info=info)
	
	#print html
	return html
