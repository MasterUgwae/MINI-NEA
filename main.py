# main.py

import os
import sys

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'



import pygame


class Clickable:


    def __init__(self, x, y, width, height):
        self.x = y
        self.y = y
        self.width = width
        self.height = height

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, self.width, self.height))

class Tile(Clickable):

    def __init__(self, x, y, grid_tile_width, grid_tile_height):
        #x, y are the tiles position on the grid and not the screen
        super().__init__(x, y, grid_tile_width, grid_tile_height)
    
    def draw(self, screen, angel_x, angel_y, angel_power ):
        ## Check if the tile is within the angel's range
        ## if the tile is within the angel's range, draw it
        ## Otherwise, draw it as gray
        top = self.y - self.height // 2
        left = self.x - self.width // 2
        rect = pygame.Rect(left, top, self.width, self.height)
        if (self.x >= angel_x - angel_power and self.x <= angel_x + angel_power and
                self.y >= angel_y - angel_power and self.y <= angel_y + angel_power):
            pygame.draw.rect(screen, (123, 242, 242), rect)
        else:
            pygame.draw.rect(screen, (200, 200, 200), rect)


class Block:

    def __init__(self) -> None:
        self.x = 0
        self.y = 0
        self.turn_placed = 0

    def is_on_grid(self, grid_center_x, grid_center_y, grid_height, grid_width):
        return (self.x >= grid_center_x - grid_width // 2 and
                self.x <= grid_center_x + grid_width // 2 and
                self.y >= grid_center_y - grid_height // 2 and
                self.y <= grid_center_y + grid_height // 2)

    def draw(self, screen, grid_center_x, grid_center_y, grid_height, grid_width):
        block_width = grid_width // 10
        block_height = grid_height // 10
        block_x = grid_center_x - grid_width // 2 + (self.x * block_width)
        block_y = grid_center_y - grid_height // 2 + (self.y * block_height)
        pygame.draw.rect(screen, (125, 19, 19), (block_x, block_y, block_width, block_height))

class Button(Clickable):

    def __init__(self, x, y, width, height, text,option):
        super().__init__(x, y, width, height)
        self.text = text

    def draw(self, screen):
        pygame.draw.rect(screen, (85, 85, 85), (self.x-self.width // 2, self.y-self.height // 2, self.width, self.height))
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.x, self.y))
        screen.blit(text_surface, text_rect)


class GameState:

    def __init__(self):
        self.SCREEN_WIDTH = 600
        self.SCREEN_HEIGHT = 600
        self.GRID_WIDTH = self.SCREEN_WIDTH // 100
        self.GRID_HEIGHT = self.SCREEN_HEIGHT // 100
        self.grid_centre_x = 0
        self.grid_centre_y = 0
        self.screen = None
        self.clock = None
        self.angel_power = 1
        self.blocks = []

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

    while not end:
        start, end = menu(game_state)
        if start:

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
                if (startButton.x <= mouse_x <= startButton.x + startButton.width and
                        startButton.y <= mouse_y <= startButton.y + startButton.height):
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
                if (play_button.x <= mouse_x <= play_button.x + play_button.width and
                    play_button.y <= mouse_y <= play_button.y + play_button.height):
                    start = True
                elif (options_button.x <= mouse_x <= options_button.x + options_button.width and
                        options_button.y <= mouse_y <= options_button.y + options_button.height):
                    options()
                elif (exit_button.x <= mouse_x <= exit_button.x + exit_button.width and
                        exit_button.y <= mouse_y <= exit_button.y + exit_button.height):
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


def gameloop():
    pass

def handleInput():
    pass

def renderGrid():
    pass

def moveGrid():
    pass

def getBlockedTiles():
    pass

def placeBlockedTile():
    pass

def findLegalMoves():
    pass

def highlightLegalMoves():
    pass

def checkLegalMove():
    pass

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

