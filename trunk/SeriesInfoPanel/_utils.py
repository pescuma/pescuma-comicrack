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
import System
import re

clr.AddReference('System')

from System.IO import File, StreamReader, StreamWriter


SCRIPT_DIRECTORY =  __file__[:-len('_utils.py')] 


def ToString(v):
	if v is None:
		return ''
	if not isinstance(v, basestring):
		return str(v)
	return v

def ToInt(v):
	v = ToString(v)
	try:
		return int(round(ToFloat(v)))
	except:
		return 0

def ToFloat(x):
	try:
		return float(x)
	except:
		try:
			return float(re.sub('[^0-9.]', '', x))
		except:
			try:
				return float(re.sub('[^0-9]', '', x))
			except:
				return 0.0

def ResizeImage(image, width, height):
	if width <= 0 and height <= 0:
		return image
	elif width <= 0:
		width = image.Width * height / image.Height
	elif height <= 0:
		height = image.Height * width / image.Width
	
	result = System.Drawing.Bitmap(width, height)
	
	graphics = System.Drawing.Graphics.FromImage(result)
	graphics.CompositingQuality = System.Drawing.Drawing2D.CompositingQuality.HighQuality
	graphics.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.HighQualityBicubic
	graphics.SmoothingMode = System.Drawing.Drawing2D.SmoothingMode.HighQuality
	graphics.DrawImage(image, 0, 0, result.Width, result.Height)
	
	return result

def ReadFile(path, data):
	if not File.Exists(path):
		return data
	
	file = StreamReader(path)
	
	try:
		line = file.ReadLine()
		while line:
			line = line.strip()
			pos = line.find('=')
			if pos < 0:
				continue
			name = line[:pos].strip()
			val = line[pos+1:].strip()
			
			if hasattr(data, name):
				oldVal = getattr(data, name)
				if isinstance(oldVal, list):
					tmp = []
					for v in val.split('|'):
						tmp.append(v.strip())
					val = tmp
					
				elif isinstance(oldVal, bool):
					val = (val != 'False' and val != '0')
					
				elif isinstance(oldVal, int):
					val = ToInt(val)
					
				elif isinstance(oldVal, float):
					val = ToFloat(val)
			
			setattr(data, name, val)
			
			line = file.ReadLine()
		
	finally:
		file.Dispose()
	
	return data
	
def WriteFile(path, data):
	file = StreamWriter(path)
	
	try:
		for name in dir(data):
			if name[0] == '_':
				continue
			if not hasattr(data, name):
				continue
			val = getattr(data, name)
			if val is None or callable(val):
				continue
			
			if isinstance(val, list):
				val = '|'.join(val)
			
			file.WriteLine(name + " = " + ToString(val))
		
	finally:
		file.Dispose()


_translations = { 
	'NumIssues': 'Num of books', 
	'ReadPercentage': 'Read' ,
	'FullPublishers': 'Publishers/Imprints',
	'NextIssueToRead': 'Next to Read'
	}

def TranslateFieldName(name):
	if name in _translations:
		return _translations[name]
	
	ret = ''
	for i in range(len(name)):
		c = name[i]
		if i > 0 and c >= 'A' and c <= 'Z':
			ret += ' '
		ret += c
	return ret


def CreateFullName(series, volume, number, count):
	ret = CreateFullSeries(series, volume)
	
	_number = CreateFullNumber(number, count)
	if _number:
		ret += ' #' + _number
	
	return ret

def CreateFullNumber(number, count):
	if not number:
		return ''
	
	ret = number
	if count:
		ret += ' of ' + count
	
	return ret

def CreateFullSeries(series, volume):
	if series:
		ret = series
	else:
		ret = '<Unknown Series>'
	
	if volume:
		if ToInt(volume) < 1900:
			ret += ' v'+ volume
		else:
			ret += ' (' + volume + ')'
	
	return ret

def CreateFullAlternateName(series, number, count):
	_number = CreateFullNumber(number, count)
	
	if not series and not _number:
		return ''
	
	ret = series
	if _number:
		ret += ' #' + _number
	
	return ret
	
def CreateFullPublisher(publisher, imprint):
	if not publisher and not imprint:
		return ''
	
	if publisher:
		ret = publisher
	else:
		ret = '<Unknown Publisher>'
	
	if imprint:
		ret += ' - ' + imprint
	
	return ret

def CreateDate(month, year):
	if not month and not year:
		return ''
	
	if month:
		ret = month + '/'
	else:
		ret = ''
	
	if year:
		ret += year
	else:
		ret += '????'
	
	return ret

def StartedReadingIssue(book):
	return book.OpenedCount > 0 and (book.ReadPercentage > 50 or book.LastPageRead >= book.FrontCoverPageIndex + 3)


class Placeholder:
	pass
