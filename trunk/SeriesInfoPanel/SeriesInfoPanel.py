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

SCRIPT_DIRECTORY =  __file__[:-len('SeriesInfoPanel.py')] 


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





def GenerateHTMLForSeries(books):
	global config, skins

	db = DB()
	
	info = []
	
	finishTime = time.clock() + 0.2
	for book in books:
		book = BookWrapper(book)
		series = db.GetSeries(book)
		volume = series.GetVolume(book)
		volume.Issues.append(book)
		
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
		s.ShowVolumeNames = (series.Volumes.keys() != [''])
		s.Volumes = []
		s.NumIssues = 0
		s.Formats = set()
		
		for volumeKey in sorted(series.Volumes.iterkeys()):
			volume = series.Volumes[volumeKey]
			
			volume.sort()
			
			v = Placeholder()
			s.Volumes.append(v)
			
			v.config = Placeholder()
			
			v.Name = volume.Name
			v.Cover = volume.Issues[0].Cover
			v.NumIssues = len(volume.Issues)
			v.Issues = CreateFullNumber(volume.IssuesRange, volume.IssuesCount)
			v.IssuesCount = volume.IssuesCount
			v.MissingIssues = volume.MissingIssues
			v.DuplicatedIssues = volume.DuplicatedIssues
			v.ReadPercentage = volume.ReadPercentage
			v.FilesFormat = volume.FilesFormat
			v.Rating = volume.Rating
			v.CommunityRating = volume.CommunityRating
			v.PublishersImprints = volume.PublishersImprints
			v.Publishers = volume.Publishers
			v.Imprints = volume.Imprints
			v.Format = volume.Format
			v.NextIssuesToRead = volume.NextIssuesToRead
			
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
			
			s.Formats.add(v.Format)
			s.NumIssues += v.NumIssues
		
		s.Formats = sorted(s.Formats)
		
		# Avoid look forever
		if time.clock() > finishTime:
			info.append(Translate('Warn.StoppedProcessing', 'Stopped processing because it took too much time'))
			break
	
	seriesTemplate = GetTemplate('series.html')
	
	vars = defaultVars.copy()
	vars['allSeries'] = allSeries
	vars['info'] = info
	
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
		
		skin.seriesFields = FixSeriesFields(skin.seriesFields)
		skin.issueFields = FixIssueFields(skin.issueFields)
		
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
	
	config.seriesFields = FixSeriesFields(config.seriesFields)
	config.issueFields = FixIssueFields(config.issueFields)


def WriteConfig():
	global config, skins
	
	WriteFile(SCRIPT_DIRECTORY + CONFIG_FILE, config)


# Init only once

LoadSkins()

