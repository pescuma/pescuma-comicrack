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

import clr
clr.AddReference('System.Drawing')
import System

oldTmpFiles = []

def DeleteOldTmpFiles():
	global oldTmpFiles
	for file in oldTmpFiles:
		System.IO.File.Delete(file)
	oldTmpFiles = []

def html_encode(text):
	html_encode_table = {
		"&": "&amp;",
		'"': "&quot;",
#		"'": "&apos;",
		">": "&gt;",
		"<": "&lt;",
		}
	return "".join(html_encode_table.get(c,c) for c in text)

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
		
		for issue in self.issues:
			n = GetNumber(issue)
			if n in nums:
				ret.append(n)
			else:
				nums.add(n)
		
		return ret
	
	def GetMissingIssues(self):
		nums = set()
		
		for issue in self.issues:
			nums.add(GetNumberInt(issue))
		
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

def FirstNotEmpty(*args):
	for x in args:
		if x != '':
			return x
	return ''

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
	
	print coverFile
	
	try:
		image = ResizeImage(image, height)
		image.Save(coverFile, System.Drawing.Imaging.ImageFormat.Jpeg)
		return coverFile
	except Exception,e:
		print 'Exception when saving: ', e
		return ''


#@Name Series Info Panel
#@Hook ComicInfoHtml
#@Enabled true
#@Description Show information about selected series
def SeriesHtmlInfoPanel(books):
	# Cleanup old temps. I need to do this better.
	DeleteOldTmpFiles()
	
	db = DB()
	
	for book in books:
		series = db.GetSeries(GetSeriesName(book))
		volume = series.GetVolume(GetVolumeName(book))
		volume.issues.append(book)
	
	html = []
	
	for seriesKey in sorted(db.series.iterkeys()):
		series = db.series[seriesKey]
		
		html.append('<h1>' + html_encode(FirstNotEmpty(series.name, '<Unknown series>')) + '</h1>')
		
		showVolumeNames = (series.volumes.keys() != [''])
		
		html.append('<table border="0px" cellspacing="20px">')
		
		for volumeKey in sorted(series.volumes.iterkeys()):
			volume = series.volumes[volumeKey]
			html.append('<tr>')
			
			# Left column
			html.append('<td width="1px" valign="top">')
			
			# Cover
			cover = GetCoverImagePath(volume.issues[0], 120)
			if cover != '':
				html.append('<img src="' + html_encode(cover) + '" />')
			
			html.append('</td>')
			
			# Right column
			html.append('<td valign="top">')
			
			# Volume
			if showVolumeNames:
				html.append('<h2>Volume ' + html_encode(FirstNotEmpty(volume.name, '<Unknown>')) + '</h2>')
			
			# Issues
			nums = GetNumber(volume.issues[0])
			lastNum = GetNumber(volume.issues[-1])
			if nums != lastNum:
				nums += ' to ' + lastNum
			html.append('<b>Issues:</b> ' + html_encode(nums) + '<br />')
			
			# Missing issues
			missingIssues = volume.GetMissingIssues()
			if len(missingIssues) > 0:
				html.append('<b>Missing issues:</b> ' + html_encode(' '.join(missingIssues)) + '<br />')
			
			# Duplicated issues
			duplicatedIssues = volume.GetDuplicatedIssues()
			if len(duplicatedIssues) > 0:
				html.append('<b>Duplicated issues:</b> ' + html_encode(' '.join(duplicatedIssues)) + '<br />')
						
			html.append('</td>')
			
			html.append('</tr>')
		
		html.append('</table>')
	
	html = '\n'.join(html)
	#print html
	return html
