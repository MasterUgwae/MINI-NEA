# main.py

# TODO: display the coordinates of the center of the screen, the angel and the last placed block
# include a winning display screen with a button to go back to the menu
# include a button to exit to the menu
# include a button to exit the game

import os
import sys

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'



import pygame


class Clickable:



    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

class Tile(Clickable):

    def __init__(self, x, y, grid_tile_width, grid_tile_height):
        #x, y are the tiles position on the grid and not the screen
        super().__init__(x, y, grid_tile_width, grid_tile_height)

    def draw(self, screen, angel_x, angel_y, angel_power ):
        ## Check if the tile is within the angel's range
        ## if the tile is within the angel's range, draw it
        ## Otherwise, draw it as gray
        rect = pygame.Rect(self.x * self.width, self.y * self.height, self.width, self.height)
        if (self.x == angel_x and self.y == angel_y):
            pygame.draw.rect(screen, (255, 251, 0), rect, border_radius=5)
        elif (self.x >= angel_x - angel_power and self.x <= angel_x + angel_power and
                self.y >= angel_y - angel_power and self.y <= angel_y + angel_power):
            pygame.draw.rect(screen, (123, 242, 242), rect, border_radius=5)
        else:
            pygame.draw.rect(screen, (200, 200, 200), rect, border_radius=5)

class BlockedTile(Clickable):

    def __init__(self, x, y, grid_tile_width, grid_tile_height):
        super().__init__(x, y, grid_tile_width, grid_tile_height)

    def is_on_grid(self, grid_left, grid_top, visible_tile_count_width, visible_tile_count_height):
        # Check if the absolute tile coordinate lies within the visible grid
        return (self.x >= grid_left and
                self.x < grid_left + visible_tile_count_width and
                self.y >= grid_top and
                self.y < grid_top + visible_tile_count_height)

    def draw(self, screen, grid_left, grid_top):
        # Calculate the tile's position relative to the visible grid.
        visible_x = self.x - grid_left
        visible_y = self.y - grid_top
        block_x = visible_x * self.width
        block_y = visible_y * self.height
        pygame.draw.rect(screen, (125, 19, 19), (block_x, block_y, self.width, self.height), border_radius=5)
class Button(Clickable):

    def __init__(self, x, y, width, height, text):
        super().__init__(x, y, width, height)
        self.text = text

    def draw(self, screen):
        pygame.draw.rect(screen, (85, 85, 85), (self.x-self.width // 2, self.y-self.height // 2, self.width, self.height), border_radius=5)
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.x, self.y))
        screen.blit(text_surface, text_rect)

    def is_clicked(self, mouse_x, mouse_y):
        return (self.x - self.width // 2 <= mouse_x <= self.x + self.width // 2 and
                self.y - self.height // 2 <= mouse_y <= self.y + self.height // 2)

# A simple Move class to store the move info.
class Move:
    def __init__(self, move_type, tile_x, tile_y):
        """
        move_type: "angel" or "block"
        tile_x, tile_y: absolute tile coordinates at which the move occurred.
        """
        self.move_type = move_type
        self.tile_x = tile_x
        self.tile_y = tile_y

class GameState:
    def __init__(self):
        # Screen dimensions
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600

        # Grid area dimensions (e.g. 600x600 for the grid, leaving 200 for UI)
        self.GRID_AREA_WIDTH = 600
        self.GRID_AREA_HEIGHT = 600

        # Grid settings (10x10 grid)
        self.GRID_COLS = 10
        self.GRID_ROWS = 10
        self.tile_width = self.GRID_AREA_WIDTH // self.GRID_COLS
        self.tile_height = self.GRID_AREA_HEIGHT // self.GRID_ROWS

        # Offsets: these are absolute tile indices for the top-left tile of the grid view.
        self.grid_left = 0
        self.grid_top = 0

        # Angel's absolute position (tile coordinates) and power
        self.angel_power = 1
        self.angel_x = 0  
        self.angel_y = 0

        # List of BlockedTiles (using absolute coordinates)
        self.blocks = []

        # Move stacks for undo/redo; each element is a Move object.
        self.undo_stack = []
        self.redo_stack = []

        # UI buttons for undo and redo (positioned to the right of the grid area)
        self.undo_button = Button(700, 160, 80, 40, "Undo")
        self.redo_button = Button(700, 220, 80, 40, "Redo")
    def add_clock(self, clock):
        self.clock = clock

    def add_screen(self, screen):
        self.screen = screen

    def add_block(self, block):
        self.blocks.append(block)

def main():
    game_state = GameState()

    pygame.init()
    pygame.font.init()
    pygame.display.set_caption('Angel Problem')
    screen = pygame.display.set_mode((game_state.SCREEN_WIDTH, game_state.SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    game_state.add_screen(screen)
    game_state.add_clock(clock)

    end = startScreen(game_state)
    start = False
    while not (end or start):
        start, end = menu(game_state)
        print("ended menu")
        if start:
            game_state = gameloop(game_state)
    exitGame()

def startScreen(game_state):
    # Fill half of the screen with white and the other half with red
    SCREEN_WIDTH = game_state.SCREEN_WIDTH
    SCREEN_HEIGHT = game_state.SCREEN_HEIGHT
    clock = game_state.clock
    screen = game_state.screen
    screen.fill((255, 255, 255))
    half_screen = SCREEN_WIDTH // 2
    pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(0,0, half_screen, SCREEN_HEIGHT), border_radius=5)
    title = pygame.font.Font(None, 74).render("Angel Problem", True, (0, 0, 0))
    title_rect = title.get_rect(center=(half_screen // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(title, title_rect)
    startButton = Button(half_screen, SCREEN_HEIGHT // 2 - 25, 100, 50, "Start")
    start = False
    end = False
    while not (start or end):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                end = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if startButton.is_clicked(mouse_x, mouse_y):
                    start = True

        screen.fill((255, 255, 255))
        pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(0,0, half_screen, SCREEN_HEIGHT), border_radius=5)
        startButton.draw(screen)
        pygame.display.update()
        clock.tick(60)
    if end:
        return True
    else:
        return False

def menu(game_state):
    SCREEN_WIDTH = game_state.SCREEN_WIDTH
    SCREEN_HEIGHT = game_state.SCREEN_HEIGHT
    clock = game_state.clock
    screen = game_state.screen
    clearScreen(screen, (230, 230, 230))
    play_button = Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 25, 100, 50, "Play")
    options_button = Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 25, 100, 50, "Options")
    exit_button = Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 75, 100, 50, "Exit")
    end = False
    start = False
    while not(end or start):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                end = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if (play_button.is_clicked(mouse_x, mouse_y)):
                    start = True
                elif (options_button.is_clicked(mouse_x, mouse_y)):
                    game_state = options(game_state)
                elif (exit_button.is_clicked(mouse_x, mouse_y)):
                    end = True
        clearScreen(screen)
        play_button.draw(screen)
        options_button.draw(screen)
        exit_button.draw(screen)
        pygame.display.update()
        clock.tick(60)
    return start, end

def options(game_state):
    # Add the option to change the angel's power using up and down buttons
    SCREEN_WIDTH = game_state.SCREEN_WIDTH
    SCREEN_HEIGHT = game_state.SCREEN_HEIGHT
    clock = game_state.clock
    screen = game_state.screen
    angel_power = game_state.angel_power
    clearScreen(screen, (230, 230, 230))

    title = pygame.font.Font(None, 74).render("Options", True, (0, 0, 0))
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(title, title_rect)
    angel_power_text = pygame.font.Font(None, 36).render(f"Angel Power: {angel_power}", True, (0, 0, 0))
    angel_power_text_rect = angel_power_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(angel_power_text, angel_power_text_rect)
    up_button = Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, 100, 50, "Up")
    down_button = Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100, 100, 50, "Down")
    back_button = Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150, 100, 50, "Back")
    loop = True
    while loop:
        clearScreen(screen, (230, 230, 230))
        back_button.draw(screen)
        up_button.draw(screen)
        down_button.draw(screen)
        angel_power_text = pygame.font.Font(None, 36).render(f"Angel Power: {angel_power}", True, (0, 0, 0))
        angel_power_text_rect = angel_power_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(angel_power_text, angel_power_text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                loop = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if (up_button.is_clicked(mouse_x, mouse_y)):
                    angel_power += 1
                    game_state.angel_power = angel_power
                elif (down_button.is_clicked(mouse_x, mouse_y)):
                    if (angel_power > 1):
                        angel_power -= 1
                        game_state.angel_power = angel_power
                    else:
                        angel_power = 1
                elif (back_button.is_clicked(mouse_x, mouse_y)):
                    loop = False

        pygame.display.update()
        clock.tick(60)
    return game_state


# A helper to center the grid view on a given move.
def center_grid_on_move(game_state, move_x, move_y):
    half_cols = game_state.GRID_COLS // 2  
    half_rows = game_state.GRID_ROWS // 2   
    game_state.grid_left = move_x - half_cols
    game_state.grid_top = move_y - half_rows



# In your gameloop, you can directly record moves and update state.
def gameloop(game_state):
    SCREEN_WIDTH = game_state.SCREEN_WIDTH
    SCREEN_HEIGHT = game_state.SCREEN_HEIGHT
    clock = game_state.clock
    screen = game_state.screen
    grid_width = game_state.tile_width  # using tile_width now derived from the grid area.
    grid_height = game_state.tile_height
    current_player = "Angel"
    turn_number = 1
    grid = [[Tile(i, j, grid_width, grid_height) for j in range(game_state.GRID_ROWS)]
            for i in range(game_state.GRID_COLS)]  # 10x10 grid as before

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exitGame()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                # Check if click is in the UI panel
                if mouse_x > game_state.GRID_AREA_WIDTH:
                    # UI area for undo/redo
                    if game_state.undo_button.is_clicked(mouse_x, mouse_y):
                        game_state = undoMove(game_state)
                        if game_state.undo_stack:
                            current_player = "Angel" if turn_number % 2 == 0 else "Devil"
                            turn_number -= 1
                    elif game_state.redo_button.is_clicked(mouse_x, mouse_y):
                        game_state = redoMove(game_state)
                        if game_state.redo_stack:
                            current_player = "Angel" if turn_number % 2 == 0 else "Devil"
                            turn_number += 1
                else:
                    # Process grid clicks (angel move or block placement).
                    if current_player == "Angel":
                        # Convert click (in pixels) into an absolute tile coordinate.
                        tile_x = (mouse_x // grid_width) + game_state.grid_left
                        tile_y = (mouse_y // grid_height) + game_state.grid_top
                        print("clicked (abs):", tile_x, tile_y)
                        print("angel at:", game_state.angel_x, game_state.angel_y)
                        # use checkLegalMove with appropriate coordinate conversion.
                        if checkLegalMove(game_state, tile_x - game_state.grid_left, tile_y - game_state.grid_top):
                            # Record the angel move.
                            move = Move("angel", tile_x, tile_y)
                            game_state.undo_stack.append(move)
                            game_state.redo_stack.clear()
                            
                            # Update angel's state.
                            game_state.angel_x = tile_x
                            game_state.angel_y = tile_y
                            current_player = "Devil"
                            turn_number += 1
                    elif current_player == "Devil":
                        # For block placement, convert click coordinates:
                        tile_x = (mouse_x // grid_width) + game_state.grid_left
                        tile_y = (mouse_y // grid_height) + game_state.grid_top

                        # Check that tile is available and within the grid.
                        if (tile_x >= game_state.grid_left and tile_x < game_state.grid_left + game_state.GRID_COLS and
                            tile_y >= game_state.grid_top and tile_y < game_state.grid_top + game_state.GRID_ROWS):
                            # Prevent duplicate block placements and block if angel is here.
                            if not any(b.x == tile_x and b.y == tile_y for b in game_state.blocks) and \
                               not (tile_x == game_state.angel_x and tile_y == game_state.angel_y):
                                new_block = BlockedTile(tile_x, tile_y, grid_width, grid_height)
                                move = Move("block", tile_x, tile_y)
                                game_state.undo_stack.append(move)
                                game_state.redo_stack.clear()
                                
                                game_state.blocks.append(new_block)
                                current_player = "Angel"
                                turn_number += 1
                                if checkWin(game_state):
                                    print("Devil wins!")
                                    exitGame()

            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]:
                    game_state = moveGrid(game_state, event.key)
                    
        renderGrid(screen, game_state, grid, current_player, turn_number)
        # Optionally, render the UI buttons in the UI region.

# The undoMove function is where we now center the grid.
def undoMove(game_state):
    if not game_state.undo_stack:
        print("Nothing to undo.")
        return game_state

    move = game_state.undo_stack.pop()

    if move.move_type == "angel":
        # Look back at the last angel move if there is one.
        last_angel_move = None
        for m in reversed(game_state.undo_stack):
            if m.move_type == "angel":
                last_angel_move = m
                break
        if last_angel_move:
            game_state.angel_x = last_angel_move.tile_x
            game_state.angel_y = last_angel_move.tile_y
            center_grid_on_move(game_state, last_angel_move.tile_x, last_angel_move.tile_y)
        else:
            # Default state if no previous angel move.
            game_state.angel_x = 0
            game_state.angel_y = 0
            center_grid_on_move(game_state, 0, 0)
    elif move.move_type == "block":
        # Remove the block that matches this move.
        game_state.blocks = [b for b in game_state.blocks if not (b.x == move.tile_x and b.y == move.tile_y)]
        # Center on the most recent move in the undo stack.
        if game_state.undo_stack:
            last = game_state.undo_stack[-1]
            center_grid_on_move(game_state, last.tile_x, last.tile_y)

    game_state.redo_stack.append(move)
    return game_state

def redoMove(game_state):
    if not game_state.redo_stack:
        print("Nothing to redo.")
        return game_state

    move = game_state.redo_stack.pop()

    if move.move_type == "angel":
        game_state.angel_x = move.tile_x
        game_state.angel_y = move.tile_y
        center_grid_on_move(game_state, move.tile_x, move.tile_y)
    elif move.move_type == "block":
        new_block = BlockedTile(move.tile_x, move.tile_y, game_state.tile_width, game_state.tile_height)
        game_state.blocks.append(new_block)
        center_grid_on_move(game_state, move.tile_x, move.tile_y)

    game_state.undo_stack.append(move)
    return game_state
 

def renderGrid(screen, game_state, grid, current_player, turn_number):
    clock = game_state.clock
    screen.fill((255, 255, 255))
    # Calculate visible angel coordinates based on the current grid offset:
    visible_angel_x = game_state.angel_x - game_state.grid_left
    visible_angel_y = game_state.angel_y - game_state.grid_top

    for i in range(10):
        for j in range(10):
            grid[i][j].draw(screen, visible_angel_x, visible_angel_y, game_state.angel_power)

    for block in game_state.blocks:
        if block.is_on_grid(game_state.grid_left, game_state.grid_top, 10, 10):
            block.draw(screen, game_state.grid_left, game_state.grid_top)
    

    # Show the turn of the current player in the right panel
    font = pygame.font.Font(None, 36)

    if current_player == "Angel":
        player_text = font.render("Current Player:", True, (123, 242, 242))
    else:
        player_text = font.render("Current Player:", True, (255, 0, 0))
    player_rect = player_text.get_rect(center=(game_state.GRID_AREA_WIDTH + 100, 50))
    screen.blit(player_text, player_rect)

    if current_player == "Angel":
        player_text = font.render("Angel", True, (123, 242, 242))
    else:
        player_text = font.render("Devil", True, (255, 0, 0))
    player_rect = player_text.get_rect(center=(game_state.GRID_AREA_WIDTH + 100, 75))
    screen.blit(player_text, player_rect)

    turn_text = font.render(f"Turn: {turn_number}", True, (0, 0, 0))
    turn_rect = turn_text.get_rect(center=(game_state.GRID_AREA_WIDTH + 100, 125))
    screen.blit(turn_text, turn_rect)

    coordinates_text = font.render(f"Looking at: ({game_state.grid_left + game_state.GRID_COLS // 2}, {game_state.grid_top + game_state.GRID_ROWS // 2})", True, (0, 0, 0))
    coordinates_rect = coordinates_text.get_rect(center=(game_state.GRID_AREA_WIDTH + 100, 275))
    screen.blit(coordinates_text, coordinates_rect)

    angel_coordinates_text = font.render(f"Angel At: ({game_state.angel_x}, {game_state.angel_y})", True, (0, 0, 0))
    angel_coordinates_rect = angel_coordinates_text.get_rect(center=(game_state.GRID_AREA_WIDTH + 100, 325))
    screen.blit(angel_coordinates_text, angel_coordinates_rect)

    last_block_coordinates_text = font.render(f"Last Block: {(game_state.blocks[-1].x,game_state.blocks[-1].y) if game_state.blocks else None}", True, (0, 0, 0))
    last_block_coordinates_rect = last_block_coordinates_text.get_rect(center=(game_state.GRID_AREA_WIDTH + 100, 375))
    screen.blit(last_block_coordinates_text, last_block_coordinates_rect)



    # Draw the undo and redo buttons
    game_state.undo_button.draw(screen)
    game_state.redo_button.draw(screen)

    pygame.display.update()
    clock.tick(60)

def moveGrid(game_state, key):
    match key:
        case pygame.K_w:
            game_state.grid_top -= 1
        case pygame.K_a:
            game_state.grid_left -= 1
        case pygame.K_s:
            game_state.grid_top += 1
        case pygame.K_d:
            game_state.grid_left += 1
    return game_state

def placeBlockedTile(game_state, mouse_x, mouse_y, blocked_tiles):
    grid_width = game_state.GRID_WIDTH
    grid_height = game_state.GRID_HEIGHT
    grid_offset_x = game_state.grid_left  # these are tile indices
    grid_offset_y = game_state.grid_top

    # Convert pixel click to an absolute tile coordinate
    tile_x = (mouse_x // grid_width) + grid_offset_x
    tile_y = (mouse_y // grid_height) + grid_offset_y

    # Check that the clicked tile falls within the visible grid (10x10)
    if (tile_x >= grid_offset_x and tile_x < grid_offset_x + 10 and
        tile_y >= grid_offset_y and tile_y < grid_offset_y + 10):
        
        # Check that no blocked tile already exists at this absolute coordinate
        if not any(block.x == tile_x and block.y == tile_y for block in blocked_tiles):
            # Also, prevent placing a block on the angel's position (absolute coordinates)
            if not (tile_x == game_state.angel_x and tile_y == game_state.angel_y):
                new_block = BlockedTile(tile_x, tile_y, grid_width, grid_height)
                blocked_tiles.append(new_block)
                game_state.add_block(new_block)
    return game_state, blocked_tiles

def checkLegalMove(game_state, tile_x, tile_y):
    # Convert the clicked relative coordinates into an absolute coordinate
    clicked_abs_x = tile_x + game_state.grid_left
    clicked_abs_y = tile_y + game_state.grid_top

    # Use the absolute angel position as stored in game_state
    angel_abs_x = game_state.angel_x
    angel_abs_y = game_state.angel_y

    # Assuming blocked_tiles are stored in absolute coordinates; if not, adjust similarly.
    blocked_tiles = game_state.blocks

    if (tile_x >= 0 and tile_x < 10 and tile_y >= 0 and tile_y < 10 and
        not any(block.x == clicked_abs_x and block.y == clicked_abs_y for block in blocked_tiles) and
        not (clicked_abs_x == angel_abs_x and clicked_abs_y == angel_abs_y) and
        clicked_abs_x >= angel_abs_x - game_state.angel_power and
        clicked_abs_x <= angel_abs_x + game_state.angel_power and
        clicked_abs_y >= angel_abs_y - game_state.angel_power and
        clicked_abs_y <= angel_abs_y + game_state.angel_power):
        print("legal move")
        return True

    return False
def checkWin(game_state):
    ax = game_state.angel_x  # angel's absolute x coordinate
    ay = game_state.angel_y  # angel's absolute y coordinate
    p = game_state.angel_power

    # Loop over every candidate tile in the angel's move range.
    # For each candidate (dx, dy) offset from the angel,
    # skip the angel's current position.
    for dx in range(-p, p + 1):
        for dy in range(-p, p + 1):
            if dx == 0 and dy == 0:
                continue  # skip the current position
            candidate_x = ax + dx
            candidate_y = ay + dy
            # Check the candidate is not blocked:
            blocked = any(block.x == candidate_x and block.y == candidate_y 
                          for block in game_state.blocks)
            if not blocked:
                # Found at least one legal move
                return False

    # If every candidate move is blocked, the angel is trapped.
    print("Angel is trapped! Devil wins!")
    return True

def clearScreen(screen,colour=(255, 255, 255)):
    screen.fill(colour)

def exitGame():
    pygame.quit()
    sys.exit()

if __name__=="__main__":
    main()
