# main.py

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
            pygame.draw.rect(screen, (255, 251, 0), rect)
        elif (self.x >= angel_x - angel_power and self.x <= angel_x + angel_power and
                self.y >= angel_y - angel_power and self.y <= angel_y + angel_power):
            pygame.draw.rect(screen, (123, 242, 242), rect)
        else:
            pygame.draw.rect(screen, (200, 200, 200), rect)

class BlockedTile(Clickable):

    def __init__(self, x, y, grid_tile_width, grid_tile_height):
        super().__init__(x, y, grid_tile_width, grid_tile_height)

    def is_on_grid(self, grid_left, grid_top, grid_height, grid_width):
        return (self.x >= grid_left and
                self.x <= grid_left + grid_width and
                self.y >= grid_top and
                self.y <= grid_top + grid_height)

    def draw(self, screen, grid_left, grid_top):
        block_x = grid_left + (self.x * self.width)
        block_y = grid_top - (self.y * self.height)
        pygame.draw.rect(screen, (125, 19, 19), (block_x, block_y, self.width, self.height))

class Button(Clickable):

    def __init__(self, x, y, width, height, text):
        super().__init__(x, y, width, height)
        self.text = text

    def draw(self, screen):
        pygame.draw.rect(screen, (85, 85, 85), (self.x-self.width // 2, self.y-self.height // 2, self.width, self.height))
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.x, self.y))
        screen.blit(text_surface, text_rect)

    def is_clicked(self, mouse_x, mouse_y):
        return (self.x - self.width // 2 <= mouse_x <= self.x + self.width // 2 and
                self.y - self.height // 2 <= mouse_y <= self.y + self.height // 2)

class GameState:

    def __init__(self):
        self.SCREEN_WIDTH = 600
        self.SCREEN_HEIGHT = 600
        self.GRID_WIDTH = self.SCREEN_WIDTH // 100
        self.GRID_HEIGHT = self.SCREEN_HEIGHT // 100
        self.grid_left = 0
        self.grid_top = 0
        self.screen = None
        self.clock = None
        self.angel_power = 1
        self.blocks = []
        self.angel_x = 0
        self.angel_y = 0

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
    pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(0,0, half_screen, SCREEN_HEIGHT))
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
        pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(0,0, half_screen, SCREEN_HEIGHT))
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

def gameloop(game_state):
    SCREEN_WIDTH = game_state.SCREEN_WIDTH
    SCREEN_HEIGHT = game_state.SCREEN_HEIGHT
    clock = game_state.clock
    screen = game_state.screen
    grid_width = game_state.GRID_WIDTH
    grid_height = game_state.GRID_HEIGHT
    grid_left = game_state.grid_left
    grid_top = game_state.grid_top
    angel_power = game_state.angel_power
    MOVE_KEYS = [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]
    player_turn = 0
    current_player = "Angel"
    blocked_tiles = []
    grid = []
    for i in range(10):
        grid.append([])
        for j in range(10):
            grid[i].append(Tile(i, j, grid_width, grid_height))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exitGame()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if current_player == "Devil":
                    game_state, blocked_tiles = placeBlockedTile(game_state, mouse_x, mouse_y, blocked_tiles)
                    current_player = "Angel"
                elif current_player == "Angel":
                    tile_x = (mouse_x - grid_left) // grid_width
                    tile_y = (mouse_y - grid_top) // grid_height
                    print("clicked:",tile_x, tile_y)
                    print("angel at:", game_state.angel_x, game_state.angel_y)
                    if checkLegalMove(game_state, tile_x, tile_y):
                        game_state.angel_x = tile_x + grid_left
                        game_state.angel_y = tile_y + grid_top 
                        current_player = "Devil"
            if event.type == pygame.KEYDOWN:
                if event.key in MOVE_KEYS:
                    game_state = moveGrid(game_state, event.key)
                    grid_left = game_state.grid_left
                    grid_top = game_state.grid_top

        renderGrid(screen, game_state, grid)

 

def renderGrid(screen, game_state, grid):
    clock = game_state.clock
    screen.fill((255, 255, 255))
    for i in range(10):
        for j in range(10):
            grid[i][j].draw(screen, game_state.grid_left - game_state.angel_x, game_state.grid_top - game_state.angel_y, game_state.angel_power)

    for block in game_state.blocks:
        block.draw(screen, game_state.grid_left, game_state.grid_top)
    
    pygame.display.update()
    clock.tick(60)

def moveGrid(game_state, key):
    if key == pygame.K_w:
        game_state.grid_top -= 1
    elif key == pygame.K_s:
        game_state.grid_top += 1
    elif key == pygame.K_a:
        game_state.grid_left -= 1
    elif key == pygame.K_d:
        game_state.grid_left += 1
    return game_state

def placeBlockedTile(game_state, mouse_x, mouse_y, blocked_tiles):
    grid_width = game_state.GRID_WIDTH
    grid_height = game_state.GRID_HEIGHT
    grid_left = game_state.grid_left
    grid_top = game_state.grid_top
    tile_x = (mouse_x - grid_left) // grid_width
    tile_y = (mouse_y - grid_top) // grid_height
    if (tile_x >= 0 and tile_x < 10 and tile_y >= 0 and tile_y < 10) and not(any(i.x == tile_x and i.y == tile_y for i in blocked_tiles)) and not(tile_x == game_state.angel_x - grid_left and tile_y == game_state.angel_y - grid_top):
        blocked_tiles.append(BlockedTile(tile_x, tile_y, grid_width // 10, grid_height // 10))
        game_state.add_block(blocked_tiles[-1])
    return game_state, blocked_tiles

def checkLegalMove(game_state, tile_x, tile_y):
    grid_left = game_state.grid_left
    grid_top = game_state.grid_top
    angel_x = game_state.angel_x
    angel_y = game_state.angel_y
    blocked_tiles = game_state.blocks
    if (tile_x >= 0 and tile_x < 10 and tile_y >= 0 and tile_y < 10) and not(any(i.x == tile_x and i.y == tile_y for i in blocked_tiles)) and not(tile_x == angel_x and tile_y == angel_y) and tile_x >= angel_x - game_state.angel_power and tile_x <= angel_x + game_state.angel_power and tile_y >= angel_y - game_state.angel_power and tile_y <= angel_y + game_state.angel_power:
        print("legal move")
        return True
    return False

def undoMove():
    pass

def redoMove():
    pass

def clearScreen(screen,colour=(255, 255, 255)):
    screen.fill(colour)

def exitGame():
    pygame.quit()
    sys.exit()

if __name__=="__main__":
    main()

