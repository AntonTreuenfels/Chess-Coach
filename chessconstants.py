# Chess Constants

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

# first created: 03/18/25
# last revision: 03/23/25

#--------------------
# Python modules
# none
# program modules
# none
#--------------------

# these are constant values that need to be known by more than one module

# piece colors

PC_WHITE = "White"
PC_BLACK = "Black"

# move outcomes (bit-coded)

OC_NONE 	= 0x000	# nothing special
OC_CHECK	= 0x001	# enemy in check
OC_DOUBLE	= 0x002	# enemy in double check
OC_FORK		= 0x004	# enemy forked
OC_FORK3	= 0x008	# enemy triple forked
OC_FORKM	= 0x010	# enemy forked four or more times
OC_PIN		= 0x020	# enemy pinned
OC_SKEWER	= 0x040	# enemy skewered
OC_BATTERY	= 0x080	# formed battery
OC_ATTACK	= 0x100	# more friendly attackers than enemy defenders
OC_ATTACKED	= 0x200	# more enemy defenders than friendly attackers

# empty square

SQ_EMPTY	= "."