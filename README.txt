Snakes and ladders simulation

NOTES
-   In case of a die-roll-streak, e.g. [6,6,2], each chance encounter with a snake or a ladder
    for every single roll within that streak is honored
-   Max length allowed for a snake within the board boundaries is 99
-   If a snake's head is positioned at 98 or 99, arriving at the winnig position (100)
    from any position 97 or less is considered a 'lucky' move
-   If a players arrives at the bottom of a ladder, and if that also happens to be one
    or two positions away from a snake's head than two lucky moves are counted

SPECIAL CASES
Bounce back:
    If a player rolls more than the last n required to win, will bounce back
    eg. a player on 97 (who needs 3 to win) rolls 5 will bounce back to 98 (100-2)
