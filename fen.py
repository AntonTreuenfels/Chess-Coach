# Forsyth-Edwards Notation (FEN) Reading/Writing

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

# first created: 02/08/25
# last revision: 03/23/25

#--------------------
# Python modules
# (none)
# program modules
import chessmoves as CM
import chessconstants as CK
#--------------------

class FENvariables(object):

	def __init__(self):

		# "constants"

		self.NONE  = "-"

		# variables

		# parsed fen

		self.boardRanks = None		# the board position
		self.whoseMove  = None		# whose turn to move
		self.canCastle  = None		# castling moves allowed (if any)
		self.enPassant  = None		# en passant capture square (if any) 
		self.halfMove   = None		# half move clock
		self.fullMove   = None		# full move count

		self.fenError   = None	# fen has error ?

		# each move of game

		self.fenRecord   = list()	# record of all positions in order made

# make our one instance of this class

_FEN = FENvariables()

# ----------------------------

def gameStart():
	'''the normal game start position'''
	_FEN.fenRecord.clear()
	return 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

def placeStart():
	'''place pieces on empty board'''
	_FEN.fenRecord.clear()
	return '8/8/8/8/8/8/8/8 w KQkq - 0 1'

# ----------------------------

def _parseFenError(name, value):
	'''error in fen parse'''
	_FEN.error = f"*** FEN error: Bad {name} value: {value}"
	print( _FEN.error )
	# use normal game start as default
	# we know this is a good fen (right?), so we won't error check it
	fen = getStartFen().split()
	_FEN.boardRanks = fen[ 0 ].split( '/' )
	_FEN.whoseMove  = fen[ 1 ]
	_FEN.canCastle  = fen[ 2 ]
	_FEN.enPassant  = fen[ 3 ]
	_FEN.halfMove   = fen[ 4 ]
	_FEN.fullMove   = fen[ 5 ]
	# caller will use default fen
	# - because we may have more to do
	return fen

def parseFen(fen=None):
	'''parse a fen description'''
	# default to normal start position
	if fen is None:
		fen = getStartFen()
	_FEN.fenError = None

	fields = fen.split()
	# is there something obviously wrong with this fen ?
	if len(fields) != 6:
		fields = _parseFenError( "field count", fen )

	# the board position
	_FEN.boardRanks = fields[0].split('/')
	if len(_FEN.boardRanks) != 8:
		_FEN._parseFenError( "rank count", fields[0] )
	for rank in _FEN.boardRanks:
		for ch in rank:
			if not ch in 'rnbqkpRNBQKP12345678':
				field = _parseFenError( "rank", rank )
				break

	# whose move ?
	_FEN.whoseMove = fields[ 1 ]
	if not _FEN.whoseMove in 'wb' or len(_FEN.whoseMove) > 1:
		fields = _parseFenError( "move", fields[1] )

	# which castles are allowed ?
	_FEN.canCastle = fields[ 2 ]
	if _FEN.canCastle != '-':
		for i, ch in enumerate(_FEN.canCastle):
			if not ch in 'KQkq' or i > 3:
				fields = _parseFenError( "castle", fields[2] )
				break

	# en passant capture possible ?
	_FEN.enPassant = fields[ 3 ]
	if _FEN.enPassant != '-':
		if (
			len(_FEN.enPassant) != 2
		or not _FEN.enPassant[0] in 'abcdefgh'
		or not _FEN.enPassant[1] in '12345678'
		):
			fields = _parseFenError( "en passant", fields[3] )

	# half move counter past 100?
	_FEN.halfMove = fields[ 4 ]
	if not _FEN.halfMove.isdigit() or int(_FEN.halfMove) > 100:
		fields = _parseFenError( "half move", fields[4] )
	_FEN.halfMove = int( _FEN.halfMove )

	# full move counter
	_FEN.fullMove = fields[ 5 ]
	if not _FEN.fullMove.isdigit():
		fields = _parseFenError( "full move", fields[5] )
	_FEN.fullMove = int( _FEN.fullMove )

	# ----------------------------

def setWhoseMove(color):
	_FEN.whoseMove = "w" if color == CK.PC_WHITE else "b"

def getWhoseMove():
	return CK.PC_WHITE if _FEN.whoseMove == "w" else CK.PC_BLACK

def toggleWhoseMove():
	_FEN.whoseMove = "b" if _FEN.whoseMove == "w" else "w"
	return getWhoseMove()

def getOppMove():
	return CK.PC_BLACK if _FEN.whoseMove == "w" else CK.PC_WHITE

# ----------------------------

def setCastle(directions=None):
	_FEN.canCastle = _FEN.NONE if directions is None else directions

def getCastle():
	return _FEN.canCastle

def setnoCastle(directions):
	'''remove direction from possible castling'''
	cancastle = _FEN.canCastle
	for direction in directions:
		cancastle = cancastle.replace( direction, "" )
	setCastle( cancastle if cancastle != "" else None )

# ----------------------------

def setenPassant(square=None):
	_FEN.enPassant = _FEN.NONE if square is None else square

def getenPassant():
	return _FEN.enPassant

# ----------------------------

def sethalfMove(zerocount=True):
	'''zero if pawn move or any capture'''
	if zerocount:
		_FEN.halfMove = 0
	else:
		_FEN.halfMove += 1

def gethalfMove():
	return _FEN.halfMove

# ----------------------------

def setfullMove(color=None):
	'''update after every black move'''
	if color is None:
		_FEN.fullMove = 1
	elif color == CK.PC_BLACK:
		_FEN.fullMove += 1

# ----------------------------

def putBoardPosition():
	'''set empty board to fen position'''
	board = CM.getEmptyBoard()
	for i, row in enumerate(_FEN.boardRanks):
		file = 1
		rank = 8 - i
		for ch in row:
			if ch.isdigit():
				file += int( ch )
			else:
				board[ rank ][ file ] = ch
				file += 1
	return board

def putFen(fen=None):
	'''set empty board to a given fen'''
	parseFen( fen )
	return putBoardPosition()

# ----------------------------

def getBoardPosition(board):
	'''get board position in fen notation'''
	fen = []
	for rank in range(8, 0, -1):
		fenrow = ""
		empty = 0
		for piece in board[rank][1:]:
			if piece == ".":
				empty += 1
			elif empty < 1:
				fenrow = f"{fenrow}{piece}"
			else:
				fenrow = f"{fenrow}{empty}{piece}"
				empty = 0
		if empty > 0:
			fenrow = f"{fenrow}{empty}"
		fen.append( fenrow )

	return "/".join( fen )

def getFen(board):
	'''get fen signature of board position'''
	position = getBoardPosition( board )
	return f"{position} {_FEN.whoseMove} {_FEN.canCastle} {_FEN.enPassant} {str(_FEN.halfMove)} {str(_FEN.fullMove)}"

# ----------------------------

def clearRecord():
	'''delete move record'''
	_FEN.fenRecord.clear()

def recordFen(board):
	'''record fen signature of board position'''
	fen = getFen( board )
	_FEN.fenRecord.append( fen )

def lastRepeated():
	'''count how many time the most recent move was repeated'''
	# get and break apart most recent move
	sfen = _FEN.fenRecord[ -1 ].split()
	# get rid of irrelevant clock info
	repfen = " ".join( sfen[:4] )
	# look for repetitioins
	reps = 0
	for fen in _FEN.fenRecord:
		if fen.find(repfen) == 0:
			reps += 1

	return reps

def cantakeBack():
	'''record long enough to take back move ?'''
	return bool( len(_FEN.fenRecord) > 1 )

def takeBack():
	'''take back a move'''
	# discard most recent move
	_FEN.fenRecord.pop()
	# return the move before that one
	return _FEN.fenRecord.pop()

def mostRecent():
	'''most recent move'''
	return _FEN.fenRecord.pop()

# ----------------------------
