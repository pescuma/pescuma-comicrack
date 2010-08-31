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
	_dontConvert = set([ 'Pages' ])
	
	def __init__(self, book):
		self.raw = book
		self._cover = {}
	
	def _get(self, name):
		try:
			return ToString(getattr(self.raw, name)).strip()
		except:
			return ''
	
	def __getattr__(self, name):
		if name in self._dontConvert:
			return getattr(self.raw, name)
		
		if name == 'Cover':
			return self.GetCover()
		
		if name in self._emptyVals:
			emptVal = self._emptyVals[name]
		else:
			emptVal = ''
			
		ret = self._get(name)
		if ret == '' or ret == emptVal:
			ret = self._get('Shadow' + name)
		if ret == '' or ret == emptVal:
			ret = ''
		return ret
	
	def GetCover(self, height = 0):
		global _oldTmpFiles
		
		if height in self._cover:
			return self._cover[height]
		
		coverIndex = 0 
		if self.raw.FrontCoverPageIndex > 0:
			coverIndex = self.raw.FrontCoverPageIndex
		image = _ComicRack.App.GetComicPage(self.raw, coverIndex)
		
		if image is None:
			self._cover = ''
			return ''

		tmpFile = System.IO.Path.GetTempFileName()
		_oldTmpFiles.append(tmpFile)

		# We need a jpg
		coverFile = tmpFile + '.jpg'
		_oldTmpFiles.append(coverFile)
		#print coverFile
		
		try:
			if height > 0:
				image = ResizeImage(image, height)
			image.Save(coverFile, System.Drawing.Imaging.ImageFormat.Jpeg)
			self._cover[height] = coverFile
			return coverFile
		except Exception,e:
			print '[SeriesInfoPanel] Exception when saving image: ', e
			return ''

