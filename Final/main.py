"""
This is a simple logic game.
The main goal as a player is to get to the exit.
"""

import pygame
import sys
import button


def display(entities, refresh):
    """
    Shows all entities and buttons while the level is opened.
    """
    WINDOW.fill((255, 180, 80))
    for i in range(len(entities)):
        for j in range(len(entities[i])):
            match entities[i][j]:
                case "X":
                    WINDOW.blit(BLOCK_IMAGE, (32 * j + 1, 32 * i + 1))
                case "Y":
                    WINDOW.blit(N_BLOCK_IMAGE, (32 * j + 1, 32 * i + 1))
                case "P":
                    WINDOW.blit(player_image, (32 * j + 1, 32 * i + 1))
                case "E":
                    WINDOW.blit(EXIT_IMAGE, (32 * j + 1, 32 * i + 1))
                case "S":
                    WINDOW.blit(SELECTED_IMAGE, (32 * j + 1, 32 * i + 1))
        WINDOW.blit(RESTART_IMAGE, (5, 5))
        WINDOW.blit(MENU_BUTTON_IMAGE, (480, 5))
    if refresh:
        pygame.display.update()


def reset(key, level, game_state_r):
    """
    Gives the functionality to "r" and "m"
    r - restarts the level
    m - goes back to main menu
    """
    if key == pygame.K_r:
        game_state_r = level_choice(level)
        return game_state_r, level
    if key == pygame.K_m:
        game_state_r.clear()
        level = menu()
        game_state_r = level_choice(level)
    if key == pygame.K_ESCAPE:
        sys.exit()
    return game_state_r, level


def movement(key, game_state_m):
    """
    Allow player to use arrow keys to move.
    The function does not move the player directly,
    but checks what user presses and redirects the input
    to corresponding function.
    """
    x_player, y_player = -1, -1
    for i in range(len(game_state_m)):
        for j in range(len(game_state_m[i])):
            if game_state_m[i][j] == "P":
                x_player, y_player = j, i
                break
    match key.key:
        case pygame.K_LEFT:
            if x_player > 0:
                game_state_m = to_left(game_state_m, x_player, y_player)
        case pygame.K_RIGHT:
            if x_player < len(game_state_m[y_player]) - 1:
                # player is able to go away from the screen if the level allows it
                game_state_m = to_right(game_state_m, x_player, y_player)
        case pygame.K_UP:
            if y_player > 0:
                game_state_m = to_up(game_state_m, x_player, y_player)
        case pygame.K_DOWN:
            # player is able to go as low as the level allows
            if y_player < len(game_state_m) - 1:
                game_state_m = to_down(game_state_m, x_player, y_player)
        case _:
            return game_state_m
    return game_state_m


def push(xb_from, yb_from, xb_to, yb_to, game_state_p, side):
    """
    First, puts given block into selected mode (highlighted in yellow),
    waits for user confirmation, if it gets the same key,
    on which the selected block exist - moves the block 1 unit away from the player.
    If the action is abandoned (different key press), returns previous state of the game.
    """
    block = game_state_p[yb_from][xb_from]
    game_state_p[yb_from][xb_from] = "S"
    confirmation = True
    while confirmation:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == side:
                    game_state_p[yb_from][xb_from] = "0"
                    for i in range(1, 4):
                        place = (xb_from * 32 - i * (xb_from-xb_to) * 32 /
                                 4, yb_from * 32 - i * (yb_from-yb_to) * 32 / 4)
                        display(game_state_p, False)
                        WINDOW.blit(SELECTED_IMAGE, place)
                        pygame.display.update()
                        pygame.time.wait(30)  # Limits the speed
                    game_state_p[yb_to][xb_to] = block
                else:
                    game_state_p[yb_from][xb_from] = block
                confirmation = False
        display(game_state_p, True)


def exterminate(xb_from, yb_from, xb_to, yb_to, game_state_ex, side):
    """
    First, puts 2 given blocks into selected mode (highlighted in yellow),
    waits for user confirmation, if it gets the same key,
    on which the selected blocks exist - removes them.
    If the action is abandoned (different key press), returns previous state of the game.
    """
    block1, block2 = game_state_ex[yb_from][xb_from], game_state_ex[yb_to][xb_to]
    game_state_ex[yb_from][xb_from] = "S"
    game_state_ex[yb_to][xb_to] = "S"
    display(game_state_ex, True)
    confirmation = True
    while confirmation:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == side:
                    game_state_ex[yb_from][xb_from] = "0"
                    game_state_ex[yb_to][xb_to] = "0"
                else:
                    game_state_ex[yb_from][xb_from] = block1
                    game_state_ex[yb_to][xb_to] = block2
                confirmation = False


def success(game_state_r):
    """
    Displays success screen,
    changes the game state to "success", to trigger main menu in main.
    """
    green = (0, 255, 4)
    font = pygame.font.Font('freesansbold.ttf', 70)
    text = font.render('Escaped!', True, green)
    text_rect = text.get_rect()
    text_rect.center = ARENA.center
    WINDOW.blit(text, text_rect)
    pygame.display.update()
    pygame.time.wait(2000)
    game_state_r[0][0] = 'success'
    return game_state_r


def to_left(game_state_l, p_x, p_y):
    """
    Checks what should happen after pressing 'a':
    rotation of the player, trigger success, moving player,
    player pushing block or nothing
    """
    global rotation, player_image
    if rotation == "right":
        player_image = PLAYER_IMAGE_LEFT
        rotation = "left"
    if game_state_l[p_y][p_x - 1] == "E":
        game_state_l = success(game_state_l)
        return game_state_l
    if game_state_l[p_y][p_x - 1] == "0":
        game_state_l[p_y][p_x] = "0"
        animation(p_x, p_y, p_x - 1, p_y, game_state_l)
        game_state_l[p_y][p_x - 1] = 'P'
    if p_x >= 2:
        if game_state_l[p_y][p_x - 1] in ["X", "Y"]:
            if game_state_l[p_y][p_x - 2] == "0":
                push(p_x - 1, p_y, p_x - 2, p_y, game_state_l, pygame.K_LEFT)
                return game_state_l
            if (game_state_l[p_y][p_x - 2] in ["X", "Y"])\
               and (game_state_l[p_y][p_x - 1] != game_state_l[p_y][p_x - 2]):
                exterminate(p_x - 1, p_y, p_x - 2, p_y, game_state_l, pygame.K_LEFT)
    return game_state_l


def to_right(game_state_r, p_x, p_y):
    """
    Checks what should happen after pressing 'd':
    rotation of the player, trigger success, moving player,
    player pushing block or nothing
    """
    global rotation, player_image
    if rotation == "left":
        player_image = PLAYER_IMAGE_RIGHT
        rotation = "right"
    if game_state_r[p_y][p_x + 1] == "E":
        game_state_r = success(game_state_r)
        return game_state_r
    if game_state_r[p_y][p_x + 1] == "0":
        game_state_r[p_y][p_x] = "0"
        animation(p_x, p_y, p_x + 1, p_y, game_state_r)
        game_state_r[p_y][p_x + 1] = "P"
    if p_x <= len(game_state_r[p_y]) - 3:
        if game_state_r[p_y][p_x + 1] in ["X", "Y"]:
            if game_state_r[p_y][p_x + 2] == "0":
                push(p_x + 1, p_y, p_x + 2, p_y, game_state_r, pygame.K_RIGHT)
                return game_state_r
            if (game_state_r[p_y][p_x + 2] in ["X", "Y"]) \
                    and (game_state_r[p_y][p_x + 1] != game_state_r[p_y][p_x + 2]):
                exterminate(p_x + 1, p_y, p_x + 2, p_y, game_state_r, pygame.K_RIGHT)
    return game_state_r


def to_up(game_state_up, p_x, p_y):
    """
    Checks what should happen after pressing 'w':
    trigger success, moving player,
    player pushing block or nothing
    """
    if game_state_up[p_y - 1][p_x] == "E":
        game_state_up = success(game_state_up)
        return game_state_up
    if game_state_up[p_y - 1][p_x] == "0":
        game_state_up[p_y][p_x] = "0"
        animation(p_x, p_y, p_x, p_y - 1, game_state_up)
        game_state_up[p_y - 1][p_x] = "P"
    if p_y >= 2:
        if game_state_up[p_y - 1][p_x] in ["X", "Y"]:
            if game_state_up[p_y - 2][p_x] == "0":
                push(p_x, p_y - 1, p_x, p_y - 2, game_state_up, pygame.K_UP)
                return game_state_up
            if (game_state_up[p_y - 2][p_x] in ["X", "Y"]) \
               and (game_state_up[p_y - 1][p_x] != game_state_up[p_y - 2][p_x]):
                exterminate(p_x, p_y - 1, p_x, p_y - 2, game_state_up, pygame.K_UP)
    return game_state_up


def to_down(game_state_d, p_x, p_y):
    """
    Checks what should happen after pressing 's':
    trigger success, moving player,
    player pushing block or nothing
    """
    if game_state_d[p_y + 1][p_x] == "E":
        game_state_d = success(game_state_d)
        return game_state_d
    if game_state_d[p_y + 1][p_x] == "0":
        game_state_d[p_y][p_x] = "0"
        animation(p_x, p_y, p_x, p_y + 1, game_state_d)
        game_state_d[p_y + 1][p_x] = "P"
    if p_y <= len(game_state_d) - 3:
        if game_state_d[p_y + 1][p_x] in ["X", "Y"]:
            if game_state_d[p_y + 2][p_x] == "0":
                push(p_x, p_y + 1, p_x, p_y + 2, game_state_d, pygame.K_DOWN)
                return game_state_d
            if (game_state_d[p_y + 2][p_x] in ["X", "Y"]) \
               and (game_state_d[p_y + 1][p_x] != game_state_d[p_y + 2][p_x]):
                exterminate(p_x, p_y + 1, p_x, p_y + 2, game_state_d, pygame.K_DOWN)
    return game_state_d


def animation(x_from, y_from, x_to, y_to, status_no_player):
    """
    Shows 4 frames with the player image moving between 2 places.
    """
    diff_x = (x_from - x_to) * 32
    diff_y = (y_from - y_to) * 32
    for i in range(1, 4):
        display(status_no_player, False)
        WINDOW.blit(player_image, (x_from * 32 - i * diff_x /
                                   4, y_from * 32 - i * diff_y / 4))
        pygame.display.update()
        pygame.time.wait(30)  # Limits the speed


def menu_display():
    """
    Displays explanations and name on main menu screen.
    """
    pygame.display.update()
    WINDOW.blit(BLOCK_IMAGE, (ARENA.left + 63, ARENA.centery - 150))
    WINDOW.blit(BLOCK_TEXT, (ARENA.left, ARENA.centery - 100))

    WINDOW.blit(N_BLOCK_IMAGE, (ARENA.right - 110, ARENA.centery - 150))
    WINDOW.blit(N_BLOCK_TEXT, (ARENA.right - 186, ARENA.centery - 100))

    WINDOW.blit(PLAYER_IMAGE_RIGHT, (ARENA.left + 63, ARENA.centery + 50))
    WINDOW.blit(PLAYER_TEXT, (ARENA.left + 15, ARENA.centery + 90))

    WINDOW.blit(EXIT_IMAGE, (ARENA.right - 110, ARENA.centery + 50))
    WINDOW.blit(EXIT_TEXT, (ARENA.right - 197, ARENA.centery + 90))

    WINDOW.blit(NAME, (ARENA.centerx - 123, ARENA.top))


def menu():
    """
    Displays buttons in main menu.
    Also checks and displays success stars nearby done levels.
    """
    done_levels = read_done()
    levels, keys = [], [pygame.K_1, pygame.K_2, pygame.K_3,
                        pygame.K_4, pygame.K_5, pygame.K_6,
                        pygame.K_7]
    WINDOW.fill((70, 130, 0))
    for i in range(7):
        levels.append(button.Button(ARENA.centerx - 59,
                                    100 + ARENA.top + 50 * i,
                                    LEVEL_IMAGES[i], 1))
    while True:
        menu_display()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
                if event.key in keys:
                    return keys.index(event.key) + 1
        for i in range(7):
            if done_levels[i] == 'success':
                WINDOW.blit(STAR, (ARENA.centerx - 90,
                                   ARENA.top + 100 + 50 * i))
            if levels[i].draw(WINDOW):
                return i + 1


def level_choice(number):
    """
    Loads chosen level game state from the corresponding file
    """
    gamestate = []
    match number:
        case 1:
            tutorial()
            file = open("lvl_1.txt", "r")
        case 2:
            file = open("lvl_2.txt", "r")
        case 3:
            file = open("lvl_3.txt", "r")
        case 4:
            file = open("lvl_4.txt", "r")
        case 5:
            file = open("lvl_5.txt", "r")
        case 6:
            file = open("lvl_6.txt", "r")
        case 7:
            file = open("lvl_7.txt", "r")
        case _:
            file = open("lvl_1.txt", "r")
    rows = file.readlines()
    for row in rows:
        row = row.rstrip()
        elements = row.split(" ")
        gamestate.append(elements)
    file.close()
    return gamestate


def mouse_reset(game_state_m, level):
    """
    Allows user to restart the level or go back to main menu
    with buttons (R and M) on the screen.
    """
    if RESTART.draw(WINDOW):
        game_state_m, level = reset(pygame.K_r, level, game_state_m)
    if MAIN_MENU.draw(WINDOW):
        game_state_m, level = reset(pygame.K_m, level, game_state_m)
    return game_state_m, level


def read_done():
    """
    Checks from the file which levels are already done.
    Returns a list with them.
    """
    done = []
    file = open("done_levels.txt", "r")
    rows = file.readlines()
    for row in rows:
        row = row.rstrip()
        done.append(row)
    file.close()
    return done


def write_done(done):
    """
    Writes into the file which levels have been completed.
    """
    file = open("done_levels.txt", "w")
    for item in done:
        file.write(f"{item}\n")
    file.close()


def tutorial():
    """
    Shows basic concepts of the game before level 1.
    Pressing anything continues to the level.
    """
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                return
        WINDOW.blit(TUTORIAL_IMAGE, (0, 0))
        pygame.display.update()


def main():
    """
    Main game loop.
    """
    done = read_done()
    level = menu()
    game_state = level_choice(level)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                game_state = movement(event, game_state)
                if game_state[0][0] == 'success':
                    done[level - 1] = 'success'
                    write_done(done)
                    level = menu()
                    game_state = level_choice(level)
                game_state, level = reset(event.key, level, game_state)
        display(game_state, True)
        game_state, level = mouse_reset(game_state, level)
        fpsClock.tick(30)
    pygame.quit()


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("FizGame")
    WINDOW = pygame.display.set_mode((512, 512))
    ARENA = WINDOW.get_rect()
    BLOCK_IMAGE = pygame.image.load('block_placeholder.png')
    BLOCK_TEXT = pygame.image.load('block_text1.png')
    N_BLOCK_IMAGE = pygame.image.load('n_block_placeholder.png')
    N_BLOCK_TEXT = pygame.image.load('Nblock_text1.png')
    SELECTED_IMAGE = pygame.image.load('selected_block_placeholder.png')
    PLAYER_IMAGE_RIGHT = pygame.image.load('player.png')
    PLAYER_IMAGE_LEFT = pygame.image.load('player_left.png')
    PLAYER_TEXT = pygame.image.load('player_text2.png')
    RESTART_IMAGE = pygame.image.load('Restart.png')
    MENU_BUTTON_IMAGE = pygame.image.load('Menu.png')
    TUTORIAL_IMAGE = pygame.image.load('tutorial.png')
    LEVEL_IMAGES = [pygame.image.load('level_1.png'),
                    pygame.image.load('level_2.png'),
                    pygame.image.load('level_3.png'),
                    pygame.image.load('level_4.png'),
                    pygame.image.load('level_5.png'),
                    pygame.image.load('level_6.png'),
                    pygame.image.load('level_7.png')]
    STAR = pygame.image.load('star.png')
    NAME = pygame.image.load('fiz.png')
    player_image = PLAYER_IMAGE_RIGHT
    rotation = "right"
    RESTART = button.Button(5, 5, RESTART_IMAGE, 1)
    MAIN_MENU = button.Button(480, 5, MENU_BUTTON_IMAGE, 1)
    EXIT_IMAGE = pygame.image.load('Exit.png')
    EXIT_TEXT = pygame.image.load('Exit_text2.png')
    fpsClock = pygame.time.Clock()
    main()
