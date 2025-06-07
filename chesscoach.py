# Virutal Chess Coach

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

# first created: 04/02/25
# last revision: 05/31/25

#--------------------
# Python modules
import argparse
from sys import exit, version_info
# program modules
import chessgui
#--------------------

# -------------------
# Main
# -------------------

def main():

	# minimum Python version needed
	if version_info.major < 3 or version_info.minor < 10:
		exit( "Python 3.10 or higher required" )

	# command line arguments
	parser = argparse.ArgumentParser(
		description="Show all current legal moves of any piece",
		)
	exclusive = parser.add_mutually_exclusive_group()
	exclusive.add_argument( "-p", "--puzzle",
		action="store_true",
		help="enter puzzle(s) into database",
		)
	exclusive.add_argument( "-g", "--game",
		action="store_true",
		help="enter complete games(s) into database",
		)
	args = parser.parse_args()

	chessgui.guiMain( "Virtual Chess Choach 0.9b", args )

# -------------------

if __name__ == "__main__":
	main()

