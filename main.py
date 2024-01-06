# Shooting Gallery Game like Duck Hunt
import pygame
import math

pygame.init()

#CONSTANTS, basically game settings
FPS = 60
timer = pygame.time.Clock()
font = pygame.font.Font('assets/font/8bitOperatorPlus8-Regular.ttf', 32)
big_font = pygame.font.Font('assets/font/8bitOperatorPlus8-Regular.ttf', 60)
WIDTH = 900
HEIGHT = 800
screen = pygame.display.set_mode([WIDTH, HEIGHT])
bgs = []
banners = []
guns = []
target_images = [[], []] #List for both levels
#Amount of targets on the screen
targets = {1: [6, 4, 2],
           2: [10, 6]}
level = 0 #Level 0 is start menu, pause, and etc.
points = 0
mode = 0 # 0 for freeplay, 1 for accuracy, and 2 for timed
ammo = 0
counter = 1
best_freeplay = 0
best_ammo = 0
best_timed = 0
time_passed = 0 #This is the initial start time which is 0 seconds
time_remaining = 0 #This won't be initialized until the game mode is selected
total_shots = 0
shot = False
menu = True
game_over = False
pause = False
clicked = False
write_values = False
new_coords = True
one_coords = [[], [], []]
two_coords = [[], []]
menu_img = pygame.image.load(f'assets/menus/mainMenu.png')
game_over_img = pygame.image.load(f'assets/menus/gameOver.png')
pause_img = pygame.image.load(f'assets/menus/pause.png')


#This will go through and grab all of the images for us in their specific file
for i in range(1, 3):
    bgs.append(pygame.image.load(f'assets/bgs/{i}.png'))
    banners.append(pygame.image.load(f'assets/banners/{i}.png'))
    guns.append(pygame.transform.scale(pygame.image.load(f'assets/guns/{i}.png'), (100, 200)))
    
    #Importing level 1 targets onto the screen, loading them
    if i == 1: #If level 1
        for j in range(1, 4): #The 3 targets within the level 1 file
            #Makes the enemies smaller, look at the (j*something)
            target_images[i - 1].append(pygame.transform.scale
                (pygame.image.load(f'assets/targets/{i}/{j}.png'), (120 - (j*18), 80 - (j*12))))
    else:
        for j in range(1, 3): #The 2 targets within the level 2 file
            target_images[i - 1].append(pygame.transform.scale
                (pygame.image.load(f'assets/targets/{i}/{j}.png'), (120 - (j*18), 80 - (j*12))))

# This is going to open and read our high scores as we initially enter the game
file = open('highscore.txt', 'r')
read_file = file.readlines()
file.close()
best_freeplay = int(read_file[0])
best_ammo = int(read_file[1])
best_timed = int(read_file[2])


def draw_score():
    #This is going to put the score on the banner along with text
    points_text = font.render(f'Points: {points}', True, 'black')
    #Change the pixel values around to make it fit better if needed
    screen.blit(points_text, (320, 660))

    #Blow does the same thing but with different pieces of info on the banner
    shots_text = font.render(f'Total Shots: {total_shots}', True, 'black')
    screen.blit(shots_text, (320, 687))
    time_text = font.render(f'Time Elapsed: {time_passed}', True, 'black')
    screen.blit(time_text, (320, 714))

    if mode == 0:
        mode_text = font.render('Freeplay!', True, 'black')
    elif mode == 1:
        mode_text = font.render(f'Ammo Remaining: {ammo}', True, 'black')
    elif mode == 2:
        mode_text = font.render(f'Time Remaining: {time_remaining}', True, 'black')
    screen.blit(mode_text, (320, 741))


def draw_gun():
    mouse_pos = pygame.mouse.get_pos() #list of where the mouse is positioned on the screen
    gun_point = (WIDTH/2, HEIGHT - 200) #puts the gun at top and middle of the banner
    laser = 'red'
    clicks = pygame.mouse.get_pressed() #list of clicks with the mouse
    
    if mouse_pos[0] != gun_point[0]: #pointing the gun with its slope
        slope = (mouse_pos[1] - gun_point[1])/(mouse_pos[0] - gun_point[0])
    else: #in case gun is facing straight up, it'll actually show that
        slope = -100000
    
    angle = math.atan(slope)
    rotation = math.degrees(angle)
    if mouse_pos[0] < WIDTH/2: #If the mouse is on the left side of the screen, flip the gun so it looks correct
        gun = pygame.transform.flip(guns[level - 1], True, False)
        if mouse_pos[1] < 600: #We don't want to be shooting while the mouse is in the banner
            screen.blit(pygame.transform.rotate(gun, 90 - rotation), (WIDTH/2 - 90, HEIGHT - 300))
            if clicks[0]: #draws the red circle 'laser' when you click
                pygame.draw.circle(screen, laser, mouse_pos, 5)
    else:
        gun = guns[level -1]
        if mouse_pos[1] < 600: #We don't want to be shooting while the mouse is in the banner
            screen.blit(pygame.transform.rotate(gun, 270 - rotation), (WIDTH/2 - 30, HEIGHT - 300))
            if clicks[0]: #draws the red circle 'laser' when you click
                pygame.draw.circle(screen, laser, mouse_pos, 5)


def move_level(coords):
    #This is what is actually moving the birds accross the screen
    #Also updates their coordinates
    if level == 1:
        max_val = 3
    else:
        max_val = 2
    for i in range(max_val):
        for j in range(len(coords[i])):
            my_coords = coords[i][j]
            if my_coords[0] < -150:
                coords[i][j] = (WIDTH, my_coords[1])
            else:
                #Moving them to the left at a speed equal to three to the power of the targets tier
                coords[i][j] = (my_coords[0] - 3**i, my_coords[1])
    return coords


def draw_level(coords):
    if level == 1: #hitboxes for level 1
        target_rects = [[], [], []]
    else: #hitboxes for level 2
        target_rects = [[], []]
    for i in range(len(coords)): #Tracking the coordinates of the targets
        for j in range(len(coords[i])): #The x and y coordinates, change the + number to make the hitbox bigger or smaller
            target_rects[i].append(pygame.rect.Rect((coords[i][j][0] + 20, coords[i][j][1]), 
                                   (60 - i*12, 60 - i*12)))
            #Puts the images on the screen itself
            screen.blit(target_images[level - 1][i], coords[i][j])
    return target_rects


def check_shot(targets, coords):
    #checks to see if we hit a target within its recatngular hitbox
    global points
    mouse_pos = pygame.mouse.get_pos()
    #Remember, i tells us the tier of the enemy or target
    #j tells us the coordinates or positon of it within the list
    for i in range(len(targets)):
        for j in range(len(targets[i])):
            if targets[i][j].collidepoint(mouse_pos):
                #We just want to pop that coord out of our list
                coords[i].pop(j)
                #First level of enemy is 10 points (i = 0), the next is 20 (i = 1), and 50...
                points += 10 + 10 * (i**2)
                # add sounds for enemy hit
    return coords 


def draw_menu():
    global game_over, pause, mode, level, menu, clicked, new_coords
    global time_passed, total_shots, points, ammo, time_remaining
    global best_timed, best_ammo, best_freeplay, write_values
    #Makes sure it doesn't show our other screens
    game_over = False
    pause = False
    #Puts our menu image on the screen
    screen.blit(menu_img, (0, 0))

    #Making our buttons and assigning them
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    #This will make an invisible rectangle with first (x, y) position on screen, then (height, width)
    freeplay_button = pygame.rect.Rect((170, 524), (260, 100))
    #This adds the text in to show the best score
    screen.blit(font.render(f'{best_freeplay}', True, 'black'), (330, 587))
    ammo_button = pygame.rect.Rect((475, 524), (260, 100))
    screen.blit(font.render(f'{best_ammo}', True, 'black'), (650, 587))
    timed_button = pygame.rect.Rect((178, 661), (260, 100))
    screen.blit(font.render(f'{best_timed}', True, 'black'), (350, 717))
    reset_button = pygame.rect.Rect((475, 661), (260, 100))

    #What happens when buttons are clicked
    if freeplay_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 0
        level = 1
        menu = False
        time_passed = 0
        total_shots = 0
        points = 0
        clicked = True #You can't do another click action until you release and re click
        new_coords = True
    if ammo_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 1
        level = 1
        menu = False
        time_passed = 0
        ammo = 81
        total_shots = 0
        points = 0
        clicked = True
        new_coords = True
    if timed_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 2
        level = 1
        menu = False
        time_remaining = 20
        time_passed = 0
        total_shots = 0
        points = 0
        clicked = True
        new_coords = True
    if reset_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        best_freeplay = 0
        best_ammo = 0
        best_timed = 0
        write_values = True
        clicked = True
        new_coords = True


def draw_game_over():
    global clicked, level, pause, game_over, menu
    global points, total_shots, time_passed, time_remaining
    # Scores to show
    if mode == 0:
        display_score = time_passed
    else:
        display_score = points
    screen.blit(game_over_img, (0, 0))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    exit_button = pygame.rect.Rect((178, 661), (260, 100))
    menu_button = pygame.rect.Rect((475, 661), (260, 100))
    #Shows the scores with the big font instead of regular
    screen.blit(big_font.render(f'{display_score}', True, 'black'), (650, 570))

    #What to do if those buttons are clicked
    if menu_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        clicked = True
        level = 0
        pause = False
        game_over = False
        menu = True
        points = 0
        total_shots = 0
        time_passed = 0
        time_remaining = 0
    if exit_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        global run
        run = False


def draw_pause():
    #Puts the pause image on the screen
    global level, pause, menu, points, total_shots
    global time_passed, time_remaining, clicked, new_coords
    screen.blit(pause_img, (0, 0))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    #Define where the invisible buttons are
    resume_button = pygame.rect.Rect((178, 661), (260, 100))
    menu_button = pygame.rect.Rect((475, 661), (260, 100))

    #What will happen when you click each button
    if resume_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        level = resume_level
        pause = False
        clicked = True
    if menu_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        level = 0
        pause = False
        menu = True
        points = 0
        total_shots = 0
        time_passed = 0
        time_remaining = 0
        clicked = True
        new_coords = True


run = True #While the game is running (true)... do this

#MAIN GAME LOOP
while run:
    timer.tick(FPS) #Refresh the screen at 60 fps
    # If the level is not the pause/start screen, then create a counter for the time
    if level != 0:
        if counter < 60:
            counter += 1
        else:
            #Tracking the time passed or remaining variable
            counter = 1
            time_passed += 1
            if mode == 2:
                time_remaining -= 1

    if new_coords:
        # Initialize the targets coordinates
        one_coords = [[], [], []]
        two_coords = [[], []]
        for i in range(3): #for one coords
            my_list = targets[1]
            for j in range(my_list[i]):
                #Spaces out the enemies on the screen based on screen width and height and the amount of each enemy
                one_coords[i].append((WIDTH//(my_list[i]) * j, 300 - (i * 150) + 30 * (j % 2)))
        for i in range(2): #for two coords
            my_list = targets[2]
            for j in range(my_list[i]):
                #Spaces out the enemies on the screen based on screen width and height and the amount of each enemy
                two_coords[i].append((WIDTH//(my_list[i]) * j, 300 - (i * 150) + 30 * (j % 2)))
        new_coords = False


    #Filling the screen
    screen.fill('black')
    screen.blit(bgs[level - 1], (0, 0)) #Populate background
    screen.blit(banners[level - 1], (0, HEIGHT - 200)) #Populate banner

    #Menu screens and startup
    if menu:
        level = 0
        draw_menu()
    if game_over:
        level = 0
        draw_game_over()
    if pause:
        level = 0
        draw_pause()
    
    #Levels
    if level == 1:
        target_boxes = draw_level(one_coords)
        one_coords = move_level(one_coords)
        #Calling our checked hitbox
        if shot:
            one_coords = check_shot(target_boxes, one_coords)
            shot = False #Run this check shot once and then leave it, disallows clicking and holding the mouse like a ray gun
    elif level == 2:
        target_boxes = draw_level(two_coords)
        two_coords = move_level(two_coords)
        if shot:
            two_coords = check_shot(target_boxes, two_coords)
            shot = False

    #Calls the gun function when in the level
    if level > 0:
        #Puts the gun onto the screen using its function
        draw_gun()
        #Puts the score onto the banner using its function
        draw_score()

    for event in pygame.event.get():
        #Quits the game with the little red x
        if event.type == pygame.QUIT:
            run = False
        
        #Tracks the left click on the mouse that hits the target
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_position = pygame.mouse.get_pos()
            #Keeps it within a range of the screen shooting window
            if (0 < mouse_position[0] < WIDTH) and (0 < mouse_position[1] < HEIGHT - 200):
                shot = True
                total_shots += 1
                #remember that gamemode is defined in the constants section
                if mode == 1:
                    ammo -= 1
            #This is for the paused button
            if (670 < mouse_position[0] < 860) and (660 < mouse_position[1] < 715):
                resume_level = level
                pause = True
                clicked = True
            #This is for the restart button
            if (670 < mouse_position[0] < 860) and (715 < mouse_position[1] < 760):
                menu = True
                clicked = True
                new_coords = True

        #Detecting that we have released the click on the mouse so that we can't click and drag on buttons
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and clicked:
            clicked = False

    #This will move from one level to another
    #Good game mechanic if you want each level to be sequential, but not the best for what I went since I want the levels completely separate
    if level > 0:
        if target_boxes == [[], [], []] and level == 1:
            level += 1
        #Game over conditions
        if (level == 2 and target_boxes == [[], []]) or (mode == 1 and ammo == 0) or (mode == 2 and time_remaining == 0):
            new_coords = True
            # Setting the high scores for each game mode
            if mode == 0:
                if time_passed < best_freeplay or best_freeplay == 0:
                    best_freeplay = time_passed
                    write_values = True
            if mode == 1:
                if points > best_ammo:
                    best_ammo = points
                    write_values = True
            if mode == 2:
                if points > best_timed:
                    best_timed = points
                    write_values = True
            game_over = True
    
    #If we have a new score we want to write in
    if write_values:
        file = open('highscore.txt', 'w')
        file.write(f'{best_freeplay}\n{best_ammo}\n{best_timed}')
        file.close()
        write_values = False

    pygame.display.flip() #Updates everything on the screen
pygame.quit #The function to close the program