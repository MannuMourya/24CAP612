# Simple Maze Game

A mini project for Design and Analysis of Algorithms (DAA) course that implements a maze game using Prim's and Kruskal's algorithms.

## Overview

This maze game demonstrates the application of two classic minimum spanning tree algorithms (Prim's and Kruskal's) to generate random mazes. The player navigates through the procedurally generated maze from the start point (green) to the end point (red).

## Features

- Dynamic maze generation using either Prim's or Kruskal's algorithm
- Simple keyboard controls for player movement
- Visual feedback for game state and win condition
- Ability to generate new mazes on demand

## How to Play

1. Run the game: `python maze_game.py`
2. Use arrow keys to move the player (blue circle)
3. Navigate from the start (green) to the end (red)
4. Press 'P' to generate a new maze using Prim's algorithm
5. Press 'K' to generate a new maze using Kruskal's algorithm

## Requirements

- Python 3.x
- Pygame

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/maze-game.git

# Change directory
cd maze-game

# Install dependencies
pip install pygame

# Run the game
python maze_game.py
