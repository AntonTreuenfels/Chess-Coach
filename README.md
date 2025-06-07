# Chess-Coach
A virtual chess coach for beginning learners. The main idea is to show what it is possible to do in any given position. No advice or prescription of what to do is made beyond constraining moves to only what is legal.

In any position all legal moves, square names, what squares are attacked or defended, and how many moves in total can be made can be shown. These are all optional for both sides. They can be individually turned off to reduce any advantage they provide, as a way to perhaps "equalize" two players of different skill levels.

Each move made is described, either in standard algebraic notation or in English. If a move is part of a recognized sequence of opening moves, its name will be shown. Otherwise, if the move resulted in the execution of one or more recognized tactics (such as a check or a pin), they will be shown.

Positions can be saved and played back as puzzles. Likewise, games can be saved for later playback.

All functionality originally envisioned for the virtual chess choach is now implemented. It is quite useable as it stands. However, as of version 09b, it remains somewhat unpolished with a few rough edges.

The scripts use only what comes with a standard Python distribution. The graphical user interface and the database functions are provided by Tkinter and SQLite, respectively. There are no third-party libraries.


