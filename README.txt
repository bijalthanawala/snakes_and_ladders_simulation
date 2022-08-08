SNAKES AND LADDERS SIMULATION
==================================

This is a simple, configurable Snake and Ladders game simulator.
The simulator runs a specified (configurable) number of times,
and collects a set of statistics and prints on the screen.

In this early stages it is still unoptimized in various areas.

REQUIREMENTS:
    - Python3


----------


CONFIGURE:
All the configuration is read from this file in the root of the project:
    - game.conf

Following aspects of the simulator are configurable:
    - Number of times to run the simulator
    - Number of players
    - Number and placement of snakes
    - Number and placement of ladders

The above mentioned configuration file has a running, working set of values
and also has instructions on how to change any.


----------


USAGE:
To run, type following on the command line - while in the root of the project
directory:

python3 -m src.snake_ladder_simulation


OR

python3 -m src.snake_ladder_simulation --verbose
[Prints the important moves]

OR

python3 -m src.snake_ladder_simulation --verbose --verbose
[Prints board configuration details and every single move]


----------


TEST:
The bundled tests are written with pytest and can be run with following
command - while in the root of the project directory:

pytest --verbose

The simulator has been so far tested on, and known to work on
    - Apple MacOS
    - Fedora Linux


NOTES:
* Among others, some of the restrictions on the configuration of the snakes and the ladders include:
    - A snake or a ladder spanning the entire board is not allowed
    - Placing a snake on the winning position (100) is not allowed
    - A snake or a ladder not spanning at least one row (i.e. horizontal) are not allowed
     (This restriction on horizontal placement is only to maintain the aesthatics of the game board)
    In the current implementation, simulator notifies and halts upon detecting the above conditions
* Lucky move is counted twice in a single move in the following cases:
    -   If a snake's head is positioned at 98 or 99, arriving at the winnig position (100)
        from any position 97 or less is counted 'lucky' twice
    -   If a players arrives at the bottom of a ladder, and if that also happens to be one
        or two positions away from a snake's head than two 'lucky' moves are counted
* Within a die-roll-streak (triggered by a roll of 6):
    -   In case of a die-roll-streak, e.g. [6,6,2], each chance encounter with a snake
        or a ladder for every single roll within that streak is honored
* Bounce back:
    If a player rolls more than the last n required to win, then the token will be bounced back
    eg. a player on 97 (who needs 3 to win) rolls 5 will bounce back to 98 (100-2)

================================================
