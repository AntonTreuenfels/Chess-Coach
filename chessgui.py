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
# last revision: 03/31/25

#--------------------
# Python modules
import tkinter as tk
from sys import exit, version_info
# program modules
import chessmoves as CM
import fen as FEN
import chessconstants as CK
import movedatabase as MDB
#--------------------

# global constants

CLR_LITESQ = "bisque"		# light square
CLR_DARKSQ = "bisque3"		# dark square

CLR_PROTECT = "pale green"	# protected square
CLR_ATTACK = "#F33A6A"		# attacked square (rose)

CLR_HOVER = "lightblue"		# hovered square

CLR_CHOOSER = "bisque2"		# piece chooser

CLR_BOARD = "saddle brown"	# chess board frame color
FRM_WIDTH = 8				# chess board frame pixel width

CRS_HIT  = "hand2"
CRS_DROP = "target"
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
CM_STARTSTATUS = "Waiting..."	# default status message before game start

# piece glyphs (Unicode)

OCC2GLYPH = {
	"K": "\u2654",		# white king
	"Q": "\u2655",		# white queen
	"R": "\u2656",		# white rook
	"B": "\u2657",		# white bishop
	"N": "\u2658",		# white knight
	"P": "\u2659",		# white pawn

	"k": "\u265A",		# black king
	"q": "\u265B",		# black queen
	"r": "\u265C",		# block rook
	"b": "\u265D",		# black bishop
	"n": "\u265E",		# black knight
	"p": "\u265F",		# black pawn

	".": "",			# empty
	}

# large arrow glyphs (Unicode)

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

# global variables

currBoard = None		# current location of all pieces on board
currMoves = None		# possible moves in current position

whiteMoves = None		# number of white pieces that can reach each square
blackMoves = None		# number of black pieces that can reach each square

fromButton = None		# square piece is moving from

gameRunning = False		# game is running
placePieces = False		# manual setup in progress

placedFen = None		# fen of a manual setup

chessBoard = dict()		# display frame associated with each chessboard square

# -------------------

def getSquare(file, rank):
	sqname = CM.fr2sq( file, rank )
	frame = chessBoard[ sqname ]
	button = frame.winfo_children()[0]
	return ( sqname, frame, button )

def getGlyph(piece):
	return OCC2GLYPH[ piece]

def setColor(frame, color):
	button = frame.winfo_children()[0]
	frame.config( bg=color )
	button.config( bg=color )

# -------------------

def showChessboard():
	'''draw the current board position'''
	# this erases anything that is not a piece glyph
	# - we'll just hoist this up here to save a little time and code space
	whtshowcnt = gameRunning and showWhiteReach.get()
	blkshowcnt = gameRunning and showBlackReach.get()
	for file in range(1, 9):
		for rank in range(1, 9):
			sqname, frame, button = getSquare( file, rank )
			# show name ?
			namtxt = sqname if showSqName.get() else "  "
			# show how many pieces can reach this square ?
			count = CM.getCount(whiteMoves, file, rank) if whtshowcnt else 0
			whttxt = f"{count:2}" if count > 0 else "  "
			count = CM.getCount(blackMoves, file, rank) if blkshowcnt else 0
			blktxt = f"{count:2}" if count > 0 else "  "
			title = f"{whttxt}   {namtxt}  {blktxt} " 
			frame.config( text=title, bg=frame.dfltcolor )
			# show the glyph for this square
			glyph = getGlyph( CM.occupiedBy(currBoard, file, rank) )
			button.config( text=glyph, bg=frame.dfltcolor, cursor=CRS_DFLT )

def doPlace(frame, piece):
	'''put a piece on the chessboard'''
	global currBoard

	file, rank = CM.sq2fr( frame.name )
	currBoard[ rank ][ file ] = piece
	showChessboard()

# -------------------

def occupiedBy(board, piece, file, rank):
	'''get piece on destination square'''
	# should we fake a pawn on enpassant square ?
	if CM.fr2sq(file, rank) == FEN.getenPassant():
		match piece:
			case "P":
				return "p"
			case "p":
				return "P"
			case _:
				pass

	return CM.occupiedBy( board, file, rank )

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
	# if no piece here, than can't be start of any move
	occupant = CM.occupiedBy( currBoard, sqfile, sqrank )
	if occupant == CK.SQ_EMPTY:
		return False

	# what color is occupant ?
	occ_color = CM.colorOf( occupant )

	# can we show the moves available to the color whose turn it is ?
	move_color = FEN.getWhoseMove()
	showmoves = optEnabled( move_color, showWhitePossible, showBlackPossible )

	# can this piece be moved ?
	moveable = (occ_color == move_color)
	# can we drop this piece anywhere ?
	curicon = CRS_DROP if moveable else CRS_DFLT

	# change the cursor over this square
	button.config( cursor=CRS_HIT )

	# where can this piece move to ?
	possible = currMoves[ frame.name ]

	# go through each possible move and mark buttons
	for move, file, rank in possible:
		dstsquare, dstframe, dstbutton = getSquare( file, rank )
		dstoccupant = occupiedBy( currBoard, occupant, file, rank )
		# can we show possible moves by changing square glyphs ?
		if showmoves:
			# if square is empty, mark it with an arrow
			if dstoccupant == CK.SQ_EMPTY:
				dstbutton.config( text=ARROWGLYPH[move], cursor=curicon )
			# if square has a friendly piece, mark it protected
			elif CM.colorOf(dstoccupant) == occ_color:
				dstframe.config( bg=CLR_PROTECT )
				dstbutton.config( bg=CLR_PROTECT )
			# square has an enemy piece, mark it attacked
			else:
				txtval = f"{getGlyph(occupant)}x{getGlyph(dstoccupant)}"
				dstframe.config( bg=CLR_ATTACK )
				dstbutton.config( text=txtval, bg=CLR_ATTACK, cursor=curicon )
		# no, but we still use the cursor to indicate legal moves
		elif moveable:
			if dstoccupant == CK.SQ_EMPTY or CM.colorOf(dstoccupant) != occ_color:
				dstbutton.config( cursor=CRS_DROP )

	return moveable

def getMoveDesc(srcpiece, captured, srcname, dstname, couldhavemoved):
	'''get move description'''
	srcfile, srcrank = CM.sq2fr( srcname )
	dstfile, dstrank = CM.sq2fr( dstname )

	# disambiguate (if necessary)'
	# - tricky: 'srcpiece' is already on 'dstname', not 'srcname'
	disambig = ""
	alsoreach = list()
	for square, moves in couldhavemoved.items():
		for move, file, rank in moves:
			if file != dstfile or rank != dstrank:
				continue
			sqfile, sqrank = CM.sq2fr( square )
			if srcpiece == CM.occupiedBy(currBoard, sqfile, sqrank):
				alsoreach.append( square )

	# algebraic ?
	if algebraicMoves.get():
		match len(alsoreach):
			case 0:
				pass
			case 1:
				file, rank = CM.sq2fr( alsoreach.pop() )
				disambig = f"{srcname[0]}" if file != srcfile else f"{srcname[1]}"
			case _:
				disambig = f"{srcname}"
			
		match srcpiece:
			# king castled ?
			case "K" | "k" if dstfile - srcfile == 2:
				return f"O-O"
			case "K" | "k" if srcfile - dstfile == 2:
				return r"O-O-O"
			# pawn captured ?
			case "P" | "p" if captured != CK.SQ_EMPTY:
				prefix = f"{srcname[0]}x"
				# en passant capture?
				if captured == "px":
					return f"{prefix}{CM.fr2sq(dstfile, dstrank-1)}"
				elif captured == "Px":
					return f"{prefix}{CM.fr2sq(dstfile, dstrank+1)}"
				# pawn promoted as well ?
				elif "?" in captured:
					return f"{prefix}{dstname}={captured[2].upper()}"
				# ordinary capture
				else:
					return f"{prefix}{dstname}"
			# pawn promoted ?
			case "P" | "p" if "?" in captured:
				return f"{dstname}={captured[2].upper()}"
			case "P" | "p":
				return f"{dstname}"
			case _:
				pass

		if captured == CK.SQ_EMPTY:
			return f"{srcpiece.upper()}{disambig}{dstname}"
		else:
			return f"{srcpiece.upper()}{disambig}x{dstname}"

	# English-like
	else:
		if len(alsoreach) > 0:
			disambig = f" on {srcname}"

		match srcpiece:
			# king castled ?
			case "K" | "k" if dstfile - srcfile == 2:
				return f"{getGlyph(srcpiece)} Castled Kingside"
			case "K" | "k" if srcfile - dstfile == 2:
				return f"{getGlyph(srcpiece)} Castled Queenside"
			# en passant capture?
			case "P" if captured == "px":
				return f"{getGlyph('P')}{disambig} en passant {getGlyph('p')} on {dstname}"
			case "p" if captured == "Px":
				return f"{getGlyph('p')}{disambig} en passant {getGlyph('P')} on {dstname}"
			# pawn promoted ?
			case "P" | "p" if "?" in captured:
				return f"{getGlyph(srcpiece)}{disambig} promoted to {getGlyph(captured[-1])} on {dstname}"
			case _:
				pass

		if captured == CK.SQ_EMPTY:
			return f"{getGlyph(srcpiece)}{disambig} moved to {dstname}" 
		else:
			return f"{getGlyph(srcpiece)}{disambig} captured {getGlyph(captured)} on {dstname}" 

def checkTactic(tactic, srcpiece, dstname, lastmoved):
	'''test if last move resulted in a tactic executed'''

	def moretext(this, add):
		return add if this is None else f"{this} + {add}"

	# did last move lead to a recognized position ? 
	text = MDB.openingComment( srcpiece, dstname )
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

	def gameover():
		global gameRunning

		gameRunning = False
		toMoveStatus.set( "" )
		movesAvailable.set( "" )

	drawbyreps = FEN.lastRepeated()
	drawbymoves = FEN.gethalfMove()
	if movecnt == 0 and incheck:
		text = f"Checkmate: {FEN.getOppMove()} Wins"
		gameover()
	elif movecnt == 0:
		text = f"Draw: Stalemate - {FEN.getWhoseMove()} Has No Move"
		gameover()
	elif drawbyreps > 2:
		text = f"Draw: {FEN.getOppMove()} Position Repeated Three Times"
		gameover()
	elif drawbymoves >= 100:
		text = "Draw: 50 Moves"
		gameover()
	elif CM.getInsufficient(currBoard):
		text = "Draw: Insufficient Material To Checkmate"
		gameover()
	elif drawbyreps > 1:
		text = f"{FEN.getOppMove()} Position Repeated"
	elif drawbymoves >= 90 and drawbymoves % 2 == 0:
		text = f"Draw in {(100-drawbymoves)/2} Moves"
	elif movecnt == 1:
		text = f"{FEN.getWhoseMove()} Move Forced"

	return text

def updateMove(pieces, squares, status=None):
	'''update display and FEN'''
	global currMoves, whiteMoves, blackMoves

	srcpiece, captured = pieces
	srcname, dstname = squares

	if status is None:
		# preliminary description of last move
		movedesc = getMoveDesc( srcpiece, captured, srcname, dstname, currMoves )

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
	takeBackButton.config( state=tk.NORMAL if FEN.cantakeBack() else tk.DISABLED )

	# find available moves
	currMoves, whiteMoves, blackMoves = CM.potentialMoves( currBoard )
	showChessboard()

	# update comment
	if gameRunning:
		tactic = CM.tactic( currBoard, srcpiece, dstname, currMoves, whiteMoves, blackMoves )
		text = checkTactic( tactic, srcpiece, dstname, FEN.getOppMove() )
		# update values we will need several times
		incheck = bool( (tactic & CK.OC_CHECK) or (tactic & CK.OC_DOUBLE) )
		movecnt = CM.getMoveCount( currBoard, whosemove, currMoves )
		# do we need to change comment because game is over (or nearly so) ?
		text = checkGameOver( text, incheck, movecnt )
		moveComment.set( text ) 

	# last move was not a "dummy" move ?
	if status is None:
		if algebraicMoves.get():
			movedesc = f"{movedesc}{'#' if incheck and movecnt < 1 else '+' if incheck else ''}"
		lastMoveStatus.set( movedesc )
	else:
		lastMoveStatus.set( status )

	# update move count
	showavailable = optEnabled(whosemove, showWhiteMoveCnt, showBlackMoveCnt )
	text = "" if not showavailable else str(movecnt) if gameRunning else "0"
	movesAvailable.set( text )

	# update material balance
	balance = CM.getBalance( currBoard )
	if balance > 0:
		materialBalance.set( f"{CK.PC_WHITE} +{balance}" )
	elif balance < 0:
		materialBalance.set( f"{CK.PC_BLACK} +{abs(balance)}" )
	else:
		materialBalance.set( "Even" )

def dummyMove(status, fen):
	'''dummy (non-player) move'''
	global currBoard
	currBoard = FEN.putFen( fen )
	updateMove( (CK.SQ_EMPTY, CK.SQ_EMPTY), ("a1", "h8"), status )

def doMove(dstbutton, srcbutton):
	'''move a piece to destination square'''
	global currBoard

	def promote(frame, file, promoter, varname, captured):
		'''promote a pawn'''
		varname.set( "" )
		promoter.grid( column=min(file, 6) )
		promoter.lift()
		promoter.wait_variable( varname )
		promoter.lower()
		newpiece = varname.get()
		doPlace( frame, newpiece )

		return f"{captured}{newpiece}"

	srcframe = srcbutton.master
	srcfile, srcrank = CM.sq2fr( srcframe.name )
	srcpiece = CM.occupiedBy( currBoard, srcfile, srcrank )
	dstframe = dstbutton.master
	dstfile, dstrank = CM.sq2fr( dstframe.name )
	# make the move on the board
	currBoard, captured = CM.makeMove( currBoard, dstfile, dstrank, srcfile, srcrank )
	if captured == "P?":
		captured = promote( dstframe, dstfile, whitePromoter, whitePromote, captured )
	elif captured == "p?":
		captured = promote( dstframe, dstfile, blackPromoter, blackPromote, captured )

	setColor( dstframe, dstframe.dfltcolor )
	return ( srcpiece, captured), ( srcframe.name, dstframe.name )

# -------------------

def hitSquare(button):
	''''button press'''
	global fromButton

	frame = button.master

	# is a game active now ?
	if gameRunning:
		frame.color = frame.dfltcolor
		# we can't use match..case because of "name capture"
		cursor = button.cget( "cursor" )
		# can we move a piece here ?
		if cursor == CRS_DROP:
			pieces, squares = doMove( button, fromButton )
			updateMove( pieces, squares )
			fromButton = None
		# hit the square to move from a second time ?
		elif cursor == CRS_HIT:
			showChessboard()
			fromButton = None
		# not a square involved in any moving
		else:
			showChessboard()
			canmove = showMoves( frame, button )
			fromButton = button if canmove else None

	# are we placing pieces ? 
	elif placePieces:
		doPlace( frame, piecePlace.get() )

# -------------------

def makePlacer(parent, gcol, grow, strvar):
	'''make a piece placement chooser'''
	# make a label frame for the radiobutton
	frame = tk.LabelFrame( parent,
		text = "Choose Piece",
		font=(FNT_TEXT),
		)
	frame.grid( column=gcol, row=grow, columnspan=2, rowspan=3 )
	# make it hidden "below" sibling at start
	frame.lower()

	# make the piece select radio button itself
	for frow, pieces in enumerate(["KQRBNP", "kqrbnp", CK.SQ_EMPTY]):
		for fcol, piece in enumerate(pieces):
			tk.Radiobutton( frame,
				text=getGlyph(piece),
				value = piece,
				variable=strvar,
				fg="black",
				bg=CLR_CHOOSER,
				indicatoron=False,
				font=( FNT_TEXT, ICO_POINTS ),
				height=1,
				width=2,
			).grid( column=fcol, row=frow, sticky="ew" )

	# make 'to move' toggle button
	button = tk.Button( frame,
		text="Toggle To Move",
		anchor=tk.CENTER,
		fg="black",
		bg=CLR_CHOOSER,
		font=( FNT_TEXT, FNT_POINTS ),
		height=1,
		width=4,
		command=lambda: toMoveStatus.set( FEN.toggleWhoseMove() )
	).grid( column=2, row=2, columnspan=4, sticky="nesw" )

	return frame

# -------------------

def makePromoter(parent, pieces, gcol, grow, strvar):
	'''make a radio button for pawn promotion'''
	# make a label frame for the radiobutton
	frame = tk.LabelFrame( parent,
		text="Promote To",
		font=(FNT_TEXT),
		)
	frame.grid( column=gcol, row=grow, columnspan=3 )
	# make it hidden "below" sibling at start
	frame.lower()

	# make the radio button itself
	for fcol, piece in enumerate(pieces):
		tk.Radiobutton( frame,
			text=getGlyph(piece),
			value = piece,
			variable=strvar,
			fg="black",
			bg=CLR_CHOOSER,
			indicatoron=False,
			font=( FNT_TEXT, ICO_POINTS ),
			height=1,
			width=2,
		).grid( column=fcol, row=0, sticky="ew" )

	return frame

# -------------------

def enterSquare(frame):
	'''hover over the frame and its button'''
	frame.color = frame.cget( "bg" )
	setColor( frame, CLR_HOVER )

def leaveSquare(frame):
	'''restore original square color'''
	setColor( frame, frame.color )

def makeSquare(parent, file, rank, colorndx):
	'''make one chessbaord square'''
	# the name and color of this square
	sqname = CM.fr2sq( file, rank )
	sqcolor = [ CLR_DARKSQ, CLR_LITESQ ][ colorndx ]

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
	frame.grid( column=file, row=9-rank )
	# save these because we might need them later
	frame.dfltcolor = sqcolor
	frame.color = sqcolor
	frame.name = sqname
	# we can bind these events to this frame
	frame.bind("<Enter>", lambda event: enterSquare(event.widget))
	frame.bind("<Leave>",  lambda event: leaveSquare(event.widget))
	# add frame to dictionary
	chessBoard[ sqname ] = frame

	# a button inside each frame
	button = tk.Button( frame,
		text="",			# default text
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

def makeBoard(parent):
	'''make the chessboard'''
	parent.config( bg=CLR_BOARD, bd=FRM_WIDTH )
	for file in range(1,9):			# 1..8, left to right
		colortoggle = file % 2	 	# columns 1,3,5,7 start light, 2,4,6,8 start dark
		for rank in range(8,0,-1):	# 8..1, top to bottom
			makeSquare( parent, file, rank, colortoggle )
			colortoggle = 1 - colortoggle

def makeGroupFrame(parent, textval, grow, gcol):
	'''make a frame for grouping'''
	frame = tk.LabelFrame( parent,
			text=f" {textval} ",
			height=1 * FNT_PIXELS,
			width=CONTROLSWIDTH * FNT_PIXELS,
			pady=10,
		)
	frame.grid( row=grow, column=gcol,  sticky="news" )
	frame.grid_rowconfigure( 0, weight=1 )
	frame.grid_columnconfigure( 0, weight=1 )
	frame.propagate( 0 )

	return frame

def makeControlButton(parent, textval, grow, gcol):
	'''make a control button'''
	button = tk.Button( frame,
			text=textval,
			height=1,
			width=CONTROLSWIDTH,
			font=(FNT_TEXT, FNT_POINTS),
		)
	button.grid( row=grow, column=gcol, sticky="ew" )

	return button

def makeStatusLabel(parent, textval, grow, gcol, variable):
	''' make status label'''
	# make a frame for label
	frame = makeGroupFrame( parent, textval, grow, gcol )
	# make a label in this frame
	label = tk.Label( frame,
		textvariable=variable,
		font=(FNT_TEXT, FNT_POINTS),
		height=1,
		width=CONTROLSWIDTH,
		)
	label.grid( sticky="ew" )

	return label

def makeBooleanOpt(parent, textval, grow, gcol, textvar, docommand):
	'''make on/off checkbox'''
	cbutton = tk.Checkbutton( parent,
		text=textval,
		variable=textvar,
		height=1,
		width=CONTROLSWIDTH,
		font=(FNT_TEXT, FNT_POINTS),
		anchor=tk.W,
		command=docommand,
	)
	cbutton.grid( row=grow, column=gcol, sticky="nesw" )

	return cbutton

def makeBoardOpt(parent, textvar, textval, grow, gcol):
	'''make chessboard display checkbox'''
	cbutton = makeBooleanOpt( parent, textval, grow, gcol, textvar, showChessboard )

def makeStatusOpt(wparent, wvar, bparent, bvar, textval, grow, gcol):
	'''make status display checkbox'''
	cbutton = makeBooleanOpt( wparent, textval, grow, gcol, wvar, redoStatus )
	cbutton = makeBooleanOpt( bparent, textval, grow, gcol, bvar, redoStatus )

# -------------------

def stopPlacing(button):
	'''stop placing pieces'''
	global placePieces, placedFen
	# placer button disabled ?
	if button.cget("state") == tk.DISABLED:
		return

	# reconfigure placer button
	placePieces = False
	placePiecesButton.config( text="Place Pieces" )
	placePiecesButton.bind( "<Button>", lambda event: startPlacing(event.widget) )
	piecePlacer.lower()
	piecePlace.set( CK.SQ_EMPTY )

	# stop placer loop from running
	# - the problem is that the wait_variable() loop
	# in 'startPlacing()' is still running
	# - so the idea is to fake a variable change,
	# which will break that waiting loop,
	# which won't restart now that 'placePieces' is False
	piecePlace.set( piecePlace.get() )

	# change status display
	lastMoveStatus.set( "" )

	# legal placement ?
	if CM.isLegal(currBoard):
		moveComment.set( CM_STARTSTATUS )
	else:
		moveComment.set( "Illegal Placement" )
		return

	# enable game start
	startButton.config( state=tk.NORMAL )

	# save placed arrangement
	placedFen = FEN.getFen( currBoard )

def startPlacing(button):
	global placePieces
	'''start placing pieces'''
	# placer button disabled ?
	if button.cget("state") == tk.DISABLED:
		return
	# disable game start
	startButton.config( state=tk.DISABLED )

	# reconfigure placer button
	placePieces = True
	placePiecesButton.config( text="Stop Placing" )
	placePiecesButton.bind( "<Button>", lambda event: stopPlacing(event.widget) )
	piecePlacer.lift()
	piecePlace.set( CK.SQ_EMPTY )

	status = "Place Pieces"
	# first call ?
	if currBoard is None:
		dummyMove( status, FEN.placeStart() )
	# restart
	else:
		lastMoveStatus.set( status )
	moveComment.set( "" )

	# this will be forced to stop looping when placing stops
	while placePieces:
		piecePlacer.wait_variable( piecePlace )

def startGame(button):
	'''set board to game start position'''
	global gameRunning, placePieces, placedFen
	# start button disabled ?
	if button.cget("state") == tk.DISABLED:
		return

	fen = FEN.gameStart() if placedFen is None else placedFen
	placedFen = None
	placePieces = False
	placePiecesButton.config( state=tk.DISABLED )
	FEN.clearRecord()
	MDB.clearRecord()
	gameRunning = True
	moveComment.set( "" )
	dummyMove( "Game Start", fen  )

def takeMoveBack(button):
	'''take back last move'''
	global gameRunning
	
	if button.cget("state") == tk.NORMAL:
		gameRunning = True
		MDB.takeBack()
		dummyMove( "Take Back", FEN.takeBack() )

def redoStatus():
	'''redisplay status panel'''
	# presumably some option changed
	# - not very efficient, but we're not too worried
	if gameRunning:
		dummyMove( "Toggled Status", FEN.mostRecent() )

def centerOnScreen(this):
	'''center display on screen''' 
	this.update_idletasks()
	width = this.winfo_width()
	height = this.winfo_height()
	screen_width = this.winfo_screenwidth()
	screen_height = this.winfo_screenheight()
	x = (screen_width - width) // 2
	y = (screen_height - height) // 2
	this.geometry(f"{width}x{height}+{x}+{y}")

# -------------------
# Main
# -------------------
# minimum Python version needed
if version_info.major < 3 or version_info.minor < 10:
	exit( "Python 3.10 or higher required" )

# make a main window
root = tk.Tk()
root.title( "Virtual Chess Coach 0.9" )
root.resizable( False, False )

# make widgets !

# make a left frame within the main window
rframe = tk.Frame( root )
rframe.grid( row=0, column=0 )

# make a frame for chessboard
frame = tk.Frame( rframe )
frame.grid( row=0, column=0 )

# put chessboard within this frame
makeBoard( frame )

# make (hidden) white pawn promotion radiobox within this frame
whitePromote = tk.StringVar( frame, "" )
whitePromoter = makePromoter( frame, "QRBN", 2, 2, whitePromote )

# make (hidden) black pawn promotion radiobox within this frame
blackPromote = tk.StringVar( frame, "" )
blackPromoter = makePromoter( frame, "qrbn", 2, 7, blackPromote )

# put a right frame within the main window
rframe = tk.Frame( root )
rframe.grid( row=0, column=1 )

# put 'last move' label within this frame
lastMoveStatus = tk.StringVar( rframe, "" )
label = makeStatusLabel( rframe, "Last Action", 0, 0, lastMoveStatus )

# put 'comment' label within this frame
moveComment = tk.StringVar( rframe, CM_STARTSTATUS )
label = makeStatusLabel( rframe, "Comment", 1, 0, moveComment )

# put 'to move' label within this frame
toMoveStatus = tk.StringVar( rframe, "" )
label = makeStatusLabel( rframe, "To Move", 2, 0, toMoveStatus )

# put 'moves available' label within this frame
movesAvailable = tk.StringVar( rframe, "" )
label = makeStatusLabel( rframe, "Moves Available", 3, 0, movesAvailable )

# put a 'material balance' label within this frame
materialBalance = tk.StringVar( rframe, "" )
label = makeStatusLabel( rframe, "Material Balance", 4, 0, materialBalance )

# put 'controls' frame within this frame
frame = makeGroupFrame( rframe, "Controls", 5, 0 )

# put a 'start' button within this frame
startButton = makeControlButton( frame, "Start Game", 0, 0 )
startButton.bind( "<Button>", lambda event: startGame(event.widget) )

# put a 'back' button within this frame
takeBackButton = makeControlButton( frame, "Take Back Move", 0, 1 )
takeBackButton.bind( "<Button>", lambda event: takeMoveBack(event.widget) )
takeBackButton.config(  state=tk.DISABLED )

# put a 'place pieces' button within this frame
placePiecesButton = makeControlButton( frame, "Place Pieces", 1, 0 )
placePiecesButton.bind( "<Button>", lambda event: startPlacing(event.widget) )

# put a 'record' button within this frame
recordButton = makeControlButton( frame, "Record", 1, 1 )
recordButton.config( state=tk.DISABLED ) 

# put 'options' frame within this frame
frame = makeGroupFrame( rframe, "Options", 6, 0 )

# algebraic move descriptions ?
algebraicMoves = tk.BooleanVar( frame, False )
makeBoardOpt( frame, algebraicMoves, "Standard Notation", 0, 0 )

# show square name ?
showSqName = tk.BooleanVar( frame, True )
makeBoardOpt( frame, showSqName, "Square Names", 0, 1 )

# put white and black options within this frame
wframe = makeGroupFrame( frame, "White", 1, 0 )
bframe = makeGroupFrame( frame, "Black", 1, 1 )

# show possible moves ?
showWhitePossible = tk.BooleanVar( wframe, True )
showBlackPossible = tk.BooleanVar( bframe, True )
makeStatusOpt( wframe, showWhitePossible, bframe, showBlackPossible, "Preview Moves", 0, 0 )

# show can reach counts ?
showWhiteReach = tk.BooleanVar( wframe, True )
showBlackReach = tk.BooleanVar( bframe, True )
makeStatusOpt( wframe, showWhiteReach, bframe, showBlackReach, "# Can Reach Square", 1, 0 )

# show available move count ?
showWhiteMoveCnt = tk.BooleanVar( wframe, True )
showBlackMoveCnt = tk.BooleanVar( bframe, True )
makeStatusOpt( wframe, showWhiteMoveCnt, bframe, showBlackMoveCnt, "# Moves Available", 2, 0 )

# show position names ?
showWhitePosName = tk.BooleanVar( wframe, True )
showBlackPosName = tk.BooleanVar( bframe, True )
makeStatusOpt( wframe, showWhitePosName, bframe, showBlackPosName, "Position Names", 3, 0 )

# show tactic executed ?
showWhiteTactic = tk.BooleanVar( wframe, True )
showBlackTactic = tk.BooleanVar( bframe, True )
makeStatusOpt( wframe, showWhiteTactic, bframe, showBlackTactic, "Tactic Executed", 4, 0 )

# make (hidden) piece placer radiobox within this frame
piecePlace = tk.StringVar( frame, "" )
piecePlacer = makePlacer( frame, 0, 0, piecePlace )

centerOnScreen( root )

root.mainloop()
