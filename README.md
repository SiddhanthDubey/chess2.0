# 10x10 Fantasy Chess

A unique chess variant featuring a 10x10 board with five new fantasy pieces, custom movement rules, and exciting gameplay mechanics.

## Overview

This fantasy chess game expands traditional chess to a 10x10 board and introduces new pieces with unique abilities. The game includes special mechanics like the Prince-to-King transformation, the mimicking Jester, and the teleporting Bureaucrat.

## Features

- **10x10 Chessboard**: Expanded playing field with 100 squares
- **5 New Fantasy Pieces**: Jester, Squire, Paladin, Prince, and Princess
- **Auto-Flipping Board**: Board automatically flips after each move for optimal viewing
- **Visual Move Indicators**: Color-coded highlights for regular moves, captures, and Bureaucrat teleportation
- **Smooth Gameplay**: Pygame-powered graphics with piece images
- **Special Rules**: En passant, castling, pawn promotion, and Prince succession

## Installation

### Prerequisites

- Python 3.7 or higher
- Pygame library

### Setup

1. Clone or download this repository

2. Install Pygame:
```bash
pip install pygame
```

3. Create the asset folder structure:
```
your_project/
├── chess_game_fantasy.py
└── assets/
    └── pieces/
        ├── wK.png, bK.png (King)
        ├── wQ.png, bQ.png (Queen)
        ├── wR.png, bR.png (Rook)
        ├── wB.png, bB.png (Bishop)
        ├── wN.png, bN.png (Knight)
        ├── wP.png, bP.png (Pawn)
        ├── wC.png, bC.png (Bureaucrat)
        ├── wJ.png, bJ.png (Jester)
        ├── wS.png, bS.png (Squire)
        ├── wL.png, bL.png (Paladin)
        ├── wV.png, bV.png (Prince)
        └── wW.png, bW.png (Princess)
```

4. Run the game:
```bash
python chess_game_fantasy.py
```

## Game Rules

### Board Setup

The 10x10 board is set up with the following back rank (row 0 for black, row 9 for white):
```
R - N - B - J - K - Q - C - B - N - R
```

The front rank contains:
- **Pawns** at columns 0, 3, 6, 9
- **Squires** at columns 1, 8 (in front of Knights)
- **Paladins** at columns 2, 7 (in front of Bishops)
- **Prince** at column 4 (in front of King)
- **Princess** at column 5 (in front of Queen)

### Traditional Pieces

- **King (K)**: Moves one square in any direction. Can castle if conditions are met.
- **Queen (Q)**: Moves any number of squares in any direction (orthogonal or diagonal).
- **Rook (R)**: Moves any number of squares orthogonally (horizontal or vertical).
- **Bishop (B)**: Moves any number of squares diagonally.
- **Knight (N)**: Moves in an L-shape (2 squares in one direction, 1 square perpendicular). Jumps over pieces.
- **Pawn (P)**: Moves forward one square (or two from starting position). Captures diagonally. Promotes upon reaching the opposite end.

### Fantasy Pieces

#### Jester (J)
- **Movement**: Mimics the last piece moved by the opponent
- **Special**: If no piece has been moved yet, moves like a King
- **Capture**: Can capture normally using the mimicked movement pattern
- **Note**: Cannot mimic another Jester (defaults to King movement)

#### Squire (S)
- **Movement**: Jumps exactly 2 squares orthogonally (up, down, left, right)
- **Special**: Jumps over any piece in between
- **Promotion**: Becomes a Knight upon reaching the opposite back rank

#### Paladin (L)
- **Movement**: Jumps exactly 2 squares diagonally
- **Special**: Jumps over any piece in between
- **Promotion**: Becomes a Bishop upon reaching the opposite back rank

#### Prince (V)
- **Movement**: Moves up to 2 squares in any direction (orthogonal or diagonal)
- **Special**: Cannot jump; path must be clear
- **Royal Succession**: When the King is captured, the Prince immediately becomes the King and the Princess becomes a Queen (if still alive)
- **Protection**: As long as both King and Prince are alive, the King cannot be put in check

#### Princess (W)
- **Movement**: Moves up to 3 squares in any direction (like a Queen but limited to 3 squares)
- **Special**: Cannot jump; path must be clear
- **Royal Succession**: Becomes a Queen when the Prince becomes King

#### Bureaucrat (C)
- **Movement**: Can teleport to ANY empty square of the same color as its current square
- **Special**: Cannot capture pieces (move to empty squares only)
- **Highlight**: Blue highlight indicates available teleportation squares

### Special Rules

1. **Castling**: Same rules as standard chess, adapted for the 10x10 board positioning
   
2. **En Passant**: Pawns can capture enemy pawns that just moved two squares forward

3. **Pawn Promotion**: Pawns reaching the opposite end can promote to Queen, Rook, Bishop, Knight, Bureaucrat, Jester, Squire, Paladin, Prince, or Princess

4. **Royal Succession**: 
   - If your King is captured while your Prince is alive, the Prince immediately becomes the King
   - The Princess simultaneously becomes a Queen (if alive)
   - The new King cannot castle (inherits moved status)
   - If the Prince was killed first, normal checkmate rules apply

5. **Check Protection**: While both King and Prince are alive, the King cannot be in check (special royal protection)

## How to Play

1. **Starting the Game**: Run the script to start. White moves first.

2. **Making Moves**:
   - Click on a piece to select it
   - Valid moves are highlighted in green
   - Capture moves are highlighted in red
   - Bureaucrat teleportation squares are highlighted in blue
   - Click on a highlighted square to move

3. **Board Flipping**: The board automatically flips after each move so both players view from their perspective

4. **Promotion**: When a Pawn, Squire, or Paladin reaches the opposite end, click on your desired promotion piece

5. **Winning**: 
   - Checkmate your opponent's King (if they have no Prince)
   - If they have a Prince, you must capture both the King AND the transformed Prince-King
   - Stalemate results in a draw

## Visual Indicators

- **Green Highlight**: Valid move squares
- **Red Highlight**: Squares with enemy pieces you can capture
- **Blue Highlight**: Bureaucrat teleportation destinations

## Controls

- **Left Mouse Click**: Select piece / Make move
- **Window Close Button**: Exit game

## Tips and Strategy

1. **Protect Your Prince**: Keep your Prince safe as backup royalty
2. **Use the Jester Wisely**: Plan opponent's moves to maximize Jester's potential
3. **Bureaucrat Positioning**: Use the Bureaucrat to control key squares without blocking other pieces
4. **Squire and Paladin**: Great for surprising attacks with their jumping ability
5. **Princess Power**: The Princess's 3-square range makes it excellent for mid-game control

## Technical Details

- **Resolution**: 800x800 pixels
- **Board Size**: 10x10 squares
- **Square Size**: 80x80 pixels
- **Framework**: Pygame
- **Language**: Python 3

## Troubleshooting

**No piece images showing?**
- Ensure all PNG files are in the `assets/pieces/` folder
- Check that filenames match exactly (case-sensitive): `wK.png`, `bJ.png`, etc.
- The game will display letters as fallback if images are missing

**Game won't start?**
- Verify Pygame is installed: `pip install pygame`
- Check Python version: `python --version` (requires 3.7+)

## Credits

Created as a custom chess variant combining traditional chess mechanics with fantasy role-playing game elements.

## License

Free to use and modify for personal and educational purposes.

---

Enjoy your game of Fantasy Chess! May the best strategist win!
