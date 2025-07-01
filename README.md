# Deslizator


This repository is based on a programming paradigms practice for the Computer Science degree at the University of Valladolid.  
This practice is a block-falling video game in the style of Tetris, made in Python with the help of the wxPython library. A video example of a game execution is included.

## Game Rules

The game works as follows: each turn, blocks are created on the first line, and the player can make a move by dragging a block with the mouse until it collides with another block or a game wall, or by clicking on an empty cell to drop the line above.  
The objective of the game is to achieve the highest score before the game ends, which happens when a new row cannot be inserted at the top.  
To score points, rows must be eliminated by filling an entire row with blocks, which awards 10 points. Additionally, if the blocks in a row are all the same color, the entire board is cleared and the player earns points equal to the number of occupied cells on the board.

## Game Help

At the bottom right corner, a help message appears indicating the current state of the game.

## Other Options

The game allows increasing the number of rows or changing the animation speed by modifying the corresponding values. Also, the blocks that fall in each line are based on a sequence represented in the text file `list_rows_to_fall.txt`, which can be modified. This file, along with the wxPython library and Python itself, is necessary to run the game.  
If you look closely at the game, you can see a list of moves. This is requested for the course practice and is based on keyboard commands that were used in the initial versions to make moves before the graphical interface was created. The game is designed around these commands.
