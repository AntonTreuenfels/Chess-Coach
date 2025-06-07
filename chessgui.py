# Chess GUI

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

# first created: 02/15/25
# last revision: 05/30/25

#--------------------
# Python modules
import tkinter as tk
from tkinter import messagebox
# program modules
import chessmoves as CM
import fen as FEN
import chessconstants as CK
import opendatabase as ODB
import sqldatabase as SQL
#--------------------

# global constants

CLR_LITESQ = "antiquewhite"	# light square
CLR_DARKSQ = "bisque3"		# dark square

CLR_LITEPC = "#BA020E"		# light piece
CLR_DARKPC = "black"		# dark piece

CLR_ARROW = "black"			# marked square
CLR_CANREACH = "blue"		# "can reach" square
CLR_PROTECT = "pale green"	# protected square
CLR_ATTACK = "#F33A6A"		# attacked square (rose)
CLR_ATTACKFG = "black"		# attacked square text
CLR_ATTACKKG = "yellow"		# attacked king

CLR_PLACERBG = "bisque2"	# piece chooser
CLR_PLACERFG = "black"		# piece chooser text

CLR_BOARD = "saddle brown"	# chess board frame color
FRM_WIDTH = 8				# chess board frame pixel width

CRS_DROP = "hand2"
CRS_DFLT = ""

# just a reminder of pixel/point/96ppi screen relations

# 1 pixel = 1/96 inch
# 1 point = 1/72 inch
# N point = N * 96/72 pixels
# 18 point = 18 * 96 / 72 = 24 pixels

FNT_TEXT = "TkFixedFont"

FNT_POINTS = 18
FNT_PIXELS = int(FNT_POINTS * 96 / 72)

ICO_POINTS = 40				# icon point size

CONTROLSWIDTH = 17			# width of control column

# status/button texts
CM_WAITING = "Waiting..."
CM_ILLEGAL = "Illegal placement"

BT_TAKEBACK = "Take Back Move"
BT_NEXTMOVE = "Make Next Move"
BT_NEWGAME = "New Game"
BT_STARTMOVE = "Start Moves"
BT_PLACEPIECE = "Place Pieces"
BT_STOPPLACE = "Stop Placing"
BT_LOADMOVES = "Load Moves"
BT_SAVEMOVES = "Save Moves"
BT_RESTART = "Restart Coach"
BT_QUIT = "Quit Coach"

MB_REVIEW = "Review Moves"

# piece glyphs (Unicode)

PIECEGLYPH = {
	"K": "\u2654",		# white king
	"Q": "\u2655",		# white queen
	"R": "\u2656",		# white rook
	"B": "\u2657",		# white bishop
	"N": "\u2658",		# white knight
	"P": "\u2659",		# white pawn

	"k": "\u265A",		# black king
	"q": "\u265B",		# black queen
	"r": "\u265C",		# black rook
	"b": "\u265D",		# black bishop
	"n": "\u265E",		# black knight
	"p": "\u265F",		# black pawn

	".": "",			# empty
	"x": "\u270B",		# stop
	}

# large arrow glyphs (Unicode)

# "n", "s" and "w" (especially) are emoji glyphs with VS15 and VS16 variants
# - it does not seem possible to force tkinter to render them consistently
# without first peforming unexplained initializations prior to using them

'''
ARROWGLYPH = {
	 "n": "\u2B06",		# straight up
	"ne": "\u2B08",		# up and right
	 "e": "\u2B95",		# straight right
	"se": "\u2B0A",		# down and right
	 "s": "\u2B07",		# straight down
	"sw": "\u2B0B",		# down and left
	 "w": "\u2B05",		# straight left
	"nw": "\u2B09",		# up and left
	"k1": "\u2B08",		# up two, right one
	"k2": "\u2B08",		# up one, right two
	"k3": "\u2B0A",		# down one, right two
	"k4": "\u2B0A",		# down two, right one
	"k5": "\u2B0B",		# down two, left one
	"k6": "\u2B0B",		# down one, left two
	"k7": "\u2B09",		# up one, left two
	"k8": "\u2B09",		# up two, left one
	"P2": "\u2B06",		# up two
	"p2": "\u2B07",		# down two
	"ck": "\u2B95",		# right two
	"cq": "\u2B05",		# left two
	}
'''

# these glyphs do not have any variants
# - and so tkinter renders them consistently
# without any special treatment

ARROWGLYPH = {
	 "n": "\U0001F879",		# straight up
	"ne": "\U0001F87D",		# up and right
	 "e": "\U0001F87A",		# straight right
	"se": "\U0001F87E",		# down and right
	 "s": "\U0001F87B",		# straight down
	"sw": "\U0001F87F",		# down and left
	 "w": "\U0001F878",		# straight left
	"nw": "\U0001F87C",		# up and left
	"k1": "\U0001F87D",		# up two, right one
	"k2": "\U0001F87D",		# up one, right two
	"k3": "\U0001F87E",		# down one, right two
	"k4": "\U0001F87E",		# down two, right one
	"k5": "\U0001F87F",		# down two, left one
	"k6": "\U0001F87F",		# down one, left two
	"k7": "\U0001F87C",		# up one, left two
	"k8": "\U0001F87C",		# up two, left one
	"P2": "\U0001F879",		# up two
	"p2": "\U0001F87B",		# down two
	"ck": "\U0001F87A",		# right two
	"cq": "\U0001F878",		# left two
	}

# global variables

currBoard = None		# current location of all pieces on board
currMoves = None		# possible moves in current position

whiteMoves = None		# number of white pieces that can reach each square
blackMoves = None		# number of black pieces that can reach each square

fromButton = None		# square piece is moving from

gameRunning = False		# game is running
placePieces = False		# manual setup in progress
promotePawn = False		# promoting a pawn
chooseSaveAs = False	# recording puzzle/game

recordID = None			# id of saved record
placedFen = None		# fen of a manual setup or first fen of saved record

fenPositions = None		# fen positions in saved record

chooseRecord = list()	# move record descriptions
chosenRecord = list()	# move record ID and start fen

chessBoard = dict()		# display frame associated with each chessboard square

# GUI windows we may want to refer to after creation

rootWin = None			# main window handle
lftFrame = None			# left frame handle
rgtFrame = None			# right frame handle

# GUI piece choosers

whitePromote = None		# tracker
whitePromoter = None	# display

blackPromote = None		# tracker
blackPromoter = None	# display

piecePlace = None		# tracker
piecePlacer = None		# display

# GUI saved puzzle/game chooser

savedChoose = None		# tracker
savedChooser = None		# display

# GUI "save as" puzzle/game chooser

saveAsChoose = None		# tracker
saveAsChooser = None	# display

# GUI status

lastMoveStatus = None	# tracker
moveComment = None		# tracker
toMoveStatus = None		# tracker
movesAvailable = None	# tracker
materialBalance = None	# tracker

# GUI control buttons

butTakeBack = None
butNextMove = None
butNewGame = None
butStartMoves = None
butPlacePieces = None
butStopPlacing = None
butLoadMoves = None
butSaveMoves = None
butRestart = None
butQuit = None

# GUI user options

algebraicMoves = None	# tracker
showSqName = None		# tracker
showWhitePreview = None	# tracker
showBlackPreview = None	# tracker
showWhiteReach = None	# tracker
showBlackReach = None	# tracker
showWhiteMoveCnt = None	# tracker
showBlackMoveCnt = None	# tracker
showWhiteTactic = None	# tracker
showBlackTactic = None	# tracker
showWhitePosName = None	# tracker
showBlackPosName = None	# tracker

# -------------------

def enableButtons(these):
	for button in these:
		button.config( state=tk.NORMAL,relief=tk.RAISED )

def isEnabled(button):
	return button.cget("state") == tk.NORMAL

def disableButtons(these):
	for button in these:
		button.config( state=tk.DISABLED, relief=tk.RAISED )

def isDisabled(button):
	return button.cget("state") == tk.DISABLED

def resetButtons():
	'''set control buttons to start state'''
	# - Restart and Quit are always enabled; we don't worry about them after this
	disableButtons( [butTakeBack, butNextMove, butStartMoves, butStopPlacing, butSaveMoves] )
	enableButtons( [butNewGame, butPlacePieces, butLoadMoves, butRestart, butQuit] )

def clearStatus(labels):
	for label in labels:
		label.set( "" )

def clearComment():
	moveComment.set( "" )

# -------------------

def getSquare(file, rank):
	sqname = CM.fr2sq( file, rank )
	frame = chessBoard[ sqname ]
	button = frame.winfo_children()[0]
	return ( sqname, frame, button )

def getArrow(move):
	return ARROWGLYPH[ move ]

def getGlyph(piece):
	return PIECEGLYPH[ piece ]

def getValue(piece):
	return "\u221E" if piece in "Kk" else CM.valueOf( piece )

# -------------------

def showChessboard():
	'''draw the current board position'''
	# this erases anything that is not a piece glyph
	# - we'll just hoist this next bit up to save a little time and code space
	whtshowcnt = whiteMoves is not None and showWhiteReach.get()
	blkshowcnt = blackMoves is not None and showBlackReach.get()
	for file in range(1, 9):
		for rank in range(1, 9):
			sqname, frame, button = getSquare( file, rank )
			# show name ?
			namtxt = sqname if showSqName.get() else "  "
			# show how many pieces can reach this square ?
			count = whiteMoves[file][rank] if whtshowcnt else 0
			whttxt = f"{count:2}" if count > 0 else "  "
			count = blackMoves[file][rank] if blkshowcnt else 0
			blktxt = f"{count:2}" if count > 0 else "  "
			title = f"{whttxt}   {namtxt}  {blktxt} "
			bg_color = frame.dfltcolor
			frame.config( text=title, bg=bg_color )
			# show the glyph for this square
			piece = CM.occupiedBy( currBoard, file, rank )
			# is it a king in check ?
			match piece:
				case "K" if blackMoves[file][rank] > 0:
					fg_color = CLR_ATTACKKG
					bg_color = CLR_ATTACK
				case "k" if whiteMoves[file][rank] > 0:
					fg_color = CLR_ATTACKKG
					bg_color = CLR_ATTACK
				case _:
					fg_color = CLR_LITEPC if CM.isWhite(CM.colorOf(piece)) else CLR_DARKPC
			# use the more "filled-in" glyph
			glyph = getGlyph( piece.lower() )
			button.config( text=glyph, fg=fg_color, activeforeground=fg_color, bg=bg_color, activebackground=bg_color, cursor=CRS_DFLT )

def doPlace(frame, piece):
	'''put a piece on the chessboard'''
	global currBoard, currMoves, whiteMoves, blackMoves

	file, rank = CM.sq2fr( frame.name )
	currBoard[ rank ][ file ] = piece
	currMoves, whiteMoves, blackMoves = CM.potentialMoves( currBoard )
	showChessboard()

# -------------------

def optEnabled(color, whitevar, blackvar):
	'''get state of boolean variable'''
	if color == CK.PC_WHITE:
		return whitevar.get()
	else:
		return blackvar.get()

# -------------------

def showMoves(frame, button):
	'''check if square has a piece that can be moved'''
	# file and rank of this frame
	sqfile, sqrank = CM.sq2fr( frame.name )
	# if no piece here, then can't be start of any move
	occupant = CM.occupiedBy( currBoard, sqfile, sqrank )
	if occupant == CK.SQ_EMPTY:
		return

	# what color is occupant ?
	occ_color = CM.colorOf( occupant )
	whitepiece = CM.isWhite( occ_color )

	# are we playing a game ?
	if gameRunning:

		# can we show the moves available to the color whose turn it is ?
		move_color = FEN.getWhoseMove()
		showmoves = optEnabled( move_color, showWhitePreview, showBlackPreview )

		# can this piece be moved ?
		moveable = (occ_color == move_color)
		# can we drop this piece anywhere ?
		movicon = CRS_DROP if moveable else CRS_DFLT

	# we're placing pieces
	else:
		showmoves = True
		moveable = False
		movicon = CRS_DFLT

	# where can this piece move to ?
	possible = currMoves[ frame.name ]

	# capture values (if any)
	capval = list()
	# go through each possible move and mark buttons
	for move, file, rank in possible:
		dstsquare, dstframe, dstbutton = getSquare( file, rank )
		# watch for enpassant pawn
		match occupant:
			case "P" if dstsquare == FEN.getenPassant():
				dstoccupant = "p"
			case "p" if dstsquare == FEN.getenPassant():
				dstoccupant = "P"
			case _:
				dstoccupant = CM.occupiedBy( currBoard, file, rank )
		dstcolor = CM.colorOf( dstoccupant )
		# can we show possible moves by changing square glyphs ?
		if showmoves:
			# if square is empty, mark it with an arrow
			if dstoccupant == CK.SQ_EMPTY:
				txtval = getArrow( move )
				fgcolor = CLR_ARROW
				bgcolor = dstframe.dfltcolor
				curicon = movicon
			# if square has a friendly piece, mark it protected
			elif dstcolor == occ_color:
				txtval = getGlyph( dstoccupant.lower() )
				fgcolor = CLR_LITEPC if whitepiece else CLR_DARKPC
				bgcolor = CLR_PROTECT
				curicon = CRS_DFLT
			# square has an enemy piece, mark it attacked
			else:
				txtval = f"{getGlyph(occupant)}x{getGlyph(dstoccupant)}"
				fgcolor = CLR_ATTACKKG if dstoccupant in "Kk" else CLR_ATTACKFG
				bgcolor = CLR_ATTACK
				curicon = movicon
				capval.append( f"{getGlyph(dstoccupant)}{dstsquare}:{getValue(dstoccupant)}" )
			# do the actual marking
			dstframe.config( bg=bgcolor )
			dstbutton.config( text=txtval, fg=fgcolor, bg=bgcolor, cursor=curicon )
		# no, but we still use the cursor to indicate legal moves
		elif moveable and dstcolor != occ_color:
			dstbutton.config( cursor=CRS_DROP )

		# what are the values of any enemy pieces this piece can capture ?
		# - this shows up to seven captures; beyond that two captures are partially hidden
		# - this comment will get overwritten if game ends
		if len(capval) > 4:
			text = f"{' '.join(capval)}"
		elif len(capval) > 0:
			text = f"{'  '.join(capval)}"
		else:
			text = ""
		moveComment.set( text )

def showEndGame(checkmate):
	'''show moves of the side that ended game'''
	endingside = FEN.getOppMove()
	enemyking = "k" if CM.isWhite(endingside) else "K"
	kgfile, kgrank = CM.findKing( currBoard, enemyking )
	for file in range(1,9):
		for rank in range(1,9):
			occupant = CM.occupiedBy( currBoard, file, rank )
			if CM.colorOf(occupant) == endingside:
				square, frame, button = getSquare( file, rank )
				# if stalemante, show the moves of all pieces
				if not checkmate:
					showMoves( frame, button )
				# if checkmate, show only the moves of the checkmating piece(s)
				else:
					for move, mvfile, mvrank in currMoves[square]:
						if mvfile == kgfile and mvrank == kgrank:
							showMoves( frame, button )

# -------------------

def disambigMove(srcpiece, srcname, dstname, couldhavemoved):
	'''disambiguate move'''
	srcfile, srcrank = CM.sq2fr( srcname )
	dstfile, dstrank = CM.sq2fr( dstname )

	# tricky: 'srcpiece' is already on 'dstname', not 'srcname'
	alsoreach = list()
	for square, moves in couldhavemoved.items():
		for move, file, rank in moves:
			if file != dstfile or rank != dstrank:
				continue
			sqfile, sqrank = CM.sq2fr( square )
			if srcpiece == CM.occupiedBy(currBoard, sqfile, sqrank):
				alsoreach.append( square )

	match len(alsoreach):
		case 0:	# no disambiguation necessary
			return ""
		case 1: # only one other piece of same kind could have reached
			file, rank = CM.sq2fr( alsoreach.pop() )
			return srcname[0] if file != srcfile else srcname[1]
		case _: # more than one other piece of same kind could have reached
			return srcname

def getMoveDesc(srcpiece, captured, srcname, dstname, disambig):
	'''get move description'''
	srcfile, srcrank = CM.sq2fr( srcname )
	dstfile, dstrank = CM.sq2fr( dstname )

	# algebraic ?
	if algebraicMoves.get():
		match srcpiece:
			# king castled ?
			case "K" | "k" if dstfile - srcfile == 2:
				return "O-O"
			case "K" | "k" if srcfile - dstfile == 2:
				return "O-O-O"
			# pawn promoted ?
			case "P" | "p" if "?" in captured:
				# format is "P?{captured}{promotedto}"
				suffix = f"={captured[3].upper()}"
				if captured[2] == CK.SQ_EMPTY:
					return f"{dstname}{suffix}"
				else:
					return f"{srcname[0]}x{captured[2].upper()}{suffix}"
			# pawn captured ?
			case "P" | "p" if captured != CK.SQ_EMPTY:
				prefix = f"{srcname[0]}x"
				# en passant capture?
				if captured == "px":
					return f"{prefix}{CM.fr2sq(dstfile, dstrank-1)}"
				elif captured == "Px":
					return f"{prefix}{CM.fr2sq(dstfile, dstrank+1)}"
				# ordinary capture
				else:
					return f"{prefix}{dstname}"
			case "P" | "p":
				return dstname
			case _:
				pass

		if captured == CK.SQ_EMPTY:
			return f"{srcpiece.upper()}{disambig}{dstname}"
		else:
			return f"{srcpiece.upper()}{disambig}x{dstname}"

	# English-like
	else:
		if disambig != "":
			srctxt = f"{getGlyph(srcpiece)} on {srcname}"
		else:
			srctxt = f"{getGlyph(srcpiece)}"
		dsttxt = f" on {dstname}"

		match srcpiece:
			# king castled ?
			case "K" | "k" if dstfile - srcfile == 2:
				return f"{srctxt} Castled Kingside"
			case "K" | "k" if srcfile - dstfile == 2:
				return f"{srctxt} Castled Queenside"
			# en passant capture?
			case "P" if captured == "px":
				return f"{srctxt} en passant {getGlyph('p')}{dsttxt}"
			case "p" if captured == "Px":
				return f"{srctxt} en passant {getGlyph('P')}{dsttxt}"
			# pawn promoted ?
			case "P" | "p" if "?" in captured:
				promotedto = f" promoted to {getGlyph(captured[3])}{dsttxt}"
				if captured[2] == CK.SQ_EMPTY:
					return f"{srctxt}{promotedto}"
				else:
					return f"{srctxt} captured {getGlyph(captured[2])}{promotedto}"
			case _:
				pass

		if captured == CK.SQ_EMPTY:
			return f"{srctxt} moved to {dstname}" 
		else:
			return f"{srctxt} captured {getGlyph(captured)}{dsttxt}" 

def checkTactic(tactic, text):
	'''test if last move resulted in a tactic executed'''

	def moretext(this, add):
		return add if this is None else f"{this} + {add}"

	lastmoved = FEN.getOppMove()

	# can we show the result ?
	if not optEnabled(lastmoved, showWhitePosName, showBlackPosName):
		text = None

	# did last move lead to a tactic executed ?
	if text is None and optEnabled(lastmoved, showWhiteTactic, showBlackTactic):
		if tactic & CK.OC_CHECK:
			text = "Check"
		if tactic & CK.OC_DOUBLE:
			text = "Double Check"
		if tactic & CK.OC_FORK:
			text = moretext( text, "Fork" )
		if tactic & CK.OC_FORK3:
			text = moretext( text, "Triple Fork" )
		if tactic & CK.OC_FORKM:
			text = moretext( text, "Multiple Fork" )
		if tactic & CK.OC_PIN:
			text = moretext( text, "Pin" )
		if tactic & CK.OC_SKEWER:
			text = moretext( text, "Skewer" )
		if tactic & CK.OC_BATTERY:
			text = moretext( text, "Battery" )
		if tactic & CK.OC_ATTACK:
			text = moretext( text, "Attack" )
		if tactic & CK.OC_ATTACKED:
			text = moretext( text, "Attacked !" )

	return "" if text is None else text

def checkGameOver(text, incheck, movecnt):
	'''test if game is over (or nearly so)'''
	global gameRunning

	drawbyreps = FEN.lastRepeated()
	drawbymoves = FEN.gethalfMove()
	if movecnt < 1:
		showEndGame( incheck )
		if incheck:
			text = f"Checkmate: {FEN.getOppMove()} Wins"
		else:
			text = f"Draw: Stalemate - {FEN.getWhoseMove()} Has No Move"
		gameRunning = False
	elif drawbyreps > 2:
		text = f"Draw: {FEN.getOppMove()} Position Repeated Three Times"
		gameRunning = False
	elif drawbymoves >= 100:
		text = "Draw: 50 Moves Without Pawn Move or Capture"
		gameRunning = False
	elif CM.getInsufficient(currBoard):
		text = "Draw: Insufficient Material To Checkmate"
		gameRunning = False
	elif not FEN.moreMoves(fenPositions):
		text = "Correct Solution !"
		gameRunning = False
	elif drawbyreps > 1:
		text = f"{FEN.getOppMove()} Position Repeated Twice"
	elif drawbymoves >= 90 and drawbymoves % 2 == 0:
		text = f"Draw in {(100-drawbymoves)/2} Moves"
	elif movecnt == 1 and not incheck:
		text = f"{FEN.getWhoseMove()} Move Forced"

	if not gameRunning:
		disableButtons( [butTakeBack, butNextMove, butStartMoves, butStopPlacing] )
		enableButtons( [butNewGame, butPlacePieces, butLoadMoves, butSaveMoves] )

	return text

def updateBalance():
	# update material balance
	balance = CM.getBalance( currBoard )
	if balance > 0:
		materialBalance.set( f"{CK.PC_WHITE} +{balance}" )
	elif balance < 0:
		materialBalance.set( f"{CK.PC_BLACK} +{abs(balance)}" )
	else:
		materialBalance.set( "Even" )

def updateMove(pieces, squares, status=None):
	'''update display and FEN'''
	global currMoves, whiteMoves, blackMoves
	global gameRunning

	srcpiece, captured = pieces
	srcname, dstname = squares

	disambig = ""
	if status is None:
		# preliminary description of last move
		disambig = disambigMove( srcpiece, srcname, dstname, currMoves )
		lastmove = f"{srcpiece}{disambig}{dstname}" 
		movedesc = getMoveDesc( srcpiece, captured, srcname, dstname, disambig )

		# back to zero if pawn move or capture
		FEN.sethalfMove( srcpiece in "Pp" or captured != CK.SQ_EMPTY )

		# next full move if black just moved
		FEN.setfullMove( FEN.getWhoseMove() )

		# flip whose turn
		_= FEN.toggleWhoseMove()

	# update whose move
	whosemove = FEN.getWhoseMove()
	toMoveStatus.set( whosemove )

	# record fen of current position
	FEN.recordFen( currBoard )
	# do we have enough of them to take back a move ?
	enableButtons( [butTakeBack] ) if FEN.cantakeBack() else disableButtons( [butTakeBack] )

	# find available moves
	currMoves, whiteMoves, blackMoves = CM.potentialMoves( currBoard )
	showChessboard()

	if FEN.lastmoveBad(fenPositions):
		gameRunning = False
		disableButtons( [butNextMove] )
		moveComment.set( "Incorrect Move" )

	# did last move lead to a recognized position ? 
	# - we do this now so the move record is accurate
	text = ODB.openingComment( srcpiece, disambig, dstname )

	# update comment
	if gameRunning:
		enableButtons( [butNextMove] ) if FEN.canmoveNext(fenPositions) else disableButtons( [butNextMove] )
		tactic = CM.tactic( currBoard, srcpiece, dstname, currMoves, whiteMoves, blackMoves )
		text = checkTactic( tactic, text )
		# update values we will need several times
		incheck = bool( tactic & CK.OC_INCHECK )
		movecnt = CM.getMoveCount( currBoard, whosemove, currMoves )
		# do we need to change comment because game is over (or nearly so) ?
		text = checkGameOver( text, incheck, movecnt )
		moveComment.set( text ) 

	# last move was not a "dummy" move ?
	if status is None:
		status = movedesc
		if algebraicMoves.get() and incheck:
			status = f"{status}{'#' if movecnt < 1 else '+'}"
	lastMoveStatus.set( status )

	# update move count
	showavailable = optEnabled( whosemove, showWhiteMoveCnt, showBlackMoveCnt )
	text = "" if not showavailable else str(movecnt) if gameRunning else "0"
	movesAvailable.set( text )

	# update material balance
	updateBalance()

# -------------------

def dummyMove(status, fen):
	'''dummy (non-player) move'''
	global currBoard
	# an empty source square prevents the opening database from updating
	currBoard = FEN.putFen( fen )
	updateMove( (CK.SQ_EMPTY, CK.SQ_EMPTY), ("a1", "h8"), status )

def doMove(dstbutton, srcbutton):
	'''move a piece to destination square'''
	global currBoard

	def promote(frame, file, promoter, varname, captured):
		'''promote a pawn'''
		global promotePawn
		showChessboard()
		varname.set( "" )
		promoter.grid( column=min(file, 5) )
		promotePawn = True
		promoter.lift()
		promoter.wait_variable( varname )
		promoter.lower()
		newpiece = varname.get()
		promotePawn = False
		doPlace( frame, newpiece )

		# format is "[Pp]?{captured}{promotedto}"
		return f"{captured}{newpiece}"

	srcframe = srcbutton.master
	srcfile, srcrank = CM.sq2fr( srcframe.name )
	srcpiece = CM.occupiedBy( currBoard, srcfile, srcrank )
	dstframe = dstbutton.master
	dstfile, dstrank = CM.sq2fr( dstframe.name )
	# make the move on the board
	currBoard, captured = CM.makeMove( currBoard, dstfile, dstrank, srcfile, srcrank )
	if captured.startswith("P?"):
		captured = promote( dstframe, dstfile, whitePromoter, whitePromote, captured )
	elif captured.startswith("p?"):
		captured = promote( dstframe, dstfile, blackPromoter, blackPromote, captured )

	return ( srcpiece, captured ), ( srcframe.name, dstframe.name )

# -------------------

def updatePlace(frame, button):
	'''place a piece on chessboard'''

	piece = piecePlace.get()
	piecePlace.set( "x" )
	match piece:
		case CK.SQ_STOP:
			return
		case CK.SQ_EMPTY:
			text = f"Erased {frame.name}"
		case _:
			text = f"{getGlyph(piece)} placed on {frame.name}" 
	lastMoveStatus.set( text )

	doPlace( frame, piece ) 
	showMoves( frame, button )

	# show available moves
	movecnt = CM.getMoveCount( currBoard, FEN.getWhoseMove(), currMoves )
	movesAvailable.set( str(movecnt) )

	# update material balance
	updateBalance()

# -------------------

def hitSquare(button):
	''''chessboard square pressed'''
	global fromButton

	frame = button.master

	# is a game active now ?
	if gameRunning:
		# can we move a piece here ?
		if button.cget("cursor") == CRS_DROP:
			pieces, squares = doMove( button, fromButton )
			updateMove( pieces, squares )
			fromButton = None
		else:
			showChessboard()
			# hit the last square again ?
			if button == fromButton:
				clearComment()
				fromButton = None
			else:
				showMoves( frame, button )
				fromButton = button

	# are we placing pieces ? 
	elif placePieces:
		updatePlace( frame, button )

# -------------------

def makePlacer(parent, grow, gcol, tracker, display):
	'''make a piece placement chooser'''
	# make a label frame for the radiobutton
	frame = tk.LabelFrame( parent,
		text = "Choose Piece",
		font=(FNT_TEXT),
		)
	frame.grid( column=gcol, row=grow, columnspan=2, rowspan=3 )
	# make it hidden "below" sibling at start
	frame.lower()
	# assign the tracker variable
	globals()[ tracker ] = tk.StringVar( parent, "" )
	# make the piece select radio button itself
	for frow, pieces in enumerate(["KQRBNP", "kqrbnp", ".x"]):
		for fcol, piece in enumerate(pieces):
			tk.Radiobutton( frame,
				text=getGlyph(piece),
				value = piece,
				variable=globals()[tracker],
				fg=CLR_PLACERFG,
				bg=CLR_PLACERBG,
				indicatoron=False,
				font=( FNT_TEXT, ICO_POINTS ),
				height=1,
				width=2,
			).grid( column=fcol, row=frow, sticky="ew" )

	# make 'to move' toggle button
	button = tk.Button( frame,
		text="Toggle To Move",
		anchor=tk.CENTER,
		fg=CLR_PLACERFG,
		bg=CLR_PLACERBG,
		font=( FNT_TEXT, FNT_POINTS ),
		height=1,
		width=4,
		command=lambda: toMoveStatus.set( FEN.toggleWhoseMove() )
	).grid( column=2, row=2, columnspan=4, sticky="nesw" )

	# assign the display variable
	globals()[ display ] = frame

# -------------------

def makePromoter(parent, pieces, grow, gcol, tracker, display):
	'''make a radio button for pawn promotion'''
	# make a label frame for the radiobutton
	frame = tk.LabelFrame( parent,
		text="Promote To",
		font=(FNT_TEXT),
		)
	frame.grid( column=gcol, row=grow, columnspan=3 )
	# make it hidden "below" sibling at start
	frame.lower()
	# assign the tracker variable
	globals()[ tracker ] = tk.StringVar( parent, "" )
	# make the radio button itself
	for fcol, piece in enumerate(pieces):
		tk.Radiobutton( frame,
			text=getGlyph(piece),
			value = piece,
			variable=globals()[tracker],
			fg=CLR_PLACERFG,
			bg=CLR_PLACERBG,
			indicatoron=False,
			font=( FNT_TEXT, ICO_POINTS ),
			height=1,
			width=2,
		).grid( column=fcol, row=0, sticky="ew" )

	# assign the display variable
	globals()[ display ] = frame

# -------------------

def makeChooseSaved(parent, grow, gcol, tracker, display):
	'''make a saved puzzle/game chooser'''
	# make a label frame for the listbox
	# - 'frame' is None if we try to do tk.LabelFrame().grid()
	frame = tk.LabelFrame( parent,
		text = "Choose Record",
		font=(FNT_TEXT),
		)
	frame.grid( column=gcol, row=grow, columnspan=2, rowspan=4 )
	# make it hidden "below" sibling at start
	frame.lower()
	# assign the tracker variable
	globals()[ tracker ] = tk.StringVar( parent, "" )
	# make the listbox itself
	box = tk.Listbox( frame,
			listvariable=globals()[tracker],
			font=( FNT_TEXT, FNT_POINTS ),
			height=10,
		)
	# position on grid
	# - 'box' is None if we try to do tk.Listbox().grid()
	box.grid( column=0, row=0, sticky="ew" )
	# bind events
	box.bind( "<<ListboxSelect>>", lambda event: showFirstFen(event.widget) )
	box.bind( "<Double-Button-1>", lambda event: startFirstFen(event.widget) )

	# assign the display variable
	globals()[ display ] = frame

def makeChooseSaveAs(parent, grow, gcol, tracker, display):
	'''make a save fen chooser'''
	# make a label frame for the chooser
	# - 'frame' is None if we try to do tk.LabelFrame().grid()
	frame = tk.LabelFrame( parent,
		text = "Save As",
		font=(FNT_TEXT),
		)
	frame.grid( column=gcol, row=grow, columnspan=2, rowspan=2 )
	# make it hidden "below" sibling at start
	frame.lower()
	# assign the tracker variable
	globals()[ tracker ] = tk.StringVar( parent, "" )
	# make the piece select radio button itself
	for key, value in SQL.DB_DESC_TYPES.items():
		frow, fcol, ftype = value
		tk.Radiobutton( frame,
			text=key,
			value = ftype,
			variable=globals()[tracker],
			fg=CLR_PLACERFG,
			bg=CLR_PLACERBG,
			indicatoron=False,
			font=( FNT_TEXT, FNT_POINTS ),
			height=1,
#				width=2,
		).grid( column=fcol, row=frow, sticky="ew" )

	# assign the display variable
	globals()[ display ] = frame

# -------------------

def makeSquare(parent, file, rank):
	'''make one chessboard square'''
	# the name and color of this square
	sqname = CM.fr2sq( file, rank )
	sqcolor = CLR_LITESQ if (file%2 + rank%2)%2 else CLR_DARKSQ

	# we'll make the containing frame with the label non-null
	# - this will make the label as large as it will ever be
	frame = tk.LabelFrame( parent,
		bg=sqcolor,
		text=sqname,
		labelanchor=tk.N,
		borderwidth=0,
		font=(FNT_TEXT),
	)
	# this arrangement puts white at bottom of chessboard
	frame.grid( column=file-1, row=8-rank )
	# we need these later
	frame.dfltcolor = sqcolor
	frame.name = sqname

	# a button inside each frame
	button = tk.Button( frame,
		text="",
		anchor=tk.CENTER,
		bg=sqcolor,			# it'd be nice if we could make this transparent and just color frame background
		font=( FNT_TEXT, ICO_POINTS ),
		height=1,			# this height and width makes frame look square-ish
		width=4,
		borderwidth=0,		# hide borders between buttons
	)
	# put button in frame
	button.grid(column=0, row=0, sticky="ew")
	# bind this event
	button.bind("<Button>", lambda event: hitSquare(event.widget))

	return ( sqname, frame )

def makeBoard(parent):
	'''make the chessboard'''
	parent.config( bg=CLR_BOARD, bd=FRM_WIDTH )
	for file in range(1,9):
		for rank in range(1,9):
			sqname, frame = makeSquare( parent, file, rank )
			# add frame to dictionary
			chessBoard[ sqname ] = frame

def makeGroupFrame(parent, textval, grow, gcol):
	'''make a frame for grouping'''
	frame = tk.LabelFrame( parent,
			text=f" {textval} ",
			labelanchor=tk.N,
			height=1 * FNT_PIXELS,
			width=CONTROLSWIDTH * FNT_PIXELS,
			pady=10,
		)
	frame.grid( row=grow, column=gcol,  sticky="news" )
	frame.grid_rowconfigure( 0, weight=1 )
	frame.grid_columnconfigure( 0, weight=1 )
	frame.propagate( 0 )

	return frame

def makeControlButton(parent, textval, grow, gcol, control, eventfnc=None):
	'''make a control button'''
	button = tk.Button( parent,
			text=textval,
			height=1,
			width=CONTROLSWIDTH,
			font=(FNT_TEXT, FNT_POINTS),
		)
	button.grid( row=grow, column=gcol, sticky="ew" )
	if eventfnc is not None:
		button.bind( "<Button>", lambda event: eventfnc(event.widget) )

	globals()[ control ] = button

def makeStatusLabel(parent, textval, grow, gcol, tracker):
	''' make status label'''
	# assign the variable value that will track what the label shows
	globals()[ tracker ] = tk.StringVar( parent, "" )
	# make a frame for label
	frame = makeGroupFrame( parent, textval, grow, gcol )
	# make a label in this frame
	label = tk.Label( frame,
		textvariable=globals()[tracker],
		font=(FNT_TEXT, FNT_POINTS),
		height=1,
		width=CONTROLSWIDTH,
		)
	label.grid( sticky="ew" )

def makeBooleanOpt(parent, tracker, textval, grow, gcol, docommand):
	'''make on/off checkbox'''
	# assign tracker variable
	globals()[ tracker ] = tk.BooleanVar( parent, True )
	cbutton = tk.Checkbutton( parent,
		text=textval,
		variable=globals()[tracker],
		height=1,
		width=CONTROLSWIDTH,
		font=(FNT_TEXT, FNT_POINTS),
		anchor=tk.W,
		command=docommand,
	)
	cbutton.grid( row=grow, column=gcol, sticky="nesw" )

def makeBoardOpt(parent, tracker, textval, grow, gcol):
	'''make chessboard display option checkbox'''
	makeBooleanOpt( parent, tracker, textval, grow, gcol, showChessboard )

def makeStatusOpt(wparent, wtracker, bparent, btracker, textval, grow, gcol):
	'''make status display option checkbox'''
	makeBooleanOpt( wparent, wtracker, textval, grow, gcol, redoStatus )
	makeBooleanOpt( bparent, btracker, textval, grow, gcol, redoStatus )

# -------------------

def setGeometry(this):
	'''center display on screen''' 
	# originally developed on a 2560x1440 screen
	# - "naturally" sized by tkinter at 1620x968
	# - we might use at 1920x1080 or even 1366x768
	this.update_idletasks()
	screen_width = this.winfo_screenwidth()
	screen_height = this.winfo_screenheight()
	if screen_width >= 1720 and screen_height >= 1068:
		width = 1620
		height = 968
	else:
		width = screen_width - 150
		height = int( width * (968/1620) )

	# center on screen
	x = (screen_width - width) // 2
	y = (screen_height - height) // 2
	this.geometry(f"{width}x{height}+{x}+{y}")

# -------------------

def stopChoosers():
	'''stop all chooser from running'''
	# make sure no choosers showing and no "wait variable" loops running
	# - at most only one is, but this shouldn't hurt anything
	# if there is no list in the listbox, don't try to get value of its variable
	savedChooser.lower()
	if savedChooser.size() != 0:
		savedChoose.set( savedChoose.get() )
	whitePromoter.lower()
	whitePromote.set( whitePromote.get() )
	blackPromoter.lower()
	blackPromote.set( blackPromote.get() )
	piecePlacer.lower()
	piecePlace.set( piecePlace.get() )
	saveAsChooser.lower()
	saveAsChoose.set( saveAsChoose.get() )

# -------------------

def destroyProgram():
	'''kill the main window'''
	rootWin.destroy()

def docloseProgram():
	'''close the program requested'''
	# ask if closing should really happen
	if messagebox.askokcancel("Quit", "Quit Chess Coach?"):

		# stop any active "wait loops"
		stopChoosers()

		# wait for event queues to empty and destroy the program
		rootWin.update_idletasks()
		rootWin.after_idle( destroyProgram )

def doQuit(button):
	'''quit button pressed'''
	# maybe we could do something like docloseProgram(button=None) instead
	# and handle both the labeled button and the window's "x" in one function
	docloseProgram()

# -------------------

def clearMoves():
	'''clear all move records'''
	FEN.clearRecord()
	ODB.clearRecord()

def doReset():
	'''set program to start state'''
	global currBoard, currMoves, whiteMoves, blackMoves
	global gameRunning, placePieces, promotePawn, chooseSaveAs, placedFen
	# clear any saved moves
	clearMoves()
	# display options
	algebraicMoves.set( False )
	showSqName.set( True )
	showWhitePreview.set( True )
	showBlackPreview.set( True )
	showWhiteReach.set( True )
	showBlackReach.set( True )
	showWhiteMoveCnt.set( True )
	showBlackMoveCnt.set( True )
	showWhiteTactic.set( True )
	showBlackTactic.set( True )
	showWhitePosName.set( True )
	showBlackPosName.set( True )
	# clear board
	currBoard = FEN.putFen( FEN.placeStart() )
	currMoves, whiteMoves, blackMoves = CM.potentialMoves( currBoard )
	showChessboard()
	# flags
	gameRunning = placePieces = promotePawn = chooseSaveAs = False
	placedFen = None
	# status messages
	clearStatus( [lastMoveStatus, toMoveStatus, movesAvailable, materialBalance] )
	moveComment.set( CM_WAITING )
	# buttons to start state
	# - Restart and Quit are always enabled; we don't worry about them after this
	disableButtons( [butTakeBack, butNextMove, butStartMoves, butStopPlacing, butSaveMoves] )
	enableButtons( [butNewGame, butPlacePieces, butLoadMoves, butRestart, butQuit] )
	# disable all choosers
	stopChoosers()
	# fen moves databases
	SQL.dbCreate()

def doRestart(button):
	'''restore initial setup'''
	# ask if reset should really happen
	if messagebox.askokcancel("Restart", "Restart Chess Coach?"):
		doReset()

# -------------------

def doStopPlacing(button):
	'''stop placing pieces'''
	global placePieces, placedFen

	if isDisabled(button):
		return

	# is the current board a legaal placement ?
	# - if not, just stay in "place pieces" mode
	if not CM.isLegal(currBoard):
		moveComment.set( CM_ILLEGAL )

	# placement is legal, so continue
	else:
		moveComment.set( CM_WAITING )

		# set control buttons
		disableButtons( [butNewGame, butStopPlacing, butLoadMoves] )
		enableButtons( [butStartMoves, butPlacePieces, butSaveMoves] )

		# stop placer loop from running
		# - the problem is that the wait_variable() loop
		# in 'doPlacePieces()' is still running
		# - so the idea is to fake a variable change,
		# - which will break that waiting loop,
		# - which won't restart now that 'placePieces' is False
		piecePlacer.lower()
		placePieces = False
		piecePlace.set( piecePlace.get() )

		# change status display
		clearStatus( [lastMoveStatus] )

		# erase all board markings
		showChessboard()

		# save placed arrangement
		placedFen = FEN.getFen( currBoard )

def doPlacePieces(button):
	global placePieces
	'''start placing pieces'''

	if isDisabled(button):
		return

	# set control buttons
	disableButtons( [butNewGame, butStartMoves, butPlacePieces, butLoadMoves, butSaveMoves] )
	enableButtons( [butStopPlacing] )

	# show piece chooser (by default set to stop placing)
	piecePlacer.lift()
	piecePlace.set( CK.SQ_STOP )

	# by default set to white move
	FEN.setWhoseMove( CK.PC_WHITE )

	# update status labels
	lastMoveStatus.set( BT_PLACEPIECE )
	clearComment()
	toMoveStatus.set( FEN.getWhoseMove() )

	# this will be forced to stop looping when placing stops
	placePieces = True
	while placePieces:
		piecePlacer.wait_variable( piecePlace )

# -------------------

def startMoves(tag, firstfen, allfens):
	'''start player moves'''
	global gameRunning, recordID, placedFen
	global fenPositions

	# just in case this is still raised...
	savedChooser.lower()
	# all recorded positions (if any)
	fenPositions = allfens
	# there is no saved or placed position now (if any)
	recordID = placedFen = None
	# no moves recorded from player moves yet
	clearMoves()
	clearComment()
	gameRunning = True

	# start moving
	dummyMove( tag, firstfen )

def doNewGame(button):
	'''start a new game'''
	if isEnabled(button):
		fenPositions = None
		disableButtons( [butNewGame, butStartMoves, butPlacePieces, butStopPlacing, butLoadMoves] )
		enableButtons( [butSaveMoves] )

		startMoves( BT_NEWGAME, FEN.gameStart(), None )

def doStartMoves(button):
	'''start moving from given position'''
	if isEnabled(button):
		# are we starting from an arranged position ?
		if recordID is None:
			startfen = placedFen
			fenrecord = None
			disableButtons( [butNewGame, butStartMoves, butPlacePieces, butStopPlacing, butLoadMoves, butNextMove] )
			enableButtons( [butSaveMoves] )
		# starting from a recorded position
		else:
			fenrecord = SQL.loadRecord( recordID )
			startfen = fenrecord[ 0 ]
			disableButtons( [butNewGame, butStartMoves, butPlacePieces, butStopPlacing, butLoadMoves, butSaveMoves] )
			enableButtons( [butNextMove] )

		startMoves( BT_STARTMOVE, startfen, fenrecord  )

# -------------------

def doTakeBack(button):
	'''take back last move'''
	global gameRunning
	if isEnabled(button):
		ODB.takeBack()
		gameRunning = True
		dummyMove( BT_TAKEBACK, FEN.takeBack() )

def doNextMove(button):
	'''make next move'''
	global currBoard
	# this is not enabled unless we started from a saved record
	if isEnabled(button):
		currBoard, pieces, squares = CM.getNextMove( currBoard, fenPositions )
		updateMove( pieces, squares )

def redoStatus():
	'''redisplay status panel'''
	# presumably some option changed
	# - the idea is to get the last move and immediately do it again
	# - not very efficient, but we're not too worried
	if gameRunning:
		dummyMove( "Toggled Status", FEN.mostRecent() )

# -------------------

def reviewRecord(recordtype, fens):
	'''review moves in record'''
	# display moves one by one
	for i, fen in enumerate(fens):
		dummyMove( None, fen  )
		looksgood = messagebox.askyesno( MB_REVIEW, f"Move {i+1} of {len(fens)}", detail="Looks Good ?" )
		if not looksgood:
			break

	return looksgood

def getRecordType():
	'''get type of record to save'''
	global chooseSaveAs

	saveAsChoose.set( "" )
	chooseSaveAs = True
	saveAsChooser.lift()
	saveAsChooser.wait_variable( saveAsChoose )
	saveAsChooser.lower()
	chooseSaveAs = False

	return saveAsChoose.get()

def doSaveMoves(button):
	'''record chess moves'''
	if isDisabled(button):
		return

	rtype = getRecordType()
	if rtype == "X00":
		messagebox.showinfo( BT_SAVEMOVES, message="Save Cancelled" )
	else:
		result = True
		fens = FEN.getRecord()
		if len(fens) < 2:
			messagebox.showinfo( MB_REVIEW, message="There are no moves to save" )
			result = False

		if result:
			# only last move matters if snapshot
			if rtype.startswith("A"):
				fens = [ fens[-1] ]
			result = reviewRecord( rtype, fens )

		if result:
			result = SQL.dbRecord( rtype, fens )

		if result:
			messagebox.showinfo( BT_SAVEMOVES, message="Save Successful" )
		else:
			messagebox.showerror( BT_SAVEMOVES, message="Save Failed" )

		doReset()

# -------------------

def showFirstFen(listbox):
	'''show first position of saved record (single click)'''
	global recordID, placedFen

	clearMoves()
	ndx = listbox.curselection()
	if len(ndx) == 1:
		ndx = int( ndx[0] )
		listbox.see( ndx )
		recordID, placedFen = chosenRecord[ ndx ]
		dummyMove( chooseRecord[ndx], placedFen )

def startFirstFen(listbox):
	'''start game/puzzle (double click)'''
	showFirstFen( listbox )
	doStartMoves( butStartMoves )

def doLoadMoves(button):
	'''load and display saved records'''
	global chooseRecord, chosenRecord
	# load button disabled ?
	if isDisabled(button):
		return

	# set control buttons
	disableButtons( [butNewGame, butPlacePieces, butStopPlacing, butLoadMoves, butSaveMoves] )
	enableButtons( [butStartMoves] )

	ok, chooseRecord, chosenRecord = SQL.getAllRecords()
	if ok and len(chooseRecord) > 0:
		savedChoose.set( chooseRecord )
		savedChooser.lift()
	else:
		disableButtons( [butStartMoves] )
		enableButtons( [butNewGame, butPlacePieces] )
		messagebox.showinfo( BT_LOADMOVES, message="No records to show" )

# -------------------
# Main
# -------------------

def guiMain(title, args):
	global rootWin, lftFrame, rgtFrame
	# make a main window
	rootWin = tk.Tk()
	rootWin.title( title )
	rootWin.resizable( False, False )

	# intercept closing this window
	rootWin.protocol( "WM_DELETE_WINDOW", docloseProgram )

	# make widgets !

	# make a left frame within the main window
	lftFrame = tk.Frame( rootWin )
	lftFrame.grid( row=0, column=0 )

	# make a frame for chessboard
	frame = tk.Frame( lftFrame )
	frame.grid( row=0, column=0 )

	# put chessboard within this frame
	makeBoard( frame )

	# make (hidden) white pawn promotion radiobox within this frame
	makePromoter( frame, "QRBN", 1, 2, "whitePromote", "whitePromoter" )

	# make (hidden) black pawn promotion radiobox within this frame
	makePromoter( frame, "qrbn", 6, 2, "blackPromote", "blackPromoter" )

	# put a right frame within the main window
	rgtFrame = tk.Frame( rootWin )
	rgtFrame.grid( row=0, column=1 )

	# make (hidden) saved puzzle/game chooser within this frame
	makeChooseSaved( rgtFrame, 1, 0, "savedChoose", "savedChooser" )

	# make (hidden) puzzle/game "record as" chooser within this frame
	makeChooseSaveAs( rgtFrame, 1, 0, "saveAsChoose", "saveAsChooser" )

	# put 'last move' label within this frame
	makeStatusLabel( rgtFrame, "Last Action", 0, 0, "lastMoveStatus" )

	# put 'comment' label within this frame
	makeStatusLabel( rgtFrame, "Comment", 1, 0, "moveComment" )

	# put 'to move' label within this frame
	makeStatusLabel( rgtFrame, "To Move", 2, 0, "toMoveStatus" )

	# put 'moves available' label within this frame
	makeStatusLabel( rgtFrame, "Moves Available", 3, 0, "movesAvailable" )

	# put a 'material balance' label within this frame
	makeStatusLabel( rgtFrame, "Material Balance", 4, 0, "materialBalance" )

	# put 'controls' frame within this frame
	frame = makeGroupFrame( rgtFrame, "Controls", 5, 0 )

	makeControlButton( frame, BT_TAKEBACK, 0, 0, "butTakeBack", doTakeBack )
	makeControlButton( frame, BT_NEXTMOVE, 0, 1, "butNextMove", doNextMove )
	makeControlButton( frame, BT_NEWGAME, 1, 0, "butNewGame",  doNewGame )
	makeControlButton( frame, BT_STARTMOVE, 1, 1, "butStartMoves", doStartMoves )
	makeControlButton( frame, BT_PLACEPIECE, 2, 0, "butPlacePieces", doPlacePieces )
	makeControlButton( frame, BT_STOPPLACE, 2, 1, "butStopPlacing", doStopPlacing )
	makeControlButton( frame, BT_LOADMOVES, 3, 0, "butLoadMoves", doLoadMoves )
	makeControlButton( frame, BT_SAVEMOVES, 3, 1, "butSaveMoves", doSaveMoves )
	makeControlButton( frame, BT_RESTART, 4, 0, "butRestart", doRestart )
	makeControlButton( frame, BT_QUIT, 4, 1, "butQuit", doQuit )

	# put 'options' frame within this frame
	frame = makeGroupFrame( rgtFrame, "Options", 6, 0 )

	# algebraic move descriptions ?
	makeBoardOpt( frame, "algebraicMoves", "Standard Notation", 0, 0 )

	# show square name ?
	makeBoardOpt( frame, "showSqName", "Square Names", 0, 1 )

	# put white and black options within this frame
	wframe = makeGroupFrame( frame, "White", 1, 0 )
	bframe = makeGroupFrame( frame, "Black", 1, 1 )

	# show possible moves ?
	makeStatusOpt( wframe, "showWhitePreview", bframe, "showBlackPreview", "Preview Moves", 0, 0 )

	# show can reach counts ?
	makeStatusOpt( wframe, "showWhiteReach", bframe, "showBlackReach", "# Can Reach Square", 1, 0 )

	# show available move count ?
	makeStatusOpt( wframe, "showWhiteMoveCnt", bframe, "showBlackMoveCnt", "# Moves Available", 2, 0 )

	# show position names ?
	makeStatusOpt( wframe, "showWhitePosName", bframe, "showBlackPosName", "Position Names", 3, 0 )

	# show tactic executed ?
	makeStatusOpt( wframe, "showWhiteTactic", bframe, "showBlackTactic", "Tactic Executed", 4, 0 )

	# make (hidden) piece placer radiobox within this frame
	makePlacer( frame, 0, 0, "piecePlace", "piecePlacer" )

	# set default board and options
	doReset()

	# size and set main window
	setGeometry( rootWin )

	# start the event loop
	rootWin.mainloop()
