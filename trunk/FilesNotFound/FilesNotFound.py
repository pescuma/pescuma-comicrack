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

import time
import clr
import System

clr.AddReference('System')

from System.IO import File

#@Name	 Files not found
#@Hook	 CreateBookList
#@PCount 0
#@Enabled true
#@Description List books that the file is not found on the disc (ignore fileless)
def FilesNotFound(books, a, b):
	ret = []
	
	#print '[FilesNotFound] Searching books'
	#dt = time.clock()
	
	# Load books
	for book in books:
		# Ignore fileless
		if not book.FilePath:
			continue
		
		if not File.Exists(book.FilePath):
			ret.append(book)

	
	#dt = time.clock() - dt
	#print '[FilesNotFound] Done in ', dt, 's'
	
	return ret

#@Name	 Files found in disc
#@Hook	 CreateBookList
#@PCount 0
#@Enabled true
#@Description List books that the file is found on the disc (ignore fileless)
def FilesFound(books, a, b):
	ret = []
	
	#print '[FilesFound] Searching books'
	#dt = time.clock()
	
	# Load books
	for book in books:
		# Ignore fileless
		if not book.FilePath:
			continue
		
		if File.Exists(book.FilePath):
			ret.append(book)

	
	#dt = time.clock() - dt
	#print '[FilesFound] Done in ', dt, 's'
	
	return ret
