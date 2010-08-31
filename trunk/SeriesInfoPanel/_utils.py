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


SCRIPT_DIRECTORY =  __file__[:-len('_utils.py')] 


def ToString(v):
	if v is None:
		return ''
	if not isinstance(v, basestring):
		return str(v)
	return v

def ToInt(v):
	v = ToString(v)
	if v.isdigit():
		return int(v)
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

class Placeholder:
	pass
