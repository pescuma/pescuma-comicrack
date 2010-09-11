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
import sys
import System

from _utils import *


_oldTmpFiles = []
_ComicRack = None


def _DeleteOldTmpFiles():
	global _oldTmpFiles
	for file in _oldTmpFiles:
		System.IO.File.Delete(file)
	_oldTmpFiles = []


def InitBookWrapper(ComicRack):
	global _ComicRack
	_ComicRack = ComicRack
	
	# Cleanup old temps. I need to do this better.
	_DeleteOldTmpFiles()


class BookWrapper:
	_emptyVals = { 
		'Count' : '-1', 
		'Year' : '-1', 
		'Month' : '-1', 
		'Volume' : '-1', 
		'AlternateCount' : '-1', 
		'Rating' : '0.0',
		'CommunityRating' : '0.0'
		}
	_dontConvert = set([ 
		'Pages',
		'PageCount',
		'FirstNonCoverPageIndex',
		'LastPageRead',
		'ReadPercentage',
		'OpenedCount'
		])
	_getterFields = set([ 
		'Cover',  
		'FullName', 
		'FullSeries', 
		'FullNumber',
		'FullAlternateName',
		'FullAlternateNumber',
		'FullPublisher',
		'Date'
		])
	
	def __init__(self, book):
		self.raw = book
		self._pages = {}
	
	def __dir__(self):
		ret = set()
		ret.update(set(self.__dict__))
		ret.update(dir(self.raw))
		ret.update(self._getterFields)
		return list(ret)
	
	def _safeget(self, name):
		try:
			return self._get(name)
		except:
			return ''
	
	def _get(self, name):
		return ToString(getattr(self.raw, name)).strip()
	
	def __getattr__(self, name):
		if name in self._dontConvert:
			return getattr(self.raw, name)
		
		if name in self._getterFields:
			getter = getattr(self, 'Get' + name)
			return getter()
		
		if name in self._emptyVals:
			emptVal = self._emptyVals[name]
		else:
			emptVal = ''
		
		ret = self._get(name)
		if ret == '' or ret == emptVal:
			ret = self._safeget('Shadow' + name)
		if ret == '' or ret == emptVal:
			ret = ''
		return ret
	
	def GetCover(self, width = 0, height = 0):
		coverIndex = 0 
		if self.raw.FrontCoverPageIndex > 0:
			coverIndex = self.raw.FrontCoverPageIndex
		return self.GetPage(coverIndex, width, height)
	
	def GetPage(self, page, width = 0, height = 0):
		global _oldTmpFiles
		
		if page >= self.raw.PageCount:
			return ''
		
		hash = str(page) + '_' + str(width) + '_' + str(height)
		
		if hash in self._pages:
			return self._pages[hash]
		
		self._pages[hash] = ''
		
		image = _ComicRack.App.GetComicPage(self.raw, page)
		if image is None:
			return ''

		tmpFile = System.IO.Path.GetTempFileName()
		_oldTmpFiles.append(tmpFile)

		# We need a jpg
		imageFile = tmpFile + '.jpg'
		_oldTmpFiles.append(imageFile)
		#print imageFile
		
		try:
			if width > 0 or height > 0:
				image = ResizeImage(image, width, height)
			
			image.Save(imageFile, System.Drawing.Imaging.ImageFormat.Jpeg)
			
			self._pages[hash] = imageFile
			
			return imageFile
			
		except Exception,e:
			print '[SeriesInfoPanel] Exception when saving image: ', e
			return ''
	
	def GetFullName(self):
		return CreateFullName(self.Series, self.Volume, self.Number, self.Count)
	
	def GetFullNumber(self):
		return CreateFullNumber(self.Number, self.Count)
	
	def GetFullSeries(self):
		return CreateFullSeries(self.Series, self.Volume)
	
	def GetFullAlternateName(self):
		return CreateFullAlternateName(self.AlternateSeries, self.AlternateNumber, self.AlternateCount)
	
	def GetFullAlternateNumber(self):
		return CreateFullNumber(self.AlternateNumber, self.AlternateCount)
	
	def GetFullPublisher(self):
		return CreateFullPublisher(self.Publisher, self.Imprint)
	
	def GetDate(self):
		return CreateDate(self.Month, self.Year)
