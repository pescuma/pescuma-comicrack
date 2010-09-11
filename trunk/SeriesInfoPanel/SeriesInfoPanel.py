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
import sys
import System
import tempita
import time
import re

clr.AddReference('System')

from System.IO import DirectoryInfo, File, FileInfo

from _utils import *
from _db import *
from BookWrapper import *
from SmartDict import *
from OptionsForm import *


class Skin:
	def __init__(self, id):
		self.id = id
		self.name = id
		self.canEditFields = False
		self.seriesFields = []
		self.seriesHideEmptyFields = True
		self.issueFields = []
		self.issuesHideEmptyFields = False
		self.issuesNumberOfFirstPages = 0
	
	def __str__(self):
		return self.name

class Config:
	def __init__(self):
		self.skin = 'default'
		self.seriesFields = []
		self.seriesHideEmptyFields = True
		self.issueFields = []
		self.issuesHideEmptyFields = False
		self.issuesNumberOfFirstPages = 0
	
	def copy(self):
		ret = Config()
		ret.skin = self.skin
		ret.seriesFields = self.seriesFields
		ret.seriesHideEmptyFields = self.seriesHideEmptyFields
		ret.issueFields = self.issueFields
		ret.issuesHideEmptyFields = self.issuesHideEmptyFields
		ret.issuesNumberOfFirstPages = self.issuesNumberOfFirstPages
		return ret

CONFIG_FILE = 'config.txt'

skins = {}
config = Config()
lastConfigReadDate = None


def _range(*args):
	_len = len(args)
	
	start = 0
	end = 0
		
	if _len < 1:
		return []
	elif _len == 1:
		end = ToInt(args[0])
	else:
		start = ToInt(args[0])
		end = ToInt(args[1])
	
	if start >= end:
		return []
	else:
		return range(start, end)

defaultVars = SmartDict()
defaultVars['info'] = ''
defaultVars['range'] = _range
defaultVars['toint'] = ToInt
defaultVars['tofloat'] = ToFloat
defaultVars['translate'] = Translate
defaultVars['path'] = SCRIPT_DIRECTORY



	
def GetTemplate(filename):
	global config, skins
	path = SCRIPT_DIRECTORY + config.skin + '_' + filename
	if not File.Exists(path):
		return tempita.HTMLTemplate('File not found: ' + path)
	return tempita.HTMLTemplate.from_filename(path)




def GenerateHTMLForNoComic():
	issueTemplate = GetTemplate('nothing.html')
	html = issueTemplate.substitute(defaultVars)
	
	#print html
	return html


_fieldsNotToIgnore = set([
	'ReadPercentage'
	])

def PackFields(fields, hideEmptyFields, getter):
	if not hideEmptyFields:
		return fields
		
	ret = []
	
	i = 0
	for field in fields:
		if field == '-':
			if i == 0:
				ret.append(field)
			elif len(ret) > 0 and ret[-1] != '-':
				ret.append(field)
		elif field in _fieldsNotToIgnore:
			ret.append(field)
		else:
			if getter(field):
				ret.append(field)
		i += 1
	
	if len(ret) > 0 and ret[-1] == '-' and fields[-1] != '-':
		del ret[-1]
	
	return ret


def GenerateHTMLForIssue(book):
	global config, skins

	book = BookWrapper(book)
	
	issueTemplate = GetTemplate('issue.html')
	
	cfg = Placeholder()
	
	vars = defaultVars.copy()
	vars['config'] = cfg
	vars['book'] = book
	vars.addAttributes(book)	
	
	cfg.fields = PackFields(config.issueFields, config.issuesHideEmptyFields, lambda f: vars[f])
	if book.FirstNonCoverPageIndex + config.issuesNumberOfFirstPages > book.PageCount:
		cfg.numOfFirstPages = book.PageCount - book.FirstNonCoverPageIndex
	else:
		cfg.numOfFirstPages = config.issuesNumberOfFirstPages
	
	html = issueTemplate.substitute(vars)
	
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
			ret = Translate("IssueRange",  "%(first)s to %(last)s")  % { 'first': firstNum, 'last': lastNum } 
		else:
			ret = firstNum
		
		if hasMillion:
			ret = Translate("AndMillion",  "%(issues)s and 1.000.000")  % { 'issues': ret }
		
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

def GetPublishersImprints(volume):
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
	
	for book in volume.issues:
		pi = PublisherImprint()
		pi.Publisher = book.Publisher
		pi.Imprint = book.Imprint
		if pi.Publisher or pi.Imprint:
			ret.add(pi)
	
	return sorted(ret)

def GetPublishers(volume):
	ret = set()
	
	for book in volume.issues:
		if book.Publisher:
			ret.add(book.Publisher)
	
	return sorted(ret)

def GetImprints(volume):
	ret = set()
	
	for book in volume.issues:
		if book.Imprint:
			ret.add(book.Imprint)
	
	return sorted(ret)

def GetFormats(volume):
	ret = set()
	
	for book in volume.issues:
		if book.Format:
			ret.add(book.Format)
		else:
			ret.add(Translate('Series'))
	
	return sorted(ret)

def GenerateHTMLForSeries(books):
	global config, skins

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
			info.append(Translate('Warn.StoppedLoading', 'Stopped loading because it took too much time'))
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
		s.Formats = set()
		
		for volumeKey in sorted(series.volumes.iterkeys()):
			volume = series.volumes[volumeKey]
			
			volume.sort()
			
			v = Placeholder()
			s.Volumes.append(v)
			
			v.config = Placeholder()
			
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
			v.PublishersImprints = GetPublishersImprints(volume)
			v.Publishers = GetPublishers(volume)
			v.Imprints = GetImprints(volume)
			v.Formats = GetFormats(volume)
			v.NextIssueToRead = volume.GetNextIssueToRead()
			
			v.FullName = CreateFullSeries(s.Name, v.Name)
			
			v.FullPublishers = []
			for pi in v.PublishersImprints:
				ret = ''
				if pi.Publisher:
					ret = pi.Publisher
				else:
					ret = Translate('UnknownPublisher', '<Unknown Publisher>')
				
				if pi.Imprint:
					ret += ' - ' + pi.Imprint
				v.FullPublishers.append(ret)

			v.config.fields = PackFields(config.seriesFields, config.seriesHideEmptyFields, lambda f: getattr(v, f))
			v.config.showName = s.ShowVolumeNames
			
			s.Formats.update(v.Formats)
			s.NumIssues += v.NumIssues
		
		s.Formats = sorted(s.Formats)
		
		# Avoid look forever
		if time.clock() > finishTime:
			info.append(Translate('Warn.StoppedProcessing', 'Stopped processing because it took too much time'))
			break
	
	seriesTemplate = GetTemplate('series.html')
	
	vars = defaultVars.copy()
	vars['allSeries'] = allSeries
	
	html = seriesTemplate.substitute(vars)
	
	#print html
	return html


#@Name Series Info Panel
#@Hook ComicInfoHtml
#@Enabled true
#@Description Show information about selected series
#@Image SIP.png
def SeriesInfoPanel(books):
	SetComicRack(ComicRack)
	SetScriptName('SeriesInfoPanel')
	InitBookWrapper(ComicRack)
	
	ReadConfig()
	
	numBooks = len(books)
	if numBooks < 1:
		return GenerateHTMLForNoComic()
	elif numBooks == 1:
		return GenerateHTMLForIssue(books[0])
	else:
		return GenerateHTMLForSeries(books)

#@Hook  ConfigScript
#@Key   SeriesInfoPanel
def ConfigureSeriesInfoPanel():
	ConfigSeriesInfoPanel([])

#@Name Series Info Panel Options...
#@Hook Library
#@Enabled true
#@Description Allow to configure Series Info Panel
#@Image SIP.png
def ConfigSeriesInfoPanel(books):
	global config, skins
	
	SetComicRack(ComicRack)
	SetScriptName('SeriesInfoPanel')
	
	ReadConfig()
	
	dlg = OptionsForm(skins, config)
	if dlg.ShowDialog() == DialogResult.OK:
		config = dlg._config
		WriteConfig()












def LoadSkins():
	global config, skins
	for file in DirectoryInfo(SCRIPT_DIRECTORY).GetFiles("*.skin"):
		skin = Skin(file.Name[:-5])
		
		ReadFile(file.FullName, skin)
		
		skins[skin.id] = skin

def ReadConfig():
	global config, skins, lastConfigReadDate
	
	path = SCRIPT_DIRECTORY + CONFIG_FILE
	lastModifiedDate = FileInfo(path).LastWriteTime
	
	if lastConfigReadDate and lastConfigReadDate == lastModifiedDate:
		return
	lastConfigReadDate = lastModifiedDate
	
	ReadFile(SCRIPT_DIRECTORY + CONFIG_FILE, config)
	
	resetSkin = (not config.skin or config.skin not in skins)
	if resetSkin:
		if 'default' in skins:
			config.skin = 'default'
		else:
			config.skin = skins.keys()[0]
	
	skin = skins[config.skin]
	
	if resetSkin or len(config.seriesFields) == 0:
		config.seriesFields = skin.seriesFields
	
	if resetSkin or len(config.issueFields) == 0:
		config.issueFields = skin.issueFields
	
	if resetSkin:
		config.seriesHideEmptyFields = skin.seriesHideEmptyFields
		config.issuesHideEmptyFields = skin.issuesHideEmptyFields
		config.issuesNumberOfFirstPages = skin.issuesNumberOfFirstPages


def WriteConfig():
	global config, skins
	
	WriteFile(SCRIPT_DIRECTORY + CONFIG_FILE, config)


# Init only once

LoadSkins()

