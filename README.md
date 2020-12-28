# Tic-Tac-Ception

![Logo](static/Tic-Tac-Ception_Logo.png?raw=true "Title")

This is a game of Tic-Tac-Toes within a Tic-Tac-Toe!  
You can play the game at [www.tic-tac-ception.com](http://www.tic-tac-ception.com)

## How to play
### Basic flow
The starting player can make the first move anywhere. After that, the following player needs to play on the board that corresponds to the previous move.  
Sample start of a game:  
1. X starts by playing on the center-board, in the **top-right** *position*;
2. The next move should be played on the **top-right** *board*, in any open position. O plays in the top-right board, on the **bottom-left** *position*;
3. X now needs to play on the **bottom-left** *board*, in any open position.

### What happens when a small board is over?
A small board can end because (1) a player won, or (2) there are no open positions. When a small board is over, a different set of rules applies on the move restriction.  
1. X is next to play, and should have played in a small board that X won -> X can play in any open position;
2. X is next to play, and should have played in a small board that tied -> X can play in any open position;
3. X is next to play, and should have played in a small board that **O** won -> **O** can choose any small board that's not over for X to play.

### How does it end?
Like a regular tic-tac-toe, the game ends when there is (1) a winner or (2) all small boards are over.
1. The regular rules apply -- you need to win three straight small boards (any row, column, or diagonal) to win;
2. The winner will be the player with most small board wons. If tied, then the game ends in a draw.

### Thanks
Thanks to Brian for introducing me to this game and Kenneth for suggesting the name!

### Say hi :)
[hi@tic-tac-ception.com](mailto:hi@tic-tac-ception.com)
