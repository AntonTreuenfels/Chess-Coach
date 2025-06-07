# Chess Move DB Storage

# (c) 2025 by Anton Treuenfels

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# ---------------------------------

# by Anton Treuenfels

# 5248 Horizon Dr
# Fridley, MN 55421

# e-mail: teamtempest@yahoo.com

# source language: Python 3.11.4

# first created: 04/23/25
# last revision: 05/28/25

#--------------------
# Python modules
import sqlite3 as SQL
# program modules
import chessconstants as CK
#--------------------

# database name

DB_NAME = "fenmoves.db"

# move tables and schemas

# fendesc: header of one fen sequence

# descID:		unique; assigned by SQLite
# desctype:		snapshot, game, puzzletype
# fencount:		total number of fens in sequence
# startfen:		first fen in sequence

# fenmoves: fen sequence associated with a particular fenID

# fenID:		unique; assigned by SQLite
# descID:		foreign key from fendesc
# fennumber:	which fen in sequence
# fen	:		fen
# FOREIGN KEY:	descID
# REFERENCES:	fendesc(descID)

DB_FEN_CREATE = [
	"""CREATE TABLE IF NOT EXISTS fendesc (
			descID INTEGER PRIMARY KEY,
			fentype TEXT NOT NULL,
			fencount INTEGER,
			startfen TEXT,
			desctag TEXT
		);""",

	"""CREATE TABLE IF NOT EXISTS fenmoves (
			fenID INTEGER PRIMARY KEY,
			descID INTEGER NOT NULL,
			fennumber INTEGER NOT NULL,
			fen TEXT NOT NULL,
			FOREIGN KEY (descID)
			REFERENCES fendesc(descID)
				ON DELETE CASCADE
				ON UPDATE CASCADE
		);""",
	]

# insert data into move tables

DB_FEN_INSERT = [
	"""INSERT INTO fendesc (fentype, fencount, startfen, desctag)
		VALUES(?,?,?,?)
	""",

	"""INSERT INTO fenmoves (descID, fennumber, fen)
		VALUES(?,?,?)
	""",
	]

# delete data from move tables
# - the only data we want to delete at present is a single snapshot

DB_FEN_DELETE = \
	"""DELETE FROM fendesc
		WHERE fentype = A10
	"""

# list recorded fen sequences

DB_FEN_BROWSE = \
	"""SELECT *
		FROM fendesc
		ORDER BY fentype ASC, fencount ASC
		"""

DB_FEN_LOAD = \
	"""SELECT fen
	FROM fenmoves
	WHERE descid = ?
	ORDER BY fennumber ASC
	"""

# move descriptor types
# -name : cell in chooser, descriptor type

# "A10": snapshot (only one in database at any time)
# "Bxx": puzzle ('xx' records puzzle type; no particular system)
# "Cxx": game (may eventually use 'xx' to record opening type)

DB_DESC_TYPES = {
	"Mate":			(0, 0, "B10"),
	"Fork":			(0, 1, "B20"),
	"Pin":			(0, 2, "B30"),
	"Skewer":		(0, 3, "B40"),
	"Capture":		(1, 0, "B50"),
	"Game":			(1, 1, "C10"),
	"Snapshot":		(1, 2, "A10"),
	"Cancel": 		(1, 3, "X00"),
	}

DB_DESC_TAGS = {
	"A10": "Snapshot",
	"B10": "Mate",
	"B20": "Fork",
	"B30": "Pin",
	"B40": "Skewer", 
	"B50": "Capture",
	"C10": "Game",
	}

#--------------------

def dbError(tag, error):
	'''report DB error'''
	print( f"Failed to {tag}: {error}" )
	return False

def validArgs(doing, dtype, count, limit):
	'''simple record validataion'''
	result = True
	 # is descriptor type OK ?
	if dtype is None or dtype not in DB_DESC_TAGS:
		result = dbError( doing, f"unrecognized descriptor type: {dtype}" )

	# is move count OK ?
	if count is not None and (count < 1 or count > limit):
			result =  dbError( doing, f"move count out of range: {count} > {limit}" )

	return ( result, dtype, count )

#--------------------

def dbCreate():
	'''create fen move database'''
	action = "create database"
	# let's assume this will work
	result = True
	try:
		with SQL.connect(DB_NAME) as conn:
			cursor = conn.cursor()
			for statement in DB_FEN_CREATE:
				cursor.execute( statement )
			conn.commit()

	# problem ?
	except (SQL.Error, Exception) as error:
		result = dbError( action, error )

	finally:
		if conn:
			conn.close()
		return result

def dbRecord(rtype, fens, desctag=None):
	'''insert fen moves  into database'''
	action = "insert moves"
	limit = 1 if rtype.startswith("A") else 20 if rtype.startswith("B") else 100
	goodargs, ptype, fencount = validArgs( action, rtype, len(fens), limit )
	if not goodargs:
		return False

	if desctag is None:
		desctag = DB_DESC_TAGS[ rtype ]

	result = True
	try:
		with SQL.connect(DB_NAME) as conn:
			cursor = conn.cursor()
			# a snapshot with only one fen ?
			if rtype == "A10":
				# delete any existing snapshot
				cursor.execute( DB_FEN_DELETE )
				# insert the header record (all by itself for snapshot)
				# fentype, fencount, firstfen, desctag
				params = ( rtype, fencount, fens[0], desctag )
				cursor.execute( DB_FEN_INSERT[0], params )
			# s puzzle or game record
			else:
				# insert the header record
				# fentype, fencount, firstfen, desctag
				params = ( rtype, fencount, fens[0], desctag )
				cursor.execute( DB_FEN_INSERT[0], params )
				# insert all the moves (more convenient to have them all here)
				# descid, fennumber, fen
				descid = cursor.lastrowid
				for i, fen in enumerate(fens):
					params = ( descid, i, fen )
					cursor.execute( DB_FEN_INSERT[1], params )
			# save changes
			conn.commit()

	# problem ?
	except (SQL.Error, Exception) as error:
		result = dbError( action, error )

	finally:
		if conn:
			conn.close()

	return result

def getAllRecords():
	'''get list of all header records'''
	action = "get all recrors"

	result = True
	try:
		with SQL.connect(DB_NAME) as conn:
			cursor = conn.cursor()
			cursor.execute( DB_FEN_BROWSE )
			allrows = cursor.fetchall()

	# problem ?
	except (SQL.Error, Exception) as error:
		result = dbError( action, error )
		allrows = []

	finally:
		if conn:
			conn.close()

	# make lists for choosing and chosen
	chosenlist = list()
	chooselist = list()
	# did we get anything ?
	if result and len(allrows) > 0:
		# fenID, fentype, fencount, firstfen, desctag
		firstheader = allrows[ 0 ]
		# is there a snapshot ?
		if firstheader[1] == "A10":
			chosenlist.append( firstheader[0], firstheader[3] )
			chooselist.append( firstheader[4] )
			del allrows[ 0 ]
		# everything left is a puzzle or game
		# - the main point here is to keep the puzzle numbers consistent
		for i, header in enumerate(allrows):
			chosenlist.append( (header[0], header[3]) )
			if header[1].startswith("B"):
				chooselist.append( f"# {i+1}: {header[4]} in {header[2]//2}" )
			else:
				chooselist.append( f"{header[4]}" )

	# chooselist = strings that appear in listbox
	# chosenlist = ( fenID, firstfen )

	return ( result, chooselist, chosenlist )

def loadRecord(thisid):
	'''load one saved record'''
	action = "load one record"

	result = True
	try:
		with SQL.connect(DB_NAME) as conn:
			cursor = conn.cursor()
			params = ( thisid, )
			cursor.execute( DB_FEN_LOAD, params )
			allrows = cursor.fetchall()

	# problem ?
	except (SQL.Error, Exception) as error:
		result = dbError( action, error )
		allrows = []

	finally:
		if conn:
			conn.close()

	# convert fen tuples to fen list
	fens = list()
	for row in allrows:
		fens.append( row[0] )
	return fens