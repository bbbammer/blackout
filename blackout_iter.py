# -*- coding: utf-8 -*-
"""
Created on Sun Oct 31 08:45:27 2021

@author: bamme
"""
import numpy as np
import random
import pygame
import sys
import shelve

pygame.init()
pygame.mixer.init()
window = pygame.display.set_mode((1200, 800))
# # The window is an object that pygame works with to create a display. There is a pygame website # with a lot more
# explanation on the specific attributes, but you will see window pop up a lot, # its just a variable representing the
# screen. Also (x,y) -> (0,0) is from the top left so (1200,800) is the bottom right if you draw a 100 pixel square
# at (450,450) then that is the location of the top left corner of the square and so the top right corner will be at
# (550, 450) bottom left (450,550) and bottom right (550,550)

button_sound = pygame.mixer.Sound('resources\\button_click.wav')
num_click_sound = pygame.mixer.Sound('resources\\num_click.wav')
pass_level_sound = pygame.mixer.Sound('resources\\pass_level.wav')
incorrect_selection = pygame.mixer.Sound('resources\\incorrect.wav')
intro = pygame.mixer.Sound('resources\\intro.wav')

pygame.display.set_caption("Blackout")

FONT = 'resources\\retro_font.ttf'

''' The main() function is at the very end and starts the process by calling title screen animation.
then title_screen() calls puzzle_screen with a number representing the level to generate. 

event_handling() only job is to wait for input, this is the only while loop in the whole program, in hope to avoid 
nested loops puzzle_screen() draws everything and then calls make_selections() which takes mouse coordinates from 
even_handling() and selects an action. 

When you select an operation, say row swap, the program finds the string 'row' in the action_to_take 

dictionary which returns essentially a function call that takes in the current matrices and level as parameters. 
Since 01 == 1 and 00 == 0 but we need 01 or 00 to represent a entry of the matrix, strings are used sometimes instead 
of ints. This is also helpful since they can be indexed like lists. 

NOTE: There is one bug I can't diagnose. Occasionally the pygame window closes without an error report however the 
script stays running. Haven't got a clue why... 

In the title_screen function, puzzle_screen is called, there you can select which level the game starts on when its run.


'''


def title_screen_animation():
    intro.play()
    for i in range(500):
        pygame.draw.rect(window, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
                         pygame.Rect(random.randint(0, 1200), 0, random.randint(0, 48), 800))
        pygame.draw.rect(window, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
                         pygame.Rect(0, random.randint(0, 800), 1200, random.randint(0, 48)))
    pygame.display.update()

    for j in range(800):
        pygame.draw.rect(window, (0, 0, 0), pygame.Rect(random.randint(0, 1200), 0, 8, 800))
        pygame.draw.rect(window, (0, 0, 0), pygame.Rect(0, random.randint(0, 800), 1200, 8))
        pygame.display.update()

    title_screen()


def title_screen():
    window.fill((0, 0, 0))
    start_button = pygame.Rect(200, 200, 800, 400)
    pygame.draw.rect(window, (0, 0, 0), start_button)
    draw_text("B L A C K O U T", pygame.font.Font(FONT, 100),
              (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), window, 150, 350)
    pygame.display.update()
    total_score = 0
    shelfFile = shelve.open('resources\\blackout_save')
    if 'level' in shelfFile:
        level = shelfFile['level']
    else:
        level = 1
    shelfFile.close()

    xpos, ypos = event_handling()

    if start_button.collidepoint(xpos, ypos):
        puzzle_screen(level)
    else:
        title_screen()


def puzzle_screen(level):


    current_matrix = begin_matrix_num(level)
    current_color_matrix = begin_matrix_color(level)
    selection_list = []
    matrix_hist = []
    matrix_color_hist = []
    score = 0
    background = True
    view_sol = False

    control = True
    while control:
        if background:
            for i in range(1200):
                pygame.draw.rect(window, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
                                 pygame.Rect(random.randint(0, 1200), 0, random.randint(0, 48), 800))
                pygame.draw.rect(window, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
                                 pygame.Rect(0, random.randint(0, 800), 1200, random.randint(0, 48)))
            background = False

        pygame.draw.rect(window, (0, 0, 0), pygame.Rect(0, 0, 1200, 15))
        pygame.draw.rect(window, (0, 0, 0), pygame.Rect(1185, 0, 15, 800))
        pygame.draw.rect(window, (0, 0, 0), pygame.Rect(0, 0, 15, 800))
        pygame.draw.rect(window, (0, 0, 0), pygame.Rect(0, 780, 1200, 20))
        pygame.draw.rect(window, (0, 0, 0), pygame.Rect(300, 0, 750, 50))
        pygame.draw.rect(window, (0, 0, 0), pygame.Rect(300, 100, 800, 600))

        # take the current matrix and using its dimensions, some iterables are returned which we can use to draw the
        # game screen

        matrix_to_draw = button_dict(len(current_matrix))

        buttons_to_draw, action_to_take = button_dict('puzzle')

        selections_to_draw = selection_dict(len(current_matrix))

        text_to_draw = text_list('puzzle', level)

        nums_to_draw = num_text_list(current_matrix, current_color_matrix)

        for i in buttons_to_draw:
            pygame.draw.rect(window, (0, 0, 0), buttons_to_draw[i])

        for i in range(len(text_to_draw)):
            draw_text(text_to_draw[i][0], text_to_draw[i][1], text_to_draw[i][2], text_to_draw[i][3],
                      text_to_draw[i][4], text_to_draw[i][5])

        for g in matrix_to_draw:
            pygame.draw.rect(window, (current_color_matrix[int(g[0])][int(g[1])][0],
                                      current_color_matrix[int(g[0])][int(g[1])][1],
                                      current_color_matrix[int(g[0])][int(g[1])][2]),
                             matrix_to_draw[g])

        for v in range(len(selection_list)):
            pygame.draw.rect(window, (current_color_matrix[int(selection_list[v][0])][int(selection_list[v][1])][0],
                                      current_color_matrix[int(selection_list[v][0])][int(selection_list[v][1])][1],
                                      current_color_matrix[int(selection_list[v][0])][int(selection_list[v][1])][2]),
                             selections_to_draw[selection_list[v]])

        for p in range(len(nums_to_draw)):
            for k in range(len(nums_to_draw)):
                draw_text(nums_to_draw[p][k][0], nums_to_draw[p][k][1], nums_to_draw[p][k][2], nums_to_draw[p][k][3],
                          nums_to_draw[p][k][4], nums_to_draw[p][k][5])

        pygame.display.update()

        # after telling pygame to draw everything to the screen, pygame.display.update() refreshes the screen event
        # handling is a while loop just waiting for a click, when input is received it returns the x and y
        # coordinates of the click Next the first for loop iterates over the buttons corresponding to the elements of
        # the matrix The second for loop iterates over the various buttons on the screen, most resulting in function
        # calls. the action_to_take dictionary is interesting since it returns a different function call for each key

        xpos, ypos = event_handling()

        for j in matrix_to_draw:
            if not view_sol:
                if matrix_to_draw[j].collidepoint(xpos, ypos):
                    if (current_color_matrix[int(j[0])][int(j[1])][0] > 0) or (
                            current_color_matrix[int(j[0])][int(j[1])][1] > 0) or (
                            current_color_matrix[int(j[0])][int(j[1])][2] > 0):
                        num_click_sound.play()
                        if j in selection_list:
                            selection_list.remove(j)
                        else:
                            selection_list.append(j)

        for k in buttons_to_draw:
            if buttons_to_draw[k].collidepoint(xpos, ypos):
                if k == 'view_sol':
                    button_sound.play()
                    view_sol = not view_sol
                    if view_sol:
                        if matrix_hist == []:
                            matrix_hist.append(current_matrix)
                            matrix_color_hist.append(current_color_matrix)
                        elif not np.array_equal(matrix_color_hist[-1], current_color_matrix):
                            matrix_hist.append(current_matrix)
                            matrix_color_hist.append(current_color_matrix)
                        current_matrix = end_matrix_num(level)
                        current_color_matrix = end_matrix_color(level)
                    else:
                        if matrix_hist == []:
                            current_matrix = begin_matrix_num(level)
                            current_color_matrix = begin_matrix_color(level)
                        else:
                            current_matrix = matrix_hist[-1]
                            current_color_matrix = matrix_color_hist[-1]
                            del matrix_hist[-1]
                            del matrix_color_hist[-1]

                elif k == 'help':
                    button_sound.play()
                    font = pygame.font.Font(FONT, 15)
                    go_back = pygame.Rect(0, 0, 1200, 800)
                    pygame.draw.rect(window, (0, 0, 0), go_back)
                    pygame.display.update()
                    xpos, ypos = event_handling()
                    view = True
                    while view:
                        if go_back.collidepoint(xpos, ypos):
                            view = False
                    background = True

                elif k == 'level_screen' and not view_sol:
                    button_sound.play()
                    level, background = level_screen()
                    matrix_hist.clear()
                    matrix_color_hist.clear()
                    selection_list.clear()
                    current_matrix = begin_matrix_num(level)
                    current_color_matrix = begin_matrix_color(level)

                elif k == 'clear' and not view_sol:
                    button_sound.play()
                    selection_list.clear()
                    current_matrix = begin_matrix_num(level)
                    current_color_matrix = begin_matrix_color(level)

                elif k == 'undo' and not view_sol:
                    button_sound.play()
                    if selection_list == []:
                        if matrix_hist == []:
                            current_matrix = np.copy(begin_matrix_num(level))
                            current_color_matrix = np.copy(begin_matrix_color(level))
                            matrix_hist.clear()
                            matrix_color_hist.clear()
                        elif len(matrix_hist) >= 1:
                            back_mat = matrix_hist[-1]
                            back_mat_color = matrix_color_hist[-1]
                            del matrix_hist[-1]
                            del matrix_color_hist[-1]
                            current_matrix = back_mat
                            current_color_matrix = back_mat_color
                    else:
                        selection_list.clear()

                elif ((k == 'add') or (k == 'slide') or (k == 'row') or (k == 'column')) and not view_sol:
                    button_sound.play()
                    new_mat, new_col_mat = action_to_take[k](selection_list, current_matrix, current_color_matrix, level)

                    if not np.array_equal(new_col_mat, current_color_matrix):
                        score += 1
                        matrix_hist.append(current_matrix)
                        matrix_color_hist.append(current_color_matrix)

                        if (np.array_equal(new_mat, end_matrix_num(level))) and (np.array_equal(new_col_mat, end_matrix_color(level))):
                            pass_level_sound.play()
                            level += 1
                            shelfFile = shelve.open('resources\\blackout_save')
                            shelfFile['level'] = level
                            shelfFile.close()
                            if level == 51:
                                control = False
                                pygame.draw.rect(window, (0, 0, 0), pygame.Rect(0, 0, 1200, 800))
                                draw_text("YOU WIN", pygame.font.Font(FONT, 80),
                                        (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),window, 175, 350)
                                pygame.display.update()
                                pygame.quit()
                                sys.exit()
                            for j in range(600):
                                pygame.draw.rect(window, (0, 0, 0), pygame.Rect(random.randint(0, 1200), 0, 12, 800))
                                pygame.draw.rect(window, (0, 0, 0), pygame.Rect(0, random.randint(0, 800), 1200, 12))
                                pygame.display.update()

                            next_screen = pygame.Rect(0, 0, 1200, 800)
                            pygame.draw.rect(window, (0, 0, 0), next_screen)
                            draw_text("LEVEL COMPLETE", pygame.font.Font(FONT, 80),
                                (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), window,175, 350)
                            pygame.display.update()
                            xpos, ypos = event_handling()
                            complete_screen = True
                            while complete_screen:
                                if next_screen.collidepoint(xpos, ypos):
                                    complete_screen = False
                            selection_list.clear()
                            matrix_hist.clear()
                            matrix_color_hist.clear()
                            background = True
                    selection_list.clear()
                    current_matrix = new_mat
                    current_color_matrix = new_col_mat
                    if background:
                        current_matrix = begin_matrix_num(level)
                        current_color_matrix = begin_matrix_color(level)


def level_screen():

    shelfFile = shelve.open('resources\\blackout_save')
    if 'level' in shelfFile:
        level = shelfFile['level']
    else:
        level = 1
    shelfFile.close()

    for i in range(1200):
        pygame.draw.rect(window, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
                         pygame.Rect(random.randint(0, 1200), 0, random.randint(0, 48), 800))
        pygame.draw.rect(window, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
                         pygame.Rect(0, random.randint(0, 800), 1200, random.randint(0, 48)))
    pygame.draw.rect(window, (0, 0, 0), pygame.Rect(0, 0, 1200, 15))
    pygame.draw.rect(window, (0, 0, 0), pygame.Rect(1185, 0, 15, 800))
    pygame.draw.rect(window, (0, 0, 0), pygame.Rect(0, 0, 15, 800))
    pygame.draw.rect(window, (0, 0, 0), pygame.Rect(0, 780, 1200, 20))
    pygame.draw.rect(window, (0, 0, 0), pygame.Rect(300, 100, 800, 600))
    pygame.draw.rect(window, (0, 0, 0), pygame.Rect(50, 50, 1100,700))

    levels_to_draw, nums_to_draw = button_dict('level')

    wait = True
    while wait:
            for i in levels_to_draw:
                if i < level:
                    pygame.draw.rect(window, (255, 255, 255), levels_to_draw[i])
                elif i == level:
                    pygame.draw.rect(window, (0, 255, 0), levels_to_draw[i])
                else:
                    pygame.draw.rect(window, (0, 0, 0), levels_to_draw[i])
            for p in range(5):
                for k in range(5):
                    if int(nums_to_draw[p][k][0]) <= level:
                        draw_text(nums_to_draw[p][k][0], nums_to_draw[p][k][1], nums_to_draw[p][k][2],
                                  nums_to_draw[p][k][3],
                                  nums_to_draw[p][k][4], nums_to_draw[p][k][5])
                    else:
                        draw_text(nums_to_draw[p][k][0], nums_to_draw[p][k][1], (255, 255, 255), nums_to_draw[p][k][3],
                                  nums_to_draw[p][k][4], nums_to_draw[p][k][5])

            pygame.display.update()
            xpos, ypos = event_handling()

            for l in levels_to_draw:
                if levels_to_draw[l].collidepoint(xpos,ypos):
                    if l <= level:
                        wait = False
                        background = True
                        return l, background
                        break

# The next 4 functions are performing the operations on the matrix, at the beginning of each function there is
# some testing if the squares selected are valid for that operation, if not then the current matrices are returned.

def addition(val_list, current_matrix, current_color_matrix, level):

    if len(val_list) == 1:
        val_list.append(val_list[0])

    if (len(val_list) % 2 != 0) or (len(val_list) == 0):
        incorrect_selection.play()
        return current_matrix, current_color_matrix

    inc_val = color_jump(level)
    new_color_matrix: ndarray = np.copy(current_color_matrix)
    new_matrix: ndarray = np.copy(current_matrix)

    for k in range(int(len(val_list) / 2)):

        if new_color_matrix[int(val_list[(2 * k) + 1][0])][int(val_list[(2 * k) + 1][1])][1] > 0:

            new_matrix[int(val_list[(2 * k) + 1][0])][int(val_list[(2 * k) + 1][1])] = \
                new_matrix[int(val_list[(2 * k) + 1][0])][int(val_list[(2 * k) + 1][1])] + \
                new_matrix[int(val_list[2 * k][0])][int(val_list[2 * k][1])]

            green_val = new_color_matrix[int(val_list[(2 * k) + 1][0])][int(val_list[(2 * k) + 1][1])][1] - inc_val
            if green_val < inc_val:
                green_val = 0

            new_color_matrix[int(val_list[(2 * k) + 1][0])][int(val_list[(2 * k) + 1][1])][1] = green_val

    return new_matrix, new_color_matrix


def slide(val_ind, current_matrix, current_color_matrix, level):
    rem_list = []
    for i in range(len(val_ind)):
        if current_color_matrix[int(val_ind[i][0])][int(val_ind[i][1])][2] > 0:
            rem_list.append(val_ind[i])
    val_ind = rem_list.copy()
    if len(val_ind) == 0:
        incorrect_selection.play()
        return current_matrix, current_color_matrix

    inc_val = color_jump(level)
    new_color_matrix: ndarray = np.copy(current_color_matrix)
    new_matrix: ndarray = np.copy(current_matrix)

    for i in range(len(val_ind)):
        new_matrix[int(val_ind[i][0])][int(val_ind[i][1])] = current_matrix[int(val_ind[i - 1][0])][
                                                                 int(val_ind[i - 1][1])] - 1
        blue_val = new_color_matrix[int(val_ind[i][0])][int(val_ind[i][1])][2] - inc_val
        if blue_val < inc_val:
            blue_val = 0
        new_color_matrix[int(val_ind[i][0])][int(val_ind[i][1])][2] = blue_val

    return new_matrix, new_color_matrix


def row(selection_list, current_matrix, current_color_matrix, level):
    inc_val = color_jump(level)
    new_color_matrix = np.copy(current_color_matrix)
    ret_color_matrix = np.copy(current_color_matrix)
    new_matrix = np.copy(current_matrix)
    duplicate = np.copy(current_matrix)

    if (len(selection_list) > 2) or (len(selection_list) < 1):
        incorrect_selection.play()
        return current_matrix, current_color_matrix
    if len(selection_list) == 1:
        row_1 = int(selection_list[0][0])
        row_2 = int(selection_list[0][0])
    else:
        row_1 = int(selection_list[0][0])
        row_2 = int(selection_list[1][0])

    for i in range(len(new_matrix[row_1])):
        if (current_color_matrix[row_2][i][0] > 0) and (current_color_matrix[row_1][i][0] > 0):
            new_matrix[row_2][i] = duplicate[row_1][i] + 1
            new_matrix[row_1][i] = duplicate[row_2][i] + 1
            red_val = new_color_matrix[row_2][i][0] - inc_val
            red_val1 = new_color_matrix[row_1][i][0] - inc_val
            if red_val < inc_val:
                red_val = 0
            if red_val1 < inc_val:
                red_val1 = 0
            ret_color_matrix[row_2][i][0] = red_val
            ret_color_matrix[row_1][i][0] = red_val1

    return new_matrix, ret_color_matrix


def column(selection_list, current_matrix, current_color_matrix, level):
    inc_val = color_jump(level)
    new_color_matrix = np.copy(current_color_matrix)
    ret_color_matrix = np.copy(current_color_matrix)
    new_matrix = np.copy(current_matrix)
    duplicate = np.copy(current_matrix)

    if (len(selection_list) > 2) or (len(selection_list) < 1):
        incorrect_selection.play()
        return current_matrix, current_color_matrix
    if len(selection_list) == 1:
        col_1 = int(selection_list[0][1])
        col_2 = int(selection_list[0][1])
    else:
        col_1 = int(selection_list[0][1])
        col_2 = int(selection_list[1][1])

    for i in range(len(new_matrix[col_1])):
        if (current_color_matrix[i][col_2][0] > 0) and (current_color_matrix[i][col_1][0] > 0):
            new_matrix[i][col_2] = duplicate[i][col_1] + 1
            new_matrix[i][col_1] = duplicate[i][col_2] + 1
            red_val = new_color_matrix[i][col_2][0] - inc_val
            red_val1 = new_color_matrix[i][col_1][0] - inc_val
            if red_val < inc_val:
                red_val = 0
            if red_val1 < inc_val:
                red_val1 = 0
            ret_color_matrix[i][col_2][0] = red_val
            ret_color_matrix[i][col_1][0] = red_val1

    return new_matrix, ret_color_matrix


def event_handling():
    run = True
    while run:
        pygame.time.wait(100)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                return mx, my


def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


'''--- Dictionaries --- After this point are functions that return lists or dictionaries to be drawn to the screen in 
the puzzle_screen function. '''


# pygame.Rect(xcoordinate, ycoordinate, length, height)


def selection_dict(selection_on_screen):
    if selection_on_screen == 2:
        matrix_buttons = {'00': pygame.Rect(400, 385, 275, 4), '01': pygame.Rect(725, 385, 275, 4),
                          '10': pygame.Rect(400, 685, 275, 4), '11': pygame.Rect(725, 685, 275, 4)
                          }
        return matrix_buttons
    if selection_on_screen == 3:
        matrix_buttons = {'00': pygame.Rect(400, 285, 175, 4), '01': pygame.Rect(615, 285, 175, 4),
                          '02': pygame.Rect(830, 285, 175, 4),
                          '10': pygame.Rect(400, 485, 175, 4), '11': pygame.Rect(615, 485, 175, 4),
                          '12': pygame.Rect(830, 485, 175, 4),
                          '20': pygame.Rect(400, 685, 175, 4), '21': pygame.Rect(615, 685, 175, 4),
                          '22': pygame.Rect(830, 685, 175, 4)
                          }
        return matrix_buttons
    if selection_on_screen == 4:
        matrix_buttons = {'00': pygame.Rect(430, 255, 115, 4), '01': pygame.Rect(570, 255, 115, 4),
                          '02': pygame.Rect(710, 255, 115, 4), '03': pygame.Rect(850, 255, 115, 4),
                          '10': pygame.Rect(430, 390, 115, 4), '11': pygame.Rect(570, 390, 115, 4),
                          '12': pygame.Rect(710, 390, 115, 4), '13': pygame.Rect(850, 390, 115, 4),
                          '20': pygame.Rect(430, 525, 115, 4), '21': pygame.Rect(570, 525, 115, 4),
                          '22': pygame.Rect(710, 525, 115, 4), '23': pygame.Rect(850, 525, 115, 4),
                          '30': pygame.Rect(430, 660, 115, 4), '31': pygame.Rect(570, 660, 115, 4),
                          '32': pygame.Rect(710, 660, 115, 4), '33': pygame.Rect(850, 660, 115, 4)
                          }
        return matrix_buttons


def button_dict(button_for_screen):
    if button_for_screen == 'puzzle':
        action_rect = {'add': pygame.Rect(50, 150, 200, 100),
                       'slide': pygame.Rect(50, 283, 200, 100), 'row': pygame.Rect(50, 416, 200, 100),
                       'column': pygame.Rect(50, 550, 200, 100), 'help': pygame.Rect(1000, 0, 100, 50),
                       'clear': pygame.Rect(700, 0, 100, 50), 'level_screen': pygame.Rect(865, 0, 70, 50),
                       'undo': pygame.Rect(550, 0, 100, 50), 'view_sol': pygame.Rect(330, 0, 150, 50)}

        action_function = {'add': addition, 'slide': slide, 'row': row, 'column': column}
        return action_rect, action_function

    if button_for_screen == 2:
        action_rect = {'00': pygame.Rect(400, 125, 275, 250), '01': pygame.Rect(725, 125, 275, 250),
                       '10': pygame.Rect(400, 425, 275, 250), '11': pygame.Rect(725, 425, 275, 250)
                       }
        return action_rect
    if button_for_screen == 3:
        action_rect = {'00': pygame.Rect(400, 125, 175, 150), '01': pygame.Rect(615, 125, 175, 150),
                       '02': pygame.Rect(830, 125, 175, 150),
                       '10': pygame.Rect(400, 325, 175, 150), '11': pygame.Rect(615, 325, 175, 150),
                       '12': pygame.Rect(830, 325, 175, 150),
                       '20': pygame.Rect(400, 525, 175, 150), '21': pygame.Rect(615, 525, 175, 150),
                       '22': pygame.Rect(830, 525, 175, 150)
                       }
        return action_rect
    if button_for_screen == 4:
        action_rect = {'00': pygame.Rect(430, 140, 115, 110), '01': pygame.Rect(570, 140, 115, 110),
                       '02': pygame.Rect(710, 140, 115, 110), '03': pygame.Rect(850, 140, 115, 110),
                       '10': pygame.Rect(430, 275, 115, 110), '11': pygame.Rect(570, 275, 115, 110),
                       '12': pygame.Rect(710, 275, 115, 110), '13': pygame.Rect(850, 275, 115, 110),
                       '20': pygame.Rect(430, 410, 115, 110), '21': pygame.Rect(570, 410, 115, 110),
                       '22': pygame.Rect(710, 410, 115, 110), '23': pygame.Rect(850, 410, 115, 110),
                       '30': pygame.Rect(430, 545, 115, 110), '31': pygame.Rect(570, 545, 115, 110),
                       '32': pygame.Rect(710, 545, 115, 110), '33': pygame.Rect(850, 545, 115, 110)
                       }
        return action_rect
    if button_for_screen == 'level':
        action_rect = { 1: pygame.Rect(75, 75, 125, 100), 2: pygame.Rect(306, 75, 125, 100),3: pygame.Rect(537, 75, 125, 100), 4: pygame.Rect(768, 75, 125, 100), 5: pygame.Rect(1000, 75, 125, 100),
                        6: pygame.Rect(75, 210, 125, 100), 7: pygame.Rect(306, 210, 125, 100), 8: pygame.Rect(537, 210, 125, 100), 9: pygame.Rect(768, 210, 125, 100), 10: pygame.Rect(1000, 210, 125, 100),
                       11: pygame.Rect(75, 350, 125, 100), 12: pygame.Rect(306, 350, 125, 100), 13: pygame.Rect(537, 350, 125, 100), 14: pygame.Rect(768, 350, 125, 100), 15: pygame.Rect(1000, 350, 125, 100),
                        16: pygame.Rect(75, 490, 125, 100), 17: pygame.Rect(306, 490, 125, 100), 18: pygame.Rect(537, 490, 125, 100), 19: pygame.Rect(768, 490, 125, 100), 20: pygame.Rect(1000, 490, 125, 100),
                        21: pygame.Rect(75, 630, 125, 100), 22: pygame.Rect(306, 630, 125, 100), 23: pygame.Rect(537, 630, 125, 100), 24: pygame.Rect(768, 630, 125, 100), 25: pygame.Rect(1000, 630, 125, 100)}

        num_text = np.array([[[str(1), pygame.font.Font(FONT, 50), (0, 0, 0), window, 115, 90],
                              [str(2), pygame.font.Font(FONT, 50), (0, 0, 0), window, 346, 90],
                              [str(3), pygame.font.Font(FONT, 50), (0, 0, 0), window, 577, 90],
                              [str(4), pygame.font.Font(FONT, 50), (0, 0, 0), window, 808, 90],
                              [str(5), pygame.font.Font(FONT, 50), (0, 0, 0), window, 1040, 90]],
                             [[str(6), pygame.font.Font(FONT, 50), (0, 0, 0), window, 115, 225],
                              [str(7), pygame.font.Font(FONT, 50), (0, 0, 0), window, 346, 225],
                              [str(8), pygame.font.Font(FONT, 50), (0, 0, 0), window, 577, 225],
                              [str(9), pygame.font.Font(FONT, 50), (0, 0, 0), window, 808, 225],
                              [str(10), pygame.font.Font(FONT, 50), (0, 0, 0), window, 1030, 225]],
                             [[str(11), pygame.font.Font(FONT, 50), (0, 0, 0), window, 110, 365],
                              [str(12), pygame.font.Font(FONT, 50), (0, 0, 0), window, 336, 365],
                              [str(13), pygame.font.Font(FONT, 50), (0, 0, 0), window, 567, 365],
                              [str(14), pygame.font.Font(FONT, 50), (0, 0, 0), window, 798, 365],
                              [str(15), pygame.font.Font(FONT, 50), (0, 0, 0), window, 1030, 365]],
                             [[str(16), pygame.font.Font(FONT, 50), (0, 0, 0), window, 110, 505],
                              [str(17), pygame.font.Font(FONT, 50), (0, 0, 0), window, 336, 505],
                              [str(18), pygame.font.Font(FONT, 50), (0, 0, 0), window, 567, 505],
                              [str(19), pygame.font.Font(FONT, 50), (0, 0, 0), window, 798, 505],
                              [str(20), pygame.font.Font(FONT, 50), (0, 0, 0), window, 1025, 505]],
                             [[str(21), pygame.font.Font(FONT, 50), (0, 0, 0), window, 105, 645],
                              [str(22), pygame.font.Font(FONT, 50), (0, 0, 0), window, 331, 645],
                              [str(23), pygame.font.Font(FONT, 50), (0, 0, 0), window, 562, 645],
                              [str(24), pygame.font.Font(FONT, 50), (0, 0, 0), window, 793, 645],
                              [str(25), pygame.font.Font(FONT, 50), (0, 0, 0), window, 1025, 645]]],
                            dtype=object)

        return action_rect, num_text


def num_text_list(current_matrix, current_color_matrix):
    dimension = len(current_matrix)

    # each element is a text object of the form ('string', font, color, where it goes, xcoordinate, ycoordinate )
    # where it goes refers to the pygame window initialized at the top of the program.

    if dimension == 2:
        num_list = np.array([[[str(current_matrix[0][0]), pygame.font.Font(FONT, 150), (0, 0, 0), window, 475, 150],
                              [str(current_matrix[0][1]), pygame.font.Font(FONT, 150), (0, 0, 0), window, 800, 150]],
                             [[str(current_matrix[1][0]), pygame.font.Font(FONT, 150), (0, 0, 0), window, 475, 450],
                              [str(current_matrix[1][1]), pygame.font.Font(FONT, 150), (0, 0, 0), window, 800, 450]]],
                            dtype=object)

    if dimension == 3:
        num_list = np.array([[[str(current_matrix[0][0]), pygame.font.Font(FONT, 100), (0, 0, 0), window, 450, 135],
                              [str(current_matrix[0][1]), pygame.font.Font(FONT, 100), (0, 0, 0), window, 665, 135],
                              [str(current_matrix[0][2]), pygame.font.Font(FONT, 100), (0, 0, 0), window, 880, 135]],
                             [[str(current_matrix[1][0]), pygame.font.Font(FONT, 100), (0, 0, 0), window, 450, 335],
                              [str(current_matrix[1][1]), pygame.font.Font(FONT, 100), (0, 0, 0), window, 665, 335],
                              [str(current_matrix[1][2]), pygame.font.Font(FONT, 100), (0, 0, 0), window, 880, 335]],
                             [[str(current_matrix[2][0]), pygame.font.Font(FONT, 100), (0, 0, 0), window, 450, 535],
                              [str(current_matrix[2][1]), pygame.font.Font(FONT, 100), (0, 0, 0), window, 665, 535],
                              [str(current_matrix[2][2]), pygame.font.Font(FONT, 100), (0, 0, 0), window, 880, 535]]],
                            dtype=object)
    if dimension < 4:
        for p in range(dimension):
            for k in range(dimension):
                if (abs(int(num_list[p][k][0])) > 100):
                    if dimension == 2:
                        num_list[p][k][1] = pygame.font.Font(FONT, 100)
                        num_list[p][k][5] += 30
                    else:
                        num_list[p][k][1] = pygame.font.Font(FONT, 75)
                        num_list[p][k][5] += 30
                if (int(num_list[p][k][0]) < 12):
                    num_list[p][k][4] = num_list[p][k][4] - 10
                if (int(num_list[p][k][0]) > 0) and (int(num_list[p][k][0]) < 10):
                    num_list[p][k][4] = num_list[p][k][4] + 10
                if int(num_list[p][k][0]) <= -10:
                    num_list[p][k][4] = num_list[p][k][4] - 70
                if int(num_list[p][k][0]) == 10:
                    num_list[p][k][4] = num_list[p][k][4] - 30
                if int(num_list[p][k][0]) == 11:
                    num_list[p][k][4] = num_list[p][k][4] - 15
                if int(num_list[p][k][0]) > 11:
                    num_list[p][k][4] = num_list[p][k][4] - 50

    if dimension == 4:
        num_list = np.array([[[str(current_matrix[0][0]), pygame.font.Font(FONT, 50), (0, 0, 0), window, 470, 160],
                              [str(current_matrix[0][1]), pygame.font.Font(FONT, 50), (0, 0, 0), window, 610, 160],
                              [str(current_matrix[0][2]), pygame.font.Font(FONT, 50), (0, 0, 0), window, 750, 160],
                              [str(current_matrix[0][3]), pygame.font.Font(FONT, 50), (0, 0, 0), window, 890, 160]],
                             [[str(current_matrix[1][0]), pygame.font.Font(FONT, 50), (0, 0, 0), window, 470, 295],
                              [str(current_matrix[1][1]), pygame.font.Font(FONT, 50), (0, 0, 0), window, 610, 295],
                              [str(current_matrix[1][2]), pygame.font.Font(FONT, 50), (0, 0, 0), window, 750, 295],
                              [str(current_matrix[1][3]), pygame.font.Font(FONT, 50), (0, 0, 0), window, 890, 295]],
                             [[str(current_matrix[2][0]), pygame.font.Font(FONT, 50), (0, 0, 0), window, 470, 430],
                              [str(current_matrix[2][1]), pygame.font.Font(FONT, 50), (0, 0, 0), window, 620, 430],
                              [str(current_matrix[2][2]), pygame.font.Font(FONT, 50), (0, 0, 0), window, 750, 430],
                              [str(current_matrix[2][3]), pygame.font.Font(FONT, 50), (0, 0, 0), window, 890, 430]],
                             [[str(current_matrix[3][0]), pygame.font.Font(FONT, 50), (0, 0, 0), window, 470, 565],
                              [str(current_matrix[3][1]), pygame.font.Font(FONT, 50), (0, 0, 0), window, 610, 565],
                              [str(current_matrix[3][2]), pygame.font.Font(FONT, 50), (0, 0, 0), window, 750, 565],
                              [str(current_matrix[3][3]), pygame.font.Font(FONT, 50), (0, 0, 0), window, 890, 565]]],
                            dtype=object)

        for p in range(dimension):
            for k in range(dimension):
                if int(num_list[p][k][0]) < 0:
                    num_list[p][k][4] = num_list[p][k][4] - 30
                if int(num_list[p][k][0]) == 10:
                    num_list[p][k][4] = num_list[p][k][4] - 25
                if int(num_list[p][k][0]) == 11:
                    num_list[p][k][4] = num_list[p][k][4] - 10
                if (int(num_list[p][k][0]) > 11) and (int(num_list[p][k][0]) < 20):
                    num_list[p][k][4] = num_list[p][k][4] - 20
                if int(num_list[p][k][0]) >= 20:
                    num_list[p][k][4] = num_list[p][k][4] - 25
                if abs(int(num_list[p][k][0])) > 100:
                    num_list[p][k][1] = pygame.font.Font(FONT, 30)

    for i in range(dimension):
        for j in range(dimension):
            if (current_color_matrix[i][j][0] < 50) and (current_color_matrix[i][j][1] < 50) and (
                    current_color_matrix[i][j][2] < 50):
                num_list[i][j][2] = (255, 255, 255)
    return num_list


# each element is a text object of the form ('string', font, color, where it goes, xcoordinate, ycoordinate)
# color = (R,G,B) each one randomly generated

def text_list(text_for_screen, level):
    if text_for_screen == 'puzzle':
        button_name_list = [
            ("A D D", pygame.font.Font(FONT, 30),
             (255, 255, 255), window, 98, 185),
            ("S L I D E", pygame.font.Font(FONT, 30),
             (255, 255, 255), window, 70, 318),
            ("R O W", pygame.font.Font(FONT, 30),
             (255, 255, 255), window, 100, 451),
            ("C O L U M N", pygame.font.Font(FONT, 25),
             (255, 255, 255), window, 70, 585),
            ("HELP", pygame.font.Font(FONT, 20),
             (255, 255, 255), window, 1025, 15),
            ("LEVEL: " + str(level), pygame.font.Font(FONT, 20),
             (255, 255, 255), window, 865, 15),
            ("CLEAR", pygame.font.Font(FONT, 20),
             (255, 255, 255), window, 710, 15),
            ("UNDO", pygame.font.Font(FONT, 20),
             (255, 255, 255), window, 568, 15),
            ("SOLUTION", pygame.font.Font(FONT, 20),
             (255, 255, 255), window, 345, 15)]

    # noinspection PyUnboundLocalVariable
    return button_name_list


def begin_matrix_num(level):
    matrix_dict = {1: np.array([[5, 1], [-1, 9]]),
                   2: np.array([[0, 2], [-5, 3]]),
                   3: np.array([[2, 0], [17, 8]]),
                   4: np.array([[3, 0, -3], [5, 7, 6], [10, -1, 2]]),
                   5: np.array([[6, 1], [6, -5]]),
                   6: np.array([[-16, 2], [-1, 10]]),
                   7: np.array([[1, 5, 3], [0, 0, 0], [10, -1, 2]]),
                   8: np.array([[0, -8], [7, -3]]),
                   9: np.array([[1, 2], [3, 7]]),
                   10: np.array([[1, 5, 3], [4, -6, 6], [10, -11, 2]]),
                   11: np.array([[15, -8, 2], [1, 1, 1], [0, -19, 7]]),
                   12: np.array([[1, 2, 3, 14],
                                 [-5, 6, -14, 8],
                                 [0, 7, 0, 18],
                                 [13, 3, -15, 1]]),
                   13: np.array([[13, 1, 1], [7, 2, 3], [1, -22, 2]]),
                   14: np.array([[1, 2, 0, 14],
                                 [5, 0, 7, 8],
                                 [19, 10, 0, 12],
                                 [13, 0, 15, 26]]),
                   15: np.array([[1, 0, 3, 0],
                                 [0, 7, 0, 5],
                                 [12, 0, 11, 0],
                                 [0, 13, 0, 15]]),
                   16: np.array([[1, 5, 3], [0, 0, 0], [10, -1, 2]]),
                   17: np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]]),
                   18: np.array([[1, 2, 3, 4],
                                 [5, 6, -7, 8],
                                 [9, 10, 11, 12],
                                 [13, -14, 15, 16]]),
                   19: np.array([[7, -1], [9, -4]]),
                   20: np.array([[1, -5, 3], [0, 6, 0], [-4, -1, 2]]),
                   21: np.array([[1, 2], [0, -1]]),
                   22: np.array([[10, 1], [5, -7]]),
                   23: np.array([[1, 5, 13], [0, 8, 0], [10, -1, 12]]),
                   24: np.array([[1, 2, -3, 0],
                                 [3, 6, -7, 8],
                                 [0, 10, 1, 12],
                                 [6, -14, 5, 0]]),
                   25: np.array([[1, -9, 6, 23],
                                 [2, 7, 11, 0],
                                 [18, 21, 0, 3],
                                 [-4, 0, 25, 5]]),
                   }
    begin_matrix = matrix_dict[level]
    return begin_matrix


def end_matrix_num(level):
    matrix_dict = {1: np.array([[6, 1], [-1, 9]]),
                   2: np.array([[1, 3], [-5, 3]]),
                   3: np.array([[2, 1], [17, 9]]),
                   4: np.array([[-2, 0, 4], [7, 7, 6], [3, -1, 11]]),
                   5: np.array([[6, 1], [6, -10]]),
                   6: np.array([[-17, 2], [-2, 10]]),
                   7: np.array([[2, 4, 3], [-1, 0, 5], [10, -2, 2]]),
                   8: np.array([[8, -4], [1, -7]]),
                   9: np.array([[4, 2], [3, 16]]),
                   10: np.array([[2, 0, 4], [4, -6, 6], [10, -11, 2]]),
                   11: np.array([[-9, 1, 0], [14, 1, 6], [0, -1, -20]]),
                   12: np.array([[1, -6, 3, 14],
                                 [1, 8, 1, -15],
                                 [2, 7, -13, 9],
                                 [13, 3, 17, 1]]),
                   13: np.array([[0, 1, 2], [12, 0, 1], [6, -22, 1]]),
                   14: np.array([[18, 2, 0, 0],
                                 [1, 6, 9, 8],
                                 [11, 10, 0, 13],
                                 [1, 14, 27, 16]]),
                   15: np.array([[6, 4, 1, 0],
                                 [0, 7, 0, 5],
                                 [12, 0, 11, 0],
                                 [0, 13, 0, 15]]),
                   16: np.array([[0, 5, 0], [-2, 0, -1], [20, -1, 2]]),
                   17: np.array([[0,-1, 0], [-4, 0, -2], [0, -3, 0]]),
                   18: np.array([[2, 11, 10, 1],
                                 [5, 6, -7, 8],
                                 [9, 4, 3, 12],
                                 [13, -14, 15, 16]]),
                   19: np.array([[-1, 6], [-4, 16]]),
                   20: np.array([[6, 9, 0], [-9, -3, -3], [0, -1, -10]]),
                   21: np.array([[4, 8], [7, -2]]),
                   22: np.array([[-4, -4], [0, -1]]),
                   23: np.array([[6, 20, 25], [44, 30, 29], [55, 30, 25]]),
                   24: np.array([[4, 16, 20, 0],
                                 [52, 2, 20, 8],
                                 [16, 0, 6, 28],
                                 [4, 26, 26, 12]]),
                   25: np.array([[99, 19, 80, 52],
                                 [19, -3, 50, 48],
                                 [17, 36, 57, 65],
                                 [64, -4, 69, 88]]),
                   }
    end_matrix = matrix_dict[level]
    return end_matrix


def begin_matrix_color(level):
    c = 255
    matrix_dict = {1: np.array([[[c, 0, 0], [0, 0, 0]], [[0, 0, 0], [0, 0, 0]]], dtype=object),
                   2: np.array([[[c, 0, 0], [c, 0, 0]], [[0, 0, 0], [0, 0, 0]]], dtype=object),
                   3: np.array([[[0, 0, 0], [c, 0, 0]], [[0, 0, 0], [c, 0, 0]]], dtype=object),
                   4: np.array([[[c, 0, 0], [0, 0, 0], [c, 0, 0]],
                                 [[c, 0, 0], [0, 0, 0], [c, 0, 0]],
                                 [[c, 0, 0], [0, 0, 0], [c, 0, 0]]], dtype=object),
                   5: np.array([[[0, 0, 0], [0, 0, 0]], [[0, 0, 0], [0, c, 0]]], dtype=object),
                   6: np.array([[[0, c, 0], [0, 0, 0]], [[0, c, 0], [0, 0, 0]]], dtype=object),
                   7: np.array([[[c, 0, 0], [0, c, 0], [0, 0, 0]],
                                 [[0, c, 0], [0, 0, 0], [0, c, 0]],
                                 [[0, 0, 0], [0, c, 0], [0, 0, 0]]], dtype=object),
                   8: np.array([[[c, 0, 0], [c, c, 0]], [[c, 0, 0], [c, 0, 0]]], dtype=object),
                   9: np.array([[[c, c, 0], [0, 0, 0]], [[0, 0, 0], [c, c, 0]]], dtype=object),
                   10: np.array([[[0, 0, c], [0, 0, c], [0, 0, c]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0]]], dtype=object),
                   11: np.array([[[0, 0, c], [0, 0, c], [0, 0, c]],
                                 [[0, 0, c], [0, 0, 0], [0, 0, c]],
                                 [[0, 0, c], [0, 0, c], [0, 0, c]]], dtype=object),
                   12: np.array([[[0, 0, 0], [0, 0, c], [0, 0, 0], [0, 0, 0]],
                                 [[c, 0, c], [c, 0, 0], [c, 0, 0], [c, 0, 0]],
                                 [[c, 0, 0], [c, 0, 0], [c, 0, 0], [c, 0, c]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, c], [0, 0, 0]]], dtype=object),
                   13: np.array([[[0, 0, c], [0, 0, 0], [0, 0, c]],
                                 [[0, 0, c], [0, 0, c], [0, 0, c]],
                                 [[0, 0, c], [0, 0, 0], [0, 0, c]]], dtype=object),
                   14: np.array([[[0, 0, c], [0, 0, 0], [0, c, 0], [0, 0, c]],
                                 [[c, 0, 0], [c, 0, 0], [c, 0, 0], [c, 0, 0]],
                                 [[0, 0, c], [0, 0, 0], [0, c, 0], [0, 0, c]],
                                 [[c, 0, 0], [c, 0, 0], [c, 0, 0], [c, 0, 0]]], dtype=object),
                   15: np.array([[[c, c, c], [c, c, c], [c, c, c], [c, c, c]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]], dtype=object),
                   16: np.array([[[c, c, c], [0, 0, 0], [c, c, c]],
                                 [[c, c, c], [0, 0, 0], [c, c, c]],
                                 [[c, c, c], [0, 0, 0], [c, c, c]]], dtype=object),
                   17: np.array([[[0, 0, 0], [c, c, c], [0, 0, 0]],
                                 [[c, c, c], [c, c, c], [c, c, c]],
                                 [[0, 0, 0], [c, c, c], [0, 0, 0]]], dtype=object),
                   18: np.array([[[c, 0, c], [c, 0, c], [c, 0, c], [c, 0, c]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[c, 0, c], [c, 0, c], [c, 0, c], [c, 0, c]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]], dtype=object),
                   19: np.array([[[c, c, c], [c, c, c]], [[c, c, c], [c, c, c]]], dtype=object),
                   20: np.array([[[c, c, c], [c, c, c], [c, c, c]],
                                 [[c, c, c], [c, c, c], [c, c, c]],
                                 [[c, c, c], [c, c, c], [c, c, c,]]], dtype=object),
                   21: np.array([[[c, c, c], [c, c, c]], [[c, c, c], [c, c, c]]], dtype=object),
                   22: np.array([[[c, c, c], [c, c, c]], [[c, c, c], [c, c, c]]], dtype=object),
                   23: np.array([[[c, c, c], [c, c, c], [c, c, c]],
                                 [[c, c, c], [c, c, c], [c, c, c]],
                                 [[c, c, c], [c, c, c], [c, c, c,]]], dtype=object),
                   24: np.array([[[c, c, c], [c, c, c], [c, c, c], [c, c, c]],
                                 [[c, c, c], [c, c, c], [c, c, c], [c, c, c]],
                                 [[c, c, c], [c, c, c], [c, c, c], [c, c, c]],
                                 [[c, c, c], [c, c, c], [c, c, c], [c, c, c]]], dtype=object),
                   25: np.array([[[c, c, c], [c, c, c], [c, c, c], [c, c, c]],
                                 [[c, c, c], [c, c, c], [c, c, c], [c, c, c]],
                                 [[c, c, c], [c, c, c], [c, c, c], [c, c, c]],
                                 [[c, c, c], [c, c, c], [c, c, c], [c, c, c]]], dtype=object),
                   }

    start_matrix_color = matrix_dict[level]
    return start_matrix_color


def end_matrix_color(level):
    matrix_dict = {1: np.array([[[0, 0, 0], [0, 0, 0]], [[0, 0, 0], [0, 0, 0]]], dtype=object),
                   2: np.array([[[0, 0, 0], [0, 0, 0]], [[0, 0, 0], [0, 0, 0]]], dtype=object),
                   3: np.array([[[0, 0, 0], [0, 0, 0]], [[0, 0, 0], [0, 0, 0]]], dtype=object),
                   4: np.array([[[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0]]], dtype=object),
                   5: np.array([[[0, 0, 0], [0, 0, 0]], [[0, 0, 0], [0, 0, 0]]], dtype=object),
                   6: np.array([[[0, 0, 0], [0, 0, 0]], [[0, 0, 0], [0, 0, 0]]], dtype=object),
                   7: np.array([[[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0]]], dtype=object),
                   8: np.array([[[0, 0, 0], [0, 0, 0]], [[0, 0, 0], [0, 0, 0]]], dtype=object),
                   9: np.array([[[0, 0, 0], [0, 0, 0]], [[0, 0, 0], [0, 0, 0]]], dtype=object),
                   10: np.array([[[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0]]], dtype=object),
                   11: np.array([[[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0]]], dtype=object),
                   12: np.array([[[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]], dtype=object),
                   13: np.array([[[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0]]], dtype=object),
                   14: np.array([[[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]], dtype=object),
                   15: np.array([[[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]], dtype=object),
                   16: np.array([[[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0]]], dtype=object),
                   17: np.array([[[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0]]], dtype=object),
                   18: np.array([[[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]], dtype=object),
                   19: np.array([[[0, 0, 0], [0, 0, 0]], [[0, 0, 0], [0, 0, 0]]], dtype=object),
                   20: np.array([[[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0]]], dtype=object),
                   21: np.array([[[0, 0, 0], [0, 0, 0]], [[0, 0, 0], [0, 0, 0]]], dtype=object),
                   22: np.array([[[0, 0, 0], [0, 0, 0]], [[0, 0, 0], [0, 0, 0]]], dtype=object),
                   23: np.array([[[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0]]], dtype=object),
                   24: np.array([[[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]], dtype=object),
                   25: np.array([[[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                 [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]], dtype=object),
                   }
    solution_matrix_color = matrix_dict[level]
    return solution_matrix_color

# specifies how much the RGB values will change by performing an operation

def color_jump(level):
    color_jump_dict = {1: 255, 2: 255, 3: 255, 4: 255, 5: 255, 6: 255, 7: 255, 8: 255, 9: 255, 10: 255, 11: 255,
                       12: 255, 13: 255, 14: 255, 16: 255, 15: 255, 17: 255, 18: 255, 19: 255, 20: 255, 21: 125, 22: 125,
                       23: 125, 24: 125, 25: 125
                       }
    return color_jump_dict[level]


def main():
    title_screen_animation()


main()
