# Massage Chess Openings

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

# first created: 03/31/25
# last revision: 04/01/25

#--------------------
# Python modules
# None
# program modules
# None
#--------------------

# the goal is to turn "Wikipedia:List of Chess Openings"
# into a Python dictionary we can import into our chess progam

# straightforward approach, but does not track very well:
# - positions where two like pieces can both reach the same square (not recorded)

# max number of moves for each side (max 9)

MOVELIMIT = 7

def clean(move):
	'''convert from algebraic to the internal form we use'''
	# white move ?
	if move[0] in "123456789":
		move = move[2:]
		iswhite = True
	else:
		iswhite = False

	# castle ?
	match move.count("-"):
		case 1:
			return "Kg1" if iswhite else "kg8"
		case 2:
			return "Kc1" if iswhite else "kc8"
		case _:
			pass

	# get rid of checking indicators
	move = move.replace( "+", "" )
	move = move.replace( "#", "" )

	match len(move):
		case 2:
			return f"P{move}" if iswhite else f"p{move}"
		case 3:
			return move if iswhite else move.lower()
		case 4 if "x" in move:
			destsq = move[ 2: ]
			piece = move[ 0 ]
			if piece in "abcdefgh":
				return f"P{destsq}" if iswhite else f"p{destsq}"
			else:
				return f"{piece.upper()}{destsq}" if iswhite else f"{piece.lower()}{destsq}"
		# notation includes disambiguation
		# - maybe we should figure out a way to use algebraic notation in our keys
		case _:
			return f"@@{move}@@"

total = discarded = 0

output = list()

with open("openings.txt") as f:
	for line in f:
		total += 1
		# does this line start with four spaces ?
		if not line.startswith("    "):
			discarded += 1
			continue
		# is there an opening in this line ?
		movestart = line.find( ": 1." )
		if movestart < 1:
			discarded += 1
			continue
		# get the last part of the descriptioin
		marker = line.rfind(",", 0, movestart )
		if marker < 1:
			marker = line.rfind( ":", 0, movestart )
		# if we still haven't got a start, there is no last part
		descstart = 4 if marker < 1 else marker + 1
		desc = line[descstart:movestart].strip()
		# get the moves of this opening
		moves = line[movestart+2:].split()
		# too many to bother with ?
		if len(moves) > MOVELIMIT*2:
			discarded += 1
			continue
		notation = list()
		for move in moves:
			notation.append( clean(move) )

		key = "".join( notation )
		if len(key)%3 != 0:
			print( f"\n*** Discarding {key}: {desc}" )
			discarded += 1
			continue

		output.append( f'\t"{key}": "{desc}",\n' )

# sorting isn't necessary, but it looks a bit neater
output.sort()

# decorate the result file
output.insert( 0, f"MDB_MAXMOVES = {MOVELIMIT*2}\n" )
output.insert( 1, "\n" )
output.insert( 2, "moveMDB = {\n" )

output.append( "\t}\n" )

with open("opendict.py", "w") as d:
	d.writelines( output )

print( f"\nDiscarded {discarded} of {total}" )
