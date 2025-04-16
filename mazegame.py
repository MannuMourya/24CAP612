import pygame
import random
import sys
from enum import Enum
from collections import defaultdict

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 20
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Game - Press K for Kruskal's or P for Prim's")
clock = pygame.time.Clock()

class Algorithm(Enum):
    PRIMS = 1
    KRUSKALS = 2

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.walls = {"top": True, "right": True, "bottom": True, "left": True}
        self.visited = False

    def draw(self, screen):
        x, y = self.x * CELL_SIZE, self.y * CELL_SIZE
        
        # Draw walls
        if self.walls["top"]:
            pygame.draw.line(screen, BLACK, (x, y), (x + CELL_SIZE, y), 2)
        if self.walls["right"]:
            pygame.draw.line(screen, BLACK, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), 2)
        if self.walls["bottom"]:
            pygame.draw.line(screen, BLACK, (x, y + CELL_SIZE), (x + CELL_SIZE, y + CELL_SIZE), 2)
        if self.walls["left"]:
            pygame.draw.line(screen, BLACK, (x, y), (x, y + CELL_SIZE), 2)

class Maze:
    def __init__(self):
        self.grid = [[Cell(x, y) for y in range(GRID_HEIGHT)] for x in range(GRID_WIDTH)]
        self.start = self.grid[0][0]
        self.end = self.grid[GRID_WIDTH - 1][GRID_HEIGHT - 1]
        self.player_pos = (0, 0)
    
    def reset(self):
        self.grid = [[Cell(x, y) for y in range(GRID_HEIGHT)] for x in range(GRID_WIDTH)]
        self.start = self.grid[0][0]
        self.end = self.grid[GRID_WIDTH - 1][GRID_HEIGHT - 1]
        self.player_pos = (0, 0)
    
    def get_neighbors(self, cell):
        neighbors = []
        x, y = cell.x, cell.y
        
        # Check all neighbors
        if x > 0:  # Left
            neighbors.append((self.grid[x-1][y], "left"))
        if x < GRID_WIDTH - 1:  # Right
            neighbors.append((self.grid[x+1][y], "right"))
        if y > 0:  # Top
            neighbors.append((self.grid[x][y-1], "top"))
        if y < GRID_HEIGHT - 1:  # Bottom
            neighbors.append((self.grid[x][y+1], "bottom"))
            
        return neighbors
    
    def remove_wall(self, current, next_cell, direction):
        if direction == "left":
            current.walls["left"] = False
            next_cell.walls["right"] = False
        elif direction == "right":
            current.walls["right"] = False
            next_cell.walls["left"] = False
        elif direction == "top":
            current.walls["top"] = False
            next_cell.walls["bottom"] = False
        elif direction == "bottom":
            current.walls["bottom"] = False
            next_cell.walls["top"] = False
    
    def generate_prims(self):
        # Reset the maze
        self.reset()
        
        # Start from a random cell
        current = self.grid[random.randint(0, GRID_WIDTH - 1)][random.randint(0, GRID_HEIGHT - 1)]
        current.visited = True
        
        # Frontier cells (unvisited neighbors of visited cells)
        frontier = []
        
        # Add neighbors of the starting cell to frontier
        neighbors = self.get_neighbors(current)
        for neighbor, direction in neighbors:
            if not neighbor.visited:
                frontier.append((neighbor, current, direction))
        
        # While there are frontier cells
        while frontier:
            # Pick a random frontier cell
            index = random.randint(0, len(frontier) - 1)
            next_cell, parent, direction = frontier.pop(index)
            
            # If the cell hasn't been visited yet
            if not next_cell.visited:
                # Remove the wall between the cell and its parent
                self.remove_wall(parent, next_cell, direction)
                
                # Mark the cell as visited
                next_cell.visited = True
                
                # Add unvisited neighbors to frontier
                for neighbor, dir_to_neighbor in self.get_neighbors(next_cell):
                    if not neighbor.visited:
                        frontier.append((neighbor, next_cell, dir_to_neighbor))
        
        # Mark start and end
        self.start = self.grid[0][0]
        self.end = self.grid[GRID_WIDTH - 1][GRID_HEIGHT - 1]
        self.player_pos = (0, 0)
    
    def find(self, parent, i):
        if parent[i] != i:
            parent[i] = self.find(parent, parent[i])
        return parent[i]
    
    def union(self, parent, rank, x, y):
        root_x = self.find(parent, x)
        root_y = self.find(parent, y)
        
        if root_x == root_y:
            return
        
        if rank[root_x] < rank[root_y]:
            parent[root_x] = root_y
        elif rank[root_x] > rank[root_y]:
            parent[root_y] = root_x
        else:
            parent[root_y] = root_x
            rank[root_x] += 1
    
    def generate_kruskals(self):
        # Reset the maze
        self.reset()
        
        # Create a list of all walls
        edges = []
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                cell = self.grid[x][y]
                cell_id = y * GRID_WIDTH + x
                
                # Add right wall if not on the right edge
                if x < GRID_WIDTH - 1:
                    right_cell_id = y * GRID_WIDTH + (x + 1)
                    edges.append((cell_id, right_cell_id, "horizontal", x, y))
                
                # Add bottom wall if not on the bottom edge
                if y < GRID_HEIGHT - 1:
                    bottom_cell_id = (y + 1) * GRID_WIDTH + x
                    edges.append((cell_id, bottom_cell_id, "vertical", x, y))
        
        # Shuffle edges
        random.shuffle(edges)
        
        # Initialize parent and rank arrays for Union-Find
        parent = [i for i in range(GRID_WIDTH * GRID_HEIGHT)]
        rank = [0] * (GRID_WIDTH * GRID_HEIGHT)
        
        # Process each edge
        for edge in edges:
            u, v, orientation, x, y = edge
            
            if self.find(parent, u) != self.find(parent, v):
                self.union(parent, rank, u, v)
                
                # Remove walls
                if orientation == "horizontal":  # Right wall
                    self.grid[x][y].walls["right"] = False
                    self.grid[x+1][y].walls["left"] = False
                else:  # Bottom wall
                    self.grid[x][y].walls["bottom"] = False
                    self.grid[x][y+1].walls["top"] = False
        
        # Mark all cells as visited for proper drawing
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                self.grid[x][y].visited = True
        
        # Mark start and end
        self.start = self.grid[0][0]
        self.end = self.grid[GRID_WIDTH - 1][GRID_HEIGHT - 1]
        self.player_pos = (0, 0)
    
    def draw(self, screen):
        # Clear the screen
        screen.fill(WHITE)
        
        # Draw grid
        for row in self.grid:
            for cell in row:
                cell.draw(screen)
        
        # Draw start cell (green)
        pygame.draw.rect(screen, GREEN, 
                         (self.start.x * CELL_SIZE + 2, 
                          self.start.y * CELL_SIZE + 2,
                          CELL_SIZE - 4, 
                          CELL_SIZE - 4))
        
        # Draw end cell (red)
        pygame.draw.rect(screen, RED, 
                         (self.end.x * CELL_SIZE + 2, 
                          self.end.y * CELL_SIZE + 2,
                          CELL_SIZE - 4, 
                          CELL_SIZE - 4))
        
        # Draw player
        pygame.draw.circle(screen, BLUE,
                          (self.player_pos[0] * CELL_SIZE + CELL_SIZE // 2,
                           self.player_pos[1] * CELL_SIZE + CELL_SIZE // 2),
                          CELL_SIZE // 3)
    
    def move_player(self, direction):
        x, y = self.player_pos
        current_cell = self.grid[x][y]
        
        if direction == "up" and not current_cell.walls["top"] and y > 0:
            self.player_pos = (x, y - 1)
        elif direction == "right" and not current_cell.walls["right"] and x < GRID_WIDTH - 1:
            self.player_pos = (x + 1, y)
        elif direction == "down" and not current_cell.walls["bottom"] and y < GRID_HEIGHT - 1:
            self.player_pos = (x, y + 1)
        elif direction == "left" and not current_cell.walls["left"] and x > 0:
            self.player_pos = (x - 1, y)
        
        # Check if player reached the end
        if self.player_pos == (self.end.x, self.end.y):
            return True
        return False

def main():
    maze = Maze()
    maze.generate_prims()  # Default algorithm is Prim's
    game_won = False
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    maze.generate_prims()
                    game_won = False
                elif event.key == pygame.K_k:
                    maze.generate_kruskals()
                    game_won = False
                
                if not game_won:
                    if event.key == pygame.K_UP:
                        game_won = maze.move_player("up")
                    elif event.key == pygame.K_RIGHT:
                        game_won = maze.move_player("right")
                    elif event.key == pygame.K_DOWN:
                        game_won = maze.move_player("down")
                    elif event.key == pygame.K_LEFT:
                        game_won = maze.move_player("left")
        
        # Draw everything
        maze.draw(screen)
        
        # Display game won message
        if game_won:
            font = pygame.font.SysFont(None, 55)
            text = font.render('You Won! Press P or K to restart', True, PURPLE)
            text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2))
            screen.blit(text, text_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()