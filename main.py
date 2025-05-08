# main.py

import pygame


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

    def render_block(self, screen, grid_center_x, grid_center_y, grid_height, grid_width):
        block_width = grid_width // 10
        block_height = grid_height // 10
        block_x = grid_center_x - grid_width // 2 + (self.x * block_width)
        block_y = grid_center_y - grid_height // 2 + (self.y * block_height)
        pygame.draw.rect(screen, (125, 19, 19), (block_x, block_y, block_width, block_height))

class Button:

    def __init__(self, x, y, width, height, text):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
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

    def add_clock(self, clock):
        self.clock = clock

    def add_screen(self, screen):
        self.screen = screen



def Main():
    game_state = GameState()

    pygame.init()
    pygame.font.init()
    pygame.display.set_caption('Angel Problem')
    screen = pygame.display.set_mode((game_state.SCREEN_WIDTH, game_state.SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    game_state.add_screen(screen)
    game_state.add_clock(clock)

    end = StartScreen(game_state)
    print("End of StartScreen")

    while not end:
        Menu(game_state.screen)

    ExitGame()

def StartScreen(game_state):
    # Fill half of the screen with white and the other half with red
    SCREEN_WIDTH = game_state.SCREEN_WIDTH
    SCREEN_HEIGHT = game_state.SCREEN_HEIGHT
    clock = game_state.clock
    screen = game_state.screen
    screen.fill((255, 255, 255))
    half_screen = SCREEN_WIDTH // 2
    pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(0,0, half_screen, SCREEN_HEIGHT))
    startButton = Button(half_screen, SCREEN_HEIGHT // 2 - 25, 100, 50, "Start")
    start = False
    end = False
    while not start or not end:
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


def Menu(screen):
    screen.fill((0,0,0))

def Options():
    pass

def Gameloop():
    pass

def HandleInput():
    pass

def RenderGrid():
    pass

def MoveGrid():
    pass

def GetBlockedTiles():
    pass

def PlaceBlockedTile():
    pass

def FindLegalMoves():
    pass

def HighlightLegalMoves():
    pass

def CheckLegalMove():
    pass

def undoMove():
    pass

def redoMove():
    pass

def ClearScreen(screen):
    screen.fill((255, 255, 255))

def ExitGame():
    pygame.quit()

if __name__=="__main__":
    Main()

