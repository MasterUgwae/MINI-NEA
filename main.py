# main.py

# TODO: comments

import os
import warnings
import sys

# Disabling the warning messages associated with pygame
warnings.simplefilter("ignore", DeprecationWarning)
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
warnings.simplefilter("ignore", UserWarning)

import pygame

class Clickable:

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class Tile(Clickable):

    def __init__(self, x, y, grid_tile_width, grid_tile_height):
        # x, y are the tiles position on the grid
        super().__init__(x, y, grid_tile_width, grid_tile_height)
        try:
            self.angel_image = pygame.image.load(
                "Images/angel_image.png"
            ).convert_alpha()
        except FileNotFoundError:
            self.angel_image = pygame.Surface((512, 512))
            self.angel_image.fill((255, 255, 0))

    def draw(self, screen, angel_x, angel_y, angel_power):
        # Check if the tile is within the angel's range
        # if the tile is within the angel's range, draw it
        # Otherwise, draw it as gray
        rect = pygame.Rect(
            self.x * self.width, self.y * self.height, self.width, self.height
        )
        if self.x == angel_x and self.y == angel_y:
            pygame.draw.rect(screen, (255, 251, 0), rect, border_radius=5)
            scaled_image = pygame.transform.scale(
                self.angel_image, (self.width, self.height)
            )
            screen.blit(scaled_image, rect)
        elif (
            self.x >= angel_x - angel_power
            and self.x <= angel_x + angel_power
            and self.y >= angel_y - angel_power
            and self.y <= angel_y + angel_power
        ):
            pygame.draw.rect(screen, (123, 242, 242), rect, border_radius=5)
        else:
            pygame.draw.rect(screen, (200, 200, 200), rect, border_radius=5)


class BlockedTile(Clickable):

    def __init__(self, x, y, grid_tile_width, grid_tile_height):
        super().__init__(x, y, grid_tile_width, grid_tile_height)

    def is_on_grid(
        self, grid_left, grid_top, visible_tile_count_width, visible_tile_count_height
    ):
        # Check if the absolute tile coordinate lies within the visible grid
        return (
            self.x >= grid_left
            and self.x < grid_left + visible_tile_count_width
            and self.y >= grid_top
            and self.y < grid_top + visible_tile_count_height
        )

    def draw(self, screen, grid_left, grid_top):
        # Calculate the tile's position relative to the visible grid.
        visible_x = self.x - grid_left
        visible_y = self.y - grid_top
        block_x = visible_x * self.width
        block_y = visible_y * self.height
        pygame.draw.rect(
            screen,
            (125, 19, 19),
            (block_x, block_y, self.width, self.height),
            border_radius=5,
        )


class Button(Clickable):
    def __init__(
        self,
        x,
        y,
        width,
        height,
        text,
        base_color=(0, 153, 204),        hover_color=(0, 204, 255),        text_color=(255, 255, 255),        font_size=36,
    ):
        super().__init__(x, y, width, height)
        self.text = text
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font_size = font_size
        self.font = pygame.font.Font(None, font_size)
        self.is_pressed = False
        self.pressed_offset = 4  # The downward offset when pressed
        self.press_start_time = 0  # Track when the button was pressed
        self.press_duration = 100  # Duration in milliseconds

    def draw(self, screen, mouse_pos=None):
        # Check if we should stop showing the pressed state
        if (
            self.is_pressed
            and pygame.time.get_ticks() - self.press_start_time > self.press_duration
        ):
            self.is_pressed = False

        # Determine button color based on hover state.
        color = self.base_color
        if mouse_pos and self.is_hovered(mouse_pos):
            color = self.hover_color

        # Apply the pressed offset if active.
        y_offset = self.pressed_offset if self.is_pressed else 0
        x_offset = self.pressed_offset if self.is_pressed else 0

        # Define the button rectangle (centred at self.x, self.y)
        rect = pygame.Rect(
            self.x - self.width // 2 + x_offset,
            self.y - self.height // 2 + y_offset,
            self.width,
            self.height,
        )
        if not self.is_pressed:
            # Draw a drop shadow (slightly offset and darker)
            shadow_rect = rect.copy()
            shadow_rect.x += 3
            shadow_rect.y += 3
            pygame.draw.rect(screen, (30, 30, 30), shadow_rect, border_radius=8)

        # Draw the button itself (with rounded corners)
        pygame.draw.rect(screen, color, rect, border_radius=8)

        # Render the button text and centre it.
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(self.x, self.y + y_offset))
        screen.blit(text_surface, text_rect)

    def is_hovered(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        return (
            self.x - self.width // 2 <= mouse_x <= self.x + self.width // 2
            and self.y - self.height // 2 <= mouse_y <= self.y + self.height // 2
        )

    def is_clicked(self, mouse_x, mouse_y):
        return self.is_hovered((mouse_x, mouse_y))

    def animate_press(self):
        """
        Sets the is_pressed flag and records the time. The draw method will
        handle resetting the flag after the duration expires.
        """
        self.is_pressed = True
        self.press_start_time = pygame.time.get_ticks()


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
        # Define new screen dimensions: grid remains 600x600, side panel becomes 300 pixels wide.
        self.SCREEN_WIDTH = 900
        self.SCREEN_HEIGHT = 600

        self.GRID_AREA_WIDTH = 600
        self.GRID_AREA_HEIGHT = 600

        self.GRID_COLS = 12
        self.GRID_ROWS = 12
        self.tile_width = self.GRID_AREA_WIDTH // self.GRID_COLS
        self.tile_height = self.GRID_AREA_HEIGHT // self.GRID_ROWS

        # Offsets for grid view positioning.
        self.grid_left = 0
        self.grid_top = 0

        self.angel_power = 1
        self.angel_x = 0
        self.angel_y = 0

        self.blocks = []
        self.undo_stack = []
        self.redo_stack = []

        # UI buttons for undo and redo will be (re)assigned later.
        self.undo_button = None
        self.redo_button = None

    def add_clock(self, clock):
        self.clock = clock

    def add_screen(self, screen):
        self.screen = screen

    def add_block(self, block):
        self.blocks.append(block)


def main():

    pygame.init()
    pygame.font.init()
    pygame.display.set_caption("Angel Problem")
    try:
        icon = pygame.image.load("Images/angel_icon.png")
        pygame.display.set_icon(icon)
    except:
        pass
    game_state = GameState()
    screen = pygame.display.set_mode(
        (game_state.SCREEN_WIDTH, game_state.SCREEN_HEIGHT)
    )
    clock = pygame.time.Clock()

    game_state.add_screen(screen)
    game_state.add_clock(clock)

    end = startScreen(game_state)
    start = True
    while not end and start:
        start, end = menu(game_state)
        if start:
            game_state, start, end = gameloop(game_state)
    exitGame()


def startScreen(game_state):
    SCREEN_WIDTH = game_state.SCREEN_WIDTH
    SCREEN_HEIGHT = game_state.SCREEN_HEIGHT
    clock = game_state.clock
    screen = game_state.screen

    # Draw a gradient background.
    draw_gradient(
        screen, (30, 30, 80), (10, 10, 40), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
    )

    # Create a stylised title.
    title_font = pygame.font.Font(None, 100)
    title = title_font.render("Angel Problem", True, (250, 250, 250))
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))

    # Create Start button
    start_button = Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 200, 70, "Start")

    # Present credits for images used
    credits = pygame.font.Font(None, 16).render(
        "Credits: Iconka & sodiqmahmud46", True, (200, 200, 200)
    )
    credits_rect = credits.get_rect(bottomright=(SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10))

    loop = True
    while loop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.is_clicked(*event.pos):
                    loop = False

        mouse_pos = pygame.mouse.get_pos()
        # Redraw background on every frame to clear old frames.
        draw_gradient(
            screen, (30, 30, 80), (10, 10, 40), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        screen.blit(title, title_rect)
        start_button.draw(screen, mouse_pos)
        screen.blit(credits, credits_rect)
        pygame.display.update()
        clock.tick(60)

    return False


def menu(game_state):
    SCREEN_WIDTH = game_state.SCREEN_WIDTH
    SCREEN_HEIGHT = game_state.SCREEN_HEIGHT
    clock = game_state.clock
    screen = game_state.screen

    # Use the same gradient background.
    draw_gradient(
        screen, (30, 30, 80), (10, 10, 40), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
    )

    # Create a title for the menu.
    title_font = pygame.font.Font(None, 80)
    title = title_font.render("Main Menu", True, (250, 250, 250))
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))

    # Create menu buttons
    play_button = Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 25, 200, 70, "Play")
    options_button = Button(
        SCREEN_WIDTH // 2,
        SCREEN_HEIGHT // 2 + 50,
        200,
        70,
        "Options",
        base_color=(204, 102, 0),
        hover_color=(255, 128, 0),
    )
    exit_button = Button(
        SCREEN_WIDTH // 2,
        SCREEN_HEIGHT // 2 + 125,
        200,
        70,
        "Exit",
        base_color=(204, 0, 0),
        hover_color=(255, 51, 51),
    )

    loop = True
    start = False
    end = False
    while loop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                end = True
                loop = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if play_button.is_clicked(mouse_x, mouse_y):
                    start = True
                    loop = False
                elif options_button.is_clicked(mouse_x, mouse_y):
                    game_state = options(game_state)
                    # Redraw the menu when returning from options.
                elif exit_button.is_clicked(mouse_x, mouse_y):
                    end = True
                    loop = False

        mouse_pos = pygame.mouse.get_pos()
        # Refresh background and title.
        draw_gradient(
            screen, (30, 30, 80), (10, 10, 40), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        screen.blit(title, title_rect)
        play_button.draw(screen, mouse_pos)
        options_button.draw(screen, mouse_pos)
        exit_button.draw(screen, mouse_pos)

        pygame.display.update()
        clock.tick(60)

    return start, end


def draw_gradient(screen, start_color, end_color, rect):
    """Draw a vertical gradient inside the given rectangle."""
    x, y, width, height = rect
    for i in range(height):
        r = start_color[0] + (end_color[0] - start_color[0]) * i // height
        g = start_color[1] + (end_color[1] - start_color[1]) * i // height
        b = start_color[2] + (end_color[2] - start_color[2]) * i // height
        pygame.draw.line(screen, (r, g, b), (x, y + i), (x + width, y + i))


def options(game_state):
    SCREEN_WIDTH = game_state.SCREEN_WIDTH
    SCREEN_HEIGHT = game_state.SCREEN_HEIGHT
    clock = game_state.clock
    screen = game_state.screen
    angel_power = game_state.angel_power

    # Use a different gradient background.
    draw_gradient(
        screen, (60, 60, 120), (20, 20, 40), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
    )

    title_font = pygame.font.Font(None, 80)
    title = title_font.render("Options", True, (250, 250, 250))
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))

    # Create power control buttons
    up_button = Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, 200, 70, "Up")
    down_button = Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 130, 200, 70, "Down")
    back_button = Button(
        SCREEN_WIDTH // 2,
        SCREEN_HEIGHT // 2 + 210,
        200,
        70,
        "Save",
        base_color=(204, 0, 0),
        hover_color=(255, 51, 51),
    )

    loop = True
    while loop:
        # Redraw the background each frame.
        draw_gradient(
            screen, (60, 60, 120), (20, 20, 40), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        screen.blit(title, title_rect)

        # Display the current angel power.
        power_text = pygame.font.Font(None, 36).render(
            f"Angel Power: {angel_power}", True, (250, 250, 250)
        )
        power_text_rect = power_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30)
        )
        screen.blit(power_text, power_text_rect)

        mouse_pos = pygame.mouse.get_pos()
        up_button.draw(screen, mouse_pos)
        down_button.draw(screen, mouse_pos)
        back_button.draw(screen, mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                loop = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if up_button.is_clicked(mouse_x, mouse_y):
                    up_button.animate_press()
                    angel_power += 1
                    game_state.angel_power = angel_power
                elif down_button.is_clicked(mouse_x, mouse_y):
                    down_button.animate_press()
                    if angel_power > 1:
                        angel_power -= 1
                        game_state.angel_power = angel_power
                    else:
                        angel_power = 1
                elif back_button.is_clicked(mouse_x, mouse_y):
                    back_button.animate_press()
                    loop = False

        pygame.display.update()
        clock.tick(60)
    return game_state


# A helper to centre the grid view on a given input
def centre_grid_on_move(game_state, move_x, move_y):
    half_cols = game_state.GRID_COLS // 2
    half_rows = game_state.GRID_ROWS // 2
    game_state.grid_left = move_x - half_cols
    game_state.grid_top = move_y - half_rows


def placeBlockedTile(game_state, mouse_x, mouse_y):
    """
    Restored placeBlockedTile function that creates a new blocked tile
    at the clicked location if it's valid.
    Returns the updated game_state and whether a tile was placed.
    """
    grid_width = game_state.tile_width
    grid_height = game_state.tile_height

    # Convert pixel click to an absolute tile coordinate
    tile_x = (mouse_x // grid_width) + game_state.grid_left
    tile_y = (mouse_y // grid_height) + game_state.grid_top

    # Check that the clicked tile falls within the visible grid
    if (
        tile_x >= game_state.grid_left
        and tile_x < game_state.grid_left + game_state.GRID_COLS
        and tile_y >= game_state.grid_top
        and tile_y < game_state.grid_top + game_state.GRID_ROWS
    ):
        # Check that no blocked tile already exists at this absolute coordinate
        if not any(
            block.x == tile_x and block.y == tile_y for block in game_state.blocks
        ):
            # Also, prevent placing a block on the angel's position (absolute coordinates)
            if not (tile_x == game_state.angel_x and tile_y == game_state.angel_y):
                new_block = BlockedTile(tile_x, tile_y, grid_width, grid_height)
                game_state.blocks.append(new_block)
                return game_state, True, tile_x, tile_y

    return game_state, False, None, None


def gameloop(game_state):
    SCREEN_WIDTH = game_state.SCREEN_WIDTH
    SCREEN_HEIGHT = game_state.SCREEN_HEIGHT
    clock = game_state.clock
    screen = game_state.screen
    grid_width = game_state.tile_width
    grid_height = game_state.tile_height
    current_player = "Angel"
    turn_number = 1

    grid = [
        [Tile(row, col, grid_width, grid_height) for col in range(game_state.GRID_ROWS)]
        for row in range(game_state.GRID_COLS)
    ]

    # Compute side panel width and its centre x coordinate.
    side_panel_width = SCREEN_WIDTH - game_state.GRID_AREA_WIDTH
    ui_left_x = game_state.GRID_AREA_WIDTH + side_panel_width // 4
    ui_right_x = game_state.GRID_AREA_WIDTH + (3 * side_panel_width) // 4

    # Position control buttons in the side panel.
    undo_button = Button(ui_left_x, 350, 120, 50, "Undo", font_size=30)
    redo_button = Button(ui_right_x, 350, 120, 50, "Redo", font_size=30)
    angel_button = Button(ui_left_x, 450, 120, 70, "Goto Angel", font_size=30)
    block_button = Button(ui_right_x, 450, 120, 70, "Goto Block", font_size=30)
    menu_button = Button(
        ui_left_x, 550, 120, 70, "Menu", base_color=(100, 100, 100), font_size=30
    )
    exit_button = Button(
        ui_right_x,
        550,
        120,
        70,
        "Quit",
        base_color=(204, 0, 0),
        hover_color=(255, 51, 51),
        font_size=30,
    )

    # Update the references in game_state
    game_state.undo_button = undo_button
    game_state.redo_button = redo_button

    win = False
    while not win:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return game_state, False, True
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                # Check if click is in the side UI panel
                if mouse_x > game_state.GRID_AREA_WIDTH:
                    if undo_button.is_clicked(mouse_x, mouse_y):
                        undo_button.animate_press()
                        if game_state.undo_stack:
                            current_player = (
                                "Angel" if turn_number % 2 == 0 else "Devil"
                            )
                            turn_number -= 1
                        game_state = undoMove(game_state)

                    elif redo_button.is_clicked(mouse_x, mouse_y):
                        redo_button.animate_press()
                        if game_state.redo_stack:
                            current_player = (
                                "Angel" if turn_number % 2 == 0 else "Devil"
                            )
                            turn_number += 1
                        game_state = redoMove(game_state)
                    elif menu_button.is_clicked(mouse_x, mouse_y):
                        menu_button.animate_press()
                        game_state = GameState()
                        game_state.add_clock(clock)
                        game_state.add_screen(screen)
                        return game_state, True, False
                    elif exit_button.is_clicked(mouse_x, mouse_y):
                        exit_button.animate_press()
                        return game_state, False, True
                    elif angel_button.is_clicked(mouse_x, mouse_y):
                        angel_button.animate_press()
                        game_state.grid_left = (
                            game_state.angel_x - game_state.GRID_COLS // 2
                        )
                        game_state.grid_top = (
                            game_state.angel_y - game_state.GRID_ROWS // 2
                        )
                    elif block_button.is_clicked(mouse_x, mouse_y):
                        block_button.animate_press()
                        if game_state.blocks:
                            game_state.grid_left = (
                                game_state.blocks[-1].x - game_state.GRID_COLS // 2
                            )
                            game_state.grid_top = (
                                game_state.blocks[-1].y - game_state.GRID_ROWS // 2
                            )
                else:
                    # Process grid clicks for Angel and Devil moves.
                    if current_player == "Angel":
                        tile_x = (mouse_x // grid_width) + game_state.grid_left
                        tile_y = (mouse_y // grid_height) + game_state.grid_top
                        if checkLegalMove(
                            game_state,
                            tile_x - game_state.grid_left,
                            tile_y - game_state.grid_top,
                        ):
                            move = Move("angel", tile_x, tile_y)
                            game_state.undo_stack.append(move)
                            game_state.redo_stack.clear()
                            game_state.angel_x = tile_x
                            game_state.angel_y = tile_y
                            current_player = "Devil"
                            turn_number += 1
                    elif current_player == "Devil":
                        # Use the restored placeBlockedTile function
                        game_state, tile_placed, tile_x, tile_y = placeBlockedTile(
                            game_state, mouse_x, mouse_y
                        )
                        if tile_placed:
                            move = Move("block", tile_x, tile_y)
                            game_state.undo_stack.append(move)
                            game_state.redo_stack.clear()
                            current_player = "Angel"
                            turn_number += 1
                            if checkWin(game_state):
                                win = True
            if event.type == pygame.KEYDOWN:
                if event.key in [
                    pygame.K_w,
                    pygame.K_a,
                    pygame.K_s,
                    pygame.K_d,
                    pygame.K_LEFT,
                    pygame.K_RIGHT,
                    pygame.K_UP,
                    pygame.K_DOWN,
                ]:
                    game_state = moveGrid(game_state, event.key)
                elif event.key == pygame.K_u:
                    if game_state.undo_stack:
                        current_player = "Angel" if turn_number % 2 == 0 else "Devil"
                        turn_number -= 1
                    game_state = undoMove(game_state)
                elif event.key == pygame.K_r:
                    if game_state.redo_stack:
                        current_player = "Angel" if turn_number % 2 == 0 else "Devil"
                        turn_number += 1
                    game_state = redoMove(game_state)

        renderGrid(
            screen,
            game_state,
            grid,
            current_player,
            turn_number,
            menu_button,
            exit_button,
            angel_button,
            block_button,
        )

    # Display win screen for the Devil
    while True:
        clearScreen(screen, (200, 0, 0))
        font = pygame.font.Font(None, 74)
        win_text = font.render("Devil Wins!", True, (255, 255, 255))
        win_rect = win_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)
        )
        screen.blit(win_text, win_rect)
        back_button = Button(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 50,
            200,
            70,
            "Menu",
            base_color=(100, 100, 100),
        )
        back_button.draw(screen, pygame.mouse.get_pos())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return game_state, False, True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if back_button.is_clicked(mouse_x, mouse_y):
                    back_button.animate_press()
                    game_state = GameState()
                    game_state.add_screen(screen)
                    game_state.add_clock(clock)
                    return game_state, True, False
        pygame.display.update()
        clock.tick(60)


# The undoMove function undoes the last move
# and centres the grid
def undoMove(game_state):
    if not game_state.undo_stack:
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
            centre_grid_on_move(
                game_state, last_angel_move.tile_x, last_angel_move.tile_y
            )
        else:
            # Default state if no previous angel move.
            game_state.angel_x = 0
            game_state.angel_y = 0
            centre_grid_on_move(game_state, 0, 0)
    elif move.move_type == "block":
        # Remove the block that matches this move.
        game_state.blocks = [
            b
            for b in game_state.blocks
            if not (b.x == move.tile_x and b.y == move.tile_y)
        ]
        # centre on the most recent move in the undo stack.
        if game_state.undo_stack:
            last = game_state.undo_stack[-1]
            centre_grid_on_move(game_state, last.tile_x, last.tile_y)

    game_state.redo_stack.append(move)
    return game_state


def redoMove(game_state):
    if not game_state.redo_stack:
        return game_state

    move = game_state.redo_stack.pop()

    if move.move_type == "angel":
        game_state.angel_x = move.tile_x
        game_state.angel_y = move.tile_y
        centre_grid_on_move(game_state, move.tile_x, move.tile_y)
    elif move.move_type == "block":
        new_block = BlockedTile(
            move.tile_x, move.tile_y, game_state.tile_width, game_state.tile_height
        )
        game_state.blocks.append(new_block)
        centre_grid_on_move(game_state, move.tile_x, move.tile_y)

    game_state.undo_stack.append(move)
    return game_state


def renderGrid(
    screen,
    game_state,
    grid,
    current_player,
    turn_number,
    menu_button,
    exit_button,
    angel_button,
    block_button,
):
    clock = game_state.clock
    clearScreen(screen, (243, 243, 243))

    # Draw the grid.
    visible_angel_x = game_state.angel_x - game_state.grid_left
    visible_angel_y = game_state.angel_y - game_state.grid_top
    for row in range(game_state.GRID_ROWS):
        for col in range(game_state.GRID_COLS):
            grid[row][col].draw(
                screen, visible_angel_x, visible_angel_y, game_state.angel_power
            )
    for block in game_state.blocks:
        if block.is_on_grid(
            game_state.grid_left,
            game_state.grid_top,
            game_state.GRID_ROWS,
            game_state.GRID_COLS,
        ):
            block.draw(screen, game_state.grid_left, game_state.grid_top)

    side_panel_width = game_state.SCREEN_WIDTH - game_state.GRID_AREA_WIDTH
    ui_centre_x = game_state.GRID_AREA_WIDTH + side_panel_width // 2

    # Draw the turn and status information in the side panel.
    font = pygame.font.Font(None, 36)
    player_text = font.render(
        "Current Player:",
        True,
        (123, 242, 242) if current_player == "Angel" else (255, 0, 0),
    )
    player_rect = player_text.get_rect(center=(ui_centre_x, 20))
    screen.blit(player_text, player_rect)

    player_name = font.render(
        "Angel" if current_player == "Angel" else "Devil",
        True,
        (123, 242, 242) if current_player == "Angel" else (255, 0, 0),
    )
    name_rect = player_name.get_rect(center=(ui_centre_x, 50))
    screen.blit(player_name, name_rect)

    turn_text = font.render(f"Turn: {turn_number}", True, (0, 0, 0))
    turn_rect = turn_text.get_rect(center=(ui_centre_x, 90))
    screen.blit(turn_text, turn_rect)

    coordinates_text = font.render(
        f"Looking at: ({game_state.grid_left + game_state.GRID_COLS // 2}, {game_state.grid_top + game_state.GRID_ROWS // 2})",
        True,
        (0, 0, 0),
    )
    coordinates_rect = coordinates_text.get_rect(center=(ui_centre_x, 140))
    screen.blit(coordinates_text, coordinates_rect)

    angel_coordinates_text = font.render(
        f"Angel At: ({game_state.angel_x}, {game_state.angel_y})", True, (0, 0, 0)
    )
    angel_rect = angel_coordinates_text.get_rect(center=(ui_centre_x, 180))
    screen.blit(angel_coordinates_text, angel_rect)

    last_block_text = font.render(
        f"Last Block: {(game_state.blocks[-1].x, game_state.blocks[-1].y) if game_state.blocks else 'None'}",
        True,
        (0, 0, 0),
    )
    block_rect = last_block_text.get_rect(center=(ui_centre_x, 220))
    screen.blit(last_block_text, block_rect)

    # Draw all UI buttons (they already contain hover/press info).
    game_state.undo_button.draw(screen, pygame.mouse.get_pos())
    game_state.redo_button.draw(screen, pygame.mouse.get_pos())
    menu_button.draw(screen, pygame.mouse.get_pos())
    exit_button.draw(screen, pygame.mouse.get_pos())
    angel_button.draw(screen, pygame.mouse.get_pos())
    block_button.draw(screen, pygame.mouse.get_pos())

    pygame.display.update()
    clock.tick(60)


def moveGrid(game_state, key):
    match key:
        case pygame.K_w | pygame.K_UP:
            game_state.grid_top -= 1
        case pygame.K_a | pygame.K_LEFT:
            game_state.grid_left -= 1
        case pygame.K_s | pygame.K_DOWN:
            game_state.grid_top += 1
        case pygame.K_d | pygame.K_RIGHT:
            game_state.grid_left += 1
    return game_state


def checkLegalMove(game_state, tile_x, tile_y):
    # Convert the clicked relative coordinates into an absolute coordinate
    clicked_abs_x = tile_x + game_state.grid_left
    clicked_abs_y = tile_y + game_state.grid_top

    # Use the absolute angel position as stored in game_state
    angel_abs_x = game_state.angel_x
    angel_abs_y = game_state.angel_y

    # Assuming blocked_tiles are stored in absolute coordinates; if not, adjust similarly.
    blocked_tiles = game_state.blocks

    if (
        tile_x >= 0
        and tile_x < game_state.GRID_ROWS
        and tile_y >= 0
        and tile_y < game_state.GRID_COLS
        and not any(
            block.x == clicked_abs_x and block.y == clicked_abs_y
            for block in blocked_tiles
        )
        and not (clicked_abs_x == angel_abs_x and clicked_abs_y == angel_abs_y)
        and clicked_abs_x >= angel_abs_x - game_state.angel_power
        and clicked_abs_x <= angel_abs_x + game_state.angel_power
        and clicked_abs_y >= angel_abs_y - game_state.angel_power
        and clicked_abs_y <= angel_abs_y + game_state.angel_power
    ):
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
            blocked = any(
                block.x == candidate_x and block.y == candidate_y
                for block in game_state.blocks
            )
            if not blocked:
                # Found at least one legal move
                return False

    # If every candidate move is blocked, the angel is trapped.
    return True


def clearScreen(screen, colour=(255, 255, 255)):
    screen.fill(colour)


def exitGame():
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
