# Chess Move Generator

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

# first created: 02/02/25
# last revision: 03/28/25

#--------------------
# Python modules
# (none)
# program modules
import fen as FEN
import chessconstants as CK
#--------------------

class CMvariables(object):

	def __init__(self):

		# "constants"

		self.EMPTY = "."
		self.OFFBOARD = "*"

		self.PC_SLIDER		= "QqRrBb"
		self.PC_RANK_SLIDER	= "QqRr"	# okay, yeah, if it can do this it can also slide on files
		self.PC_DIAG_SLIDER	= "QqBb"

		# moving from square to square

		self.MOVEDELTAS = {
			 "n": ( 0,  1),	# straight up
			"ne": ( 1,  1),	# up and right
			 "e": ( 1,  0),	# straight right
			"se": ( 1, -1),	# down and right
			 "s": ( 0, -1),	# straight down
			"sw": (-1, -1),	# down and left
			 "w": (-1,  0),	# straight left
			"nw": (-1,  1),	# up and left
			"k1": ( 1,  2),	# up two, right one
			"k2": ( 2,  1),	# up one, right two
			"k3": ( 2, -1),	# down one, right two
			"k4": ( 1, -2),	# down two, right one
			"k5": (-1, -2),	# down two, left one
			"k6": (-2, -1),	# down one, left two
			"k7": (-2,  1),	# up one, left two
			"k8": (-1,  2),	# up two, left one
			"P2": ( 0,  2),	# up two
			"p2": ( 0, -2),	# down two
			"ck": ( 2,  0), # right two
			"cq": (-2,  0), # left two
			}

		# what moves are available to pieces

		self.POSSIBLEMOVES = {
			 "K": ( False, ["n", "ne", "e", "se", "s", "sw", "w", "nw", "ck", "cq"] ),
			 "Q": ( True,  ["n", "ne", "e", "se", "s", "sw", "w", "nw"] ),
			 "R": ( True,  ["n", "e", "s", "w"] ),
			 "B": ( True,  ["ne", "se", "sw", "nw"] ),
			 "N": ( False, ["k1", "k2", "k3", "k4", "k5", "k6", "k7", "k8"] ),
			 "P": ( False, ["n", "P2", "ne", "nw"] ),
			 "p": ( False, ["s", "p2", "se", "sw"] ),
			}

		# castling availability and squares to check

		self.CASTLE = {
			"Kck": ("K", ("R", 8,1), [(6,1), (7,1)] ),
			"Kcq": ("Q", ("R", 1,1), [(4,1), (3,1), (2,1)] ),
			"kck": ("k", ("r", 8,8), [(6,8), (7,8)] ),
			"kcq": ("q", ("r", 1,8), [(4,8), (3,8), (2,8)] ),
			}

		# piece point values

		self.POINTVALUE = {
			"K": 100,
			"Q": 9,
			"R": 5,
			"B": 3,
			"N": 3,
			"P": 1,
			"k": -100,
			"q": -9,
			"r": -5,
			"b": -3,
			"n": -3,
			"p": -1,
			".": 0,
			}

		self.ABSVALUE = {
			"K": 100,
			"Q": 9,
			"R": 5,
			"B": 3,
			"N": 3,
			"P": 1,
			"k": 100,
			"q": 9,
			"r": 5,
			"b": 3,
			"n": 3,
			"p": 1,
			".": 0,
			}

# make our one instance of this class

_CM = CMvariables()

# ----------------------------

def fr2sq(file, rank):
	'''file and rank to square name'''
	return f"{'*abcdefgh'[file]}{rank}"

def sq2fr(square):
	'''square name to file and rank'''
	return "*abcdefgh".find(square[0]), "*12345678".find(square[1])

# ----------------------------

def getNoMoves():
	'''no possible moves from any square'''
	movefrom = dict()
	for file in range(1,9):
		for rank in range(1,9):
			sqname = fr2sq( file, rank )
			movefrom[ sqname ] = list()
	return movefrom

def getZeroCounts():
	'''no piececes can reach any square'''
	# a 2D array, first index rank, second index file
	# - indices will run 0..8, but we will ignore index 0
	return [ [0 for rank in range(9)] for file in range(9) ]

def getEmptyBoard():
	'''create a new empty board'''
	# a 2D array, first index rank, second index file
	# - though it could just as easily be the other way, FEN puts rank first
	# - indices will run 0..8, but we will ignore index 0
	return [ ['.' for rank in range(9)] for file in range(9) ]

# ----------------------------

def colorOf(piece):
	'''what color is this piece ?'''
	if piece in "KQRBNP":
		return CK.PC_WHITE
	elif piece in "kqrbnp":
		return CK.PC_BLACK
	else:
		return CK.SQ_EMPTY

def isWhite(piececolor):
	return piececolor == CK.PC_WHITE

def occupiedBy(board, file, rank):
	'''which piece (if any) occupies this square ?'''
	# is this position even on the board ?
	if 1 <= file <= 8 and 1 <= rank <= 8:
		return board[ rank ][ file ]
	else:
		return _CM.OFFBOARD

def makeMove(board, dstfile, dstrank, srcfile, srcrank):
	'''make a move on chessboard'''

	def _occupy(board, squares):
		'''populate squares'''
		for file, rank, marker in squares:
			board[ rank ][ file] = marker
		# this seems a little cleaner( and saves a little space )
		return True

	# what pieces are on these squares now ?
	dstpiece = occupiedBy( board, dstfile, dstrank )
	srcpiece = occupiedBy( board, srcfile, srcrank )
 
	enpassant = None
	moved = False

	# did king, rook or pawn move ?
	match srcpiece:
		# white king moved ?
		case "K":
			FEN.setnoCastle( "KQ" )
			# did white king castle kingside ?
			if dstfile - srcfile == 2:
				moved = _occupy( board, [(5, 1, CK.SQ_EMPTY), (6, 1, "R"), (7, 1, "K"), (8, 1, CK.SQ_EMPTY)] )
			# did white king castle queenside ?
			elif srcfile - dstfile == 2:
				moved = _occupy( board, [(5, 1, CK.SQ_EMPTY), (4, 1, "R"), (3, 1, "K"), (1, 1, CK.SQ_EMPTY)] )
		# black king moved ?
		case "k":
			FEN.setnoCastle( "kq" )
			# did black king castle kingside ?
			if dstfile - srcfile == 2:
				moved = _occupy( board, [(5, 8, CK.SQ_EMPTY), (6, 8, "r"), (7, 8, "k"), (8, 8, CK.SQ_EMPTY)] )
			# did black king castle queenside ?
			elif srcfile - dstfile == 2:
				moved = _occupy( board, [(5, 8, CK.SQ_EMPTY), (4, 8, "r"), (3, 8, "k"), (1, 8, CK.SQ_EMPTY)] )
		# a white rook moved ?
		case "R":
			FEN.setnoCastle( "Q" if srcfile == 1 else "K" if srcfile == 8 else _CM.OFFBOARD )
		# a black rook moved ?
		case "r":
			FEN.setnoCastle( "q" if srcfile == 1 else "k" if srcfile == 8 else _CM.OFFBOARD )
		# white pawn moved ?
		case "P":
			if dstrank == 8:
				dstpiece = "P?"
			elif dstrank - srcrank == 2:
				enpassant = fr2sq( srcfile, srcrank+1 )
			elif srcrank == 5 and fr2sq(dstfile, dstrank) == FEN.getenPassant():
				moved = _occupy( board, [(srcfile, srcrank, CK.SQ_EMPTY), (dstfile, dstrank, "P"), (dstfile, dstrank-1, CK.SQ_EMPTY)] )
				dstpiece = "px"
		# black pawn moved ? 
		case "p":
			if dstrank == 1:
				dstpiece = "p?"
			elif srcrank - dstrank == 2:
				enpassant = fr2sq( srcfile, srcrank-1 )
			elif srcrank == 4 and fr2sq(dstfile, dstrank) == FEN.getenPassant():
				moved = _occupy( board, [(srcfile, srcrank, CK.SQ_EMPTY), (dstfile, dstrank, "p"), (dstfile, dstrank+1, CK.SQ_EMPTY)] )
				dstpiece = "Px"
		case _:
			pass

	# if not moved yet, do so now
	if not moved:
		_occupy( board, [(dstfile, dstrank, srcpiece), (srcfile, srcrank, CK.SQ_EMPTY)] )

	# new enpassant square (if any)
	FEN.setenPassant( enpassant )

	# return new board and captured piece (if any)
	return ( board, dstpiece )

# ----------------------------

def pawnMove(board, piece, file, rank, moves):
	'''determine possible pawn moves'''
	canmove = list()
	for move in moves:
		dltfile, dltrank = _CM.MOVEDELTAS[ move ]
		match move:
			# can pawn move one square forward ?
			case "n" | "s":
				if occupiedBy(board, file, rank+dltrank) == CK.SQ_EMPTY:
					canmove.append( move )
			# can white pawn move two squares forward ?
			case "P2":
				if ( rank == 2
					and occupiedBy(board, file, 3) == CK.SQ_EMPTY
					and occupiedBy(board, file, 4) == CK.SQ_EMPTY
				):
					canmove.append ( move )
				
			# can black pawn move two squares forward ?
			case "p2":
				if ( rank == 7
					and occupiedBy(board, file, 6) == CK.SQ_EMPTY
					and occupiedBy(board, file, 5) == CK.SQ_EMPTY
				):
					canmove.append ( move )
			# can white pawn capture diagonally ?
			case "nw" | "ne":
				if occupiedBy(board, file+dltfile, rank+dltrank) != CK.SQ_EMPTY:
					canmove.append( move )
				# enpassant capture possible ?
				elif rank == 5 and FEN.getenPassant() == fr2sq(file+dltfile, rank+dltrank):
					canmove.append( move )
			# can black pawn capture diagonally ?
			case "sw" | "se":
				if occupiedBy(board, file+dltfile, rank+dltrank) != CK.SQ_EMPTY:
					canmove.append( move )
				# enpassant capture possible ?
				elif rank == 4 and FEN.getenPassant() == fr2sq(file+dltfile, rank+dltrank):
					canmove.append( move )
			case _:
				pass

	return canmove

# ----------------------------

def canCastle(board, piece, move):
	'''check if castling is available'''
	ndx = f"{piece}{move}"
	direction, rookon, squares = _CM.CASTLE[ ndx ]
	# castling this way available ?
	if not direction in FEN.getCastle():
		return False

	# rook and king on starting squares?
	# - rook in particular might not be
	rook, file, rank = rookon
	if occupiedBy(board, file, rank) != rook:
		return False
	if occupiedBy(board, 5, rank) != piece:
		return False

	# check castling squares
	# - all must be empty
	for square in squares:
		file, rank = square
		if occupiedBy(board, file, rank) != CK.SQ_EMPTY:
			return False

	# this castle move is ok at first glance
	return True

def kingMove(board, piece, file, rank, moves):
	'''determine possible king moves'''
	canmove = list()
	for move in moves:
		dltfile, dltrank = _CM.MOVEDELTAS[ move ]
		match move:
			# can king castle ?
			case "ck" | "cq":
				if canCastle(board, piece, move ):
					canmove.append( move )
			# can king move to an adjacent square ?
			case _:
				if occupiedBy(board, file+dltfile, rank+dltrank) != _CM.OFFBOARD:
					canmove.append( move )

	return canmove

# ----------------------------

def canReach(board, allsquares):
	'''count how many pieces can reach each square'''

	def countup(moves, color):
		for direction, file, rank in moves:
			color[ file ][ rank ] += 1

	whitecnt = getZeroCounts()
	blackcnt = getZeroCounts()

	for square, moves in allsquares.items():
		if len(moves) < 1:
			continue
		sqfile, sqrank = sq2fr( square )
		occupant = occupiedBy( board, sqfile, sqrank )
		if colorOf(occupant) == CK.PC_WHITE:
			countup( moves, whitecnt )
		else:
			countup( moves, blackcnt )

	return( whitecnt, blackcnt )

def oneMove(board, piece, file, rank):
	'''create list of squares this piece can reach on next move'''
	match piece:
		# a pawn ?
		case "P" | "p":
			slide, moves = _CM.POSSIBLEMOVES[ piece ]
			moves = pawnMove( board, piece, file, rank, moves )
		# a king ?
		case "K" | "k":
			slide, moves = _CM.POSSIBLEMOVES[ piece.upper() ]
			moves = kingMove( board, piece, file, rank, moves )
		# any other piece ?
		case _:
			slide, moves = _CM.POSSIBLEMOVES[ piece.upper() ]

	canmove = list()
	# go through each possible move
	for move in moves:
		# first square we can reach in this direction
		dltfile, dltrank = _CM.MOVEDELTAS[ move ]
		nxtfile = file + dltfile
		nxtrank = rank + dltrank

		# while we're still on the board...
		while 1 <= nxtfile <= 8 and 1 <= nxtrank <= 8:
			# we can reach this square
			canmove.append( (move, nxtfile, nxtrank) )
			# can we move to next square along this line ?
			if slide and occupiedBy(board, nxtfile, nxtrank) == CK.SQ_EMPTY:
				nxtfile += dltfile
				nxtrank += dltrank
			else:
				break

	# squares this piece can reach on next move
	return canmove

def allMoves(board):
	'''update all possible moves on this board'''
	# initialize record
	piecemov = getNoMoves()
#	whitecnt = getZeroCounts()
#	blackcnt = getZeroCounts()

	# we'll just generate all possible moves and trim them later
	for file in range(1,9):
		for rank in range(1, 9):
			occupant = occupiedBy( board, file, rank )
			if occupant == CK.SQ_EMPTY:
				continue
			# update possible moves
			canmove = oneMove( board, occupant, file, rank )
			square = fr2sq( file, rank )
			piecemov[ square ].extend( canmove )
			# update reach counts
			'''
			pcolor = colorOf( occupant )
			for pmove, pfile, prank in canmove:
				if pcolor == CK.PC_WHITE:
					whitecnt[ pfile ][ prank ] += 1
				else:
					blackcnt[ pfile ][ prank ] += 1
			'''
	whitecnt, blackcnt = canReach( board, piecemov )

	# at this point
	# - piecemov is a dictionary indexed by aquare that holds all possible moves from each square
	# - whitecnt is a 2D array indexed by file and rank that shows how many white pieces can reach each square
	# - blackcnt is a 2D array indexed by file and rank that shows how many black pieces can reach each square

	return ( piecemov, whitecnt, blackcnt )

# ----------------------------

def getVerboten(piece, white, black):
	'''get list of where king cannot go'''
	return white if piece == "k" else black

def kingChecked(file, rank, verboten):
	return bool(verboten[file][rank] )

def findKing(board, piece):
	'''find location of king piece'''
	for file in range(1, 9):
		for rank in range(1, 9):
			if piece == occupiedBy(board, file, rank):
				return ( file, rank )
	# well, this should never happen !
	return ( 0 , 0 )

# ----------------------------

def potentialMoves(board):
	'''update potential moves on this board'''
	# this is not particularly efficient
	# - but it should be thorough
	allsquares, whites, blacks = allMoves( board )

	# eliminate all moves that leave a friendly king in check
	fen = FEN.getFen( board )
	for square, moves in allsquares.items():
		# empty squares have no moves
		if len(moves) < 1:
			continue
		srcfile, srcrank = sq2fr( square )
		occupant = occupiedBy( board, srcfile, srcrank )
		occ_color = colorOf( occupant )
		enemyking, friendlyking =  ("k", "K") if isWhite(occ_color) else ("K", "k")
		canmove = list()
		for move in moves:
			dstmove, dstfile, dstrank = move
			dstpiece = occupiedBy( board, dstfile, dstrank )
			# if same color, pass the "protect" through...
			if occ_color == colorOf(dstpiece):
				canmove.append( move )
				continue
			# if enemy king would be captured, pass the "attack" through
			if dstpiece == enemyking:
				canmove.append( move )
				continue
			# if a king move, test that destination is not in check
			if occupant in "Kk":
				verboten = getVerboten( occupant, whites, blacks )
				# cannot castle out of check
				if dstmove in ["ck", "cq"] and kingChecked(srcfile, srcrank, verboten):
					continue
				# cannot castle through check
				if dstmove == "ck" and kingChecked(dstfile-1, dstrank, verboten):
					continue
				if dstmove == "cq" and kingChecked(dstfile+1, dstrank, verboten):
					continue
				# cannot move to empty checked square
				if dstpiece == CK.SQ_EMPTY and kingChecked(dstfile, dstrank, verboten):
					continue
			# try the move and test if friendly king is in check
			# - every try starts from the same position
			movboard = FEN.putFen( fen )
			movboard, movcaptured = makeMove( movboard, dstfile, dstrank, srcfile, srcrank )
			movsquares, movwhites, movblacks = allMoves( movboard )
			# we could make this slightly more efficient by updating only if friendly king moved
			# - but the logic would be more complicated
			kingfile, kingrank = findKing( movboard, friendlyking )
			kingverboten = getVerboten( friendlyking, movwhites, movblacks )
			if not kingChecked(kingfile, kingrank, kingverboten):
				canmove.append( move )
		# legal moves for this square
		allsquares[ square ] = canmove
	# leave the board as we found it
	board = FEN.putFen( fen )

	# if any moves were eliminated, counts have to be updated
	# - should we not do this if no moves were eliminated ?
	whites, blacks = canReach( board, allsquares )

	return allsquares, whites, blacks

# ----------------------------

def getCount(colorcount, file, rank):
	'''how many pieces can reach this square ?'''
	return colorcount[ file ][ rank ]

def getMoves(moves, square):
	'''what moves are possible from this square ?'''
	return moves[ square ]

def getMoveCount(board, turncolor, allsquares):
	'''count how many moves a side can make'''
	movecnt = 0
	for square in allsquares.keys():
		sqfile, sqrank = sq2fr( square )
		occupant = occupiedBy( board, sqfile, sqrank )
		if colorOf(occupant) == turncolor:
			for dstdir, dstfile, dstrank in allsquares[square]:
				dstoccupant = occupiedBy( board, dstfile, dstrank )
				if turncolor != colorOf(dstoccupant):
					movecnt += 1

	return movecnt

def getBalance(board):
	'''get material balance of board'''
	balance = 0
	for file in range(1, 9):
		for rank in range(1, 9):
			occupant = occupiedBy( board, file, rank )
			balance += _CM.POINTVALUE[ occupant ]

	return balance

def getInsufficient(board):
	'''neither side can win because material insufficient ?'''
	# this considers only some of the most common cases

	def insufficient(bcount, ncount, pcount):
		# two bishops ?
		if bcount > 1:
			return False
		# bishop and knight ?
		if bcount > 0 and ncount > 0:
			return False

		# could be:
		# - one bishop and no knights
		# - no bishop and no, one or two knights
		
		# accurate but very rough
		# - always insufficient if true, but may be insufficient if if not true
		return pcount < 1

	whiteBishop = blackBishop = 0
	whiteKnight = blackKnight = 0
	whitePawn = blackPawn = 0
	for file in range(1, 9):
		for rank in range(1, 9):
			match occupiedBy(board, file, rank):
				case "Q" | "q" | "R" | "r":
					return False
				case "B":
					whiteBishop += 1
				case "b":
					blackBishop += 1
				case "N":
					whiteKnight += 1
				case "n":
					blackKnight += 1
				case "P":
					whitePawn += 1
				case "p":
					blackPawn += 1
				case _:
					pass

	winsufficient = insufficient( whiteBishop, whiteKnight, whitePawn )
	binsufficient = insufficient( blackBishop, blackKnight, blackPawn )

	return winsufficient and binsufficient

def tactic(board, piece, square, allsquares, whites, blacks):
	'''check if last piece move was a tactic'''
	# we are somewhat conservative in our response
	# - it is true if we say it, but we may not always say it
	result = CK.OC_NONE
	# a "dummy" piece ?
	if piece == CK.SQ_EMPTY:
		return result

	attval = _CM.ABSVALUE[ piece ]
	att_color = colorOf( piece )
	sqfile, sqrank = sq2fr( square )
	attacker, defender = (whites, blacks) if isWhite(att_color) else (blacks, whites)

	# is attacker itself more attacked than defended ?
	if attacker[sqfile][sqrank] < defender[sqfile][sqrank]:
		result |= CK.OC_ATTACKED

	forkable = attacked = 0
	incheck = False
	for direction, file, rank in allsquares[square]:
		occupant = occupiedBy( board, file, rank )
		if occupant == CK.SQ_EMPTY:
			continue

		# if same color, did this move create a battery ?
		if colorOf(occupant) == att_color:
			if piece in _CM.PC_RANK_SLIDER and occupant in _CM.PC_RANK_SLIDER and direction in ["n", "s", "e", "w"]:
				result |= CK.OC_BATTERY
			# an odd promotion might have left two bishops of the same color...
			if piece in _CM.PC_DIAG_SLIDER and occupant in _CM.PC_DIAG_SLIDER and direction in ["ne", "se", "sw", "nw"]:
				result |= CK.OC_BATTERY
			continue

		# how many attackers/defenders does enemy have ?
		attnum = attacker[ file ][ rank ]
		defnum = defender[ file ][ rank ]
		# how valuable is enemy piece ?
		defval = _CM.ABSVALUE[ occupant ]

		# enemy king attacked ?
		if occupant in "Kk":
			result |= CK.OC_DOUBLE if attnum > 1 else CK.OC_CHECK
			incheck = True

		# friendly piece attacks another enemy piece?
		# - technically, any square with an enemy piece is attacked
		# - practically, it must be at least as valuable or have fewer defenders
		if attval <= _CM.ABSVALUE[occupant] or  attnum > defnum:
			forkable += 1	# maybe, we'll see
		if attval < _CM.ABSVALUE[occupant] or attnum > defnum:
			attacked += 1	# definitely attack

		# only sliding pieces can skewer or pin
		if piece not in _CM.PC_SLIDER:
			continue

		# how to get to next square
		dltfile, dltrank = _CM.MOVEDELTAS[ direction ]
		nxtfile = file
		nxtrank = rank
		nxtoccupant = CK.SQ_EMPTY
		# while we're on the board...
		while 1 <= nxtfile <= 8 and 1 <= nxtrank <= 8 and nxtoccupant == CK.SQ_EMPTY:
			nxtfile += dltfile
			nxtrank += dltrank
			nxtoccupant = occupiedBy( board, nxtfile, nxtrank )

		# is there an obscured enemy piece on the far side of the defender ?
		if colorOf(nxtoccupant) == colorOf(occupant):
			obsval = _CM.ABSVALUE[ nxtoccupant ]
			# is the obscured piece worth more than attacker or is overwhelmed ?
			if ( (attval < _CM.ABSVALUE[nxtoccupant])
				or (attacker[nxtfile][nxtrank] > defender[nxtfile][nxtrank])
				):
				# a pin ?
				# - technically, any obscured piece that has a higher value than the defender
				# - practically, we also made sure it is worth taking
				if defval < obsval:
					result |= CK.OC_PIN
				# a skewer ?
				# - technically, any obscured piece that has a lower value than the defender
				# - practically, we also made sure it is worth taking
				elif defval > obsval:
					result |= CK.OC_SKEWER

	# what did we find ?
	match forkable:
		case 2:
			result |= CK.OC_FORK
		case 3:
			result |= CK.OC_FORK3
		# these are pretty rare, but possible
		case 4 | 5| 6 | 7:
			result |= CK.OC_FORKM
		# 'attacked' is always less than or equal to 'forkable'
		case _:
			# a check is an attack, but we don't explicitly say so
			if attacked == 1 and not incheck:
				result |= CK.OC_ATTACK

	return result

def isLegal(board):
	'''legal position check'''
	# this is not an exhaustive check

	# pawns cannot be on first or eigth ranks
	wking = bking = 0
	for file in range(1, 9):
		for rank in range(1, 9):
			match occupiedBy(board, file, rank):
				case "K":
					wking += 1
					wloc = ( file, rank )
				case "k":
					bking += 1
					bloc = ( file, rank )
				case "P" | "p" if rank in [1, 8]:
					return False
				case _:
					pass

	# must have exactly one king on each side
	if wking != 1 or bking != 1:
		return False

	# we assume that if we find these, they remain legal
	castling = ""
	if occupiedBy(board, 5, 1) == "K" and occupiedBy(board, 8, 1) == "R":
		castling = f"{castling}K"
	if occupiedBy(board, 5, 1) == "K" and occupiedBy(board, 1, 1) == "R":
		castling = f"{castling}Q"
	if occupiedBy(board, 5, 8) == "k" and occupiedBy(board, 8, 8) == "r":
		castling = f"{castling}k"
	if occupiedBy(board, 5, 8) == "k" and occupiedBy(board, 1, 8) == "r":
		castling = f"{castling}q"
	FEN.setCastle( castling if castling != "" else None )

	squares, whites, blacks = potentialMoves( board )

	# kings in check ?
	file, rank = wloc
	wcheck = bool(blacks[ file ][ rank ] > 0)
	file, rank = bloc
	bcheck = bool(whites[ file ][ rank ] > 0)

	# cannot both be in check
	if wcheck and bcheck:
		return False
	# if white is in check, white must move next
	if wcheck:
		FEN.setWhoseMove( CK.PC_WHITE )
	# if black is in check, black must move next
	elif bcheck:
		FEN.setWhoseMove( CK.PC_BLACK )

	# can the side to move make any ?
	if not getMoveCount(board, FEN.getWhoseMove(), squares):
		return False

	# no enpassant square
	FEN.setenPassant()
	# half move clock to zero
	FEN.sethalfMove()
	# full move clock to one
	FEN.setfullMove()

	return True
