from random import randint
import os
import time
import json
from copy import deepcopy

player = {}
game_map = []
fog = []

# const
MAP_WIDTH = 0
MAP_HEIGHT = 0

TURNS_PER_DAY = 20
WIN_GP = 500

minerals = ['copper', 'silver', 'gold']
mineral_names = {'C': 'copper', 'S': 'silver', 'G': 'gold'}
pickaxe_price = [50, 150]

prices = {}
prices['copper'] = (1, 3)
prices['silver'] = (5, 8)
prices['gold'] = (10, 18)



def validate_usr_input(prompt: str, valid_options): # gets str 'prompt' and the list 'valid_options'. ensures that the usr input is valid. automatically .upper usr input
    usr_choice = ""
    while True:
        usr_choice = input(prompt).upper()
        if usr_choice not in valid_options:
            print("That's not possible! Please try something else")
        
        else:
            return usr_choice
    



def arr_of_str_to_2darr(list: list, reverse: bool): # reverse function for if you want 2darr to str instead of str to 2darr. 
    out = []
    if reverse:
        for line in list:
            out.append("".join(line))
    else:
        for i in range(len(list)): 
            out.append([])
            for chr in list[i]:
                out[i].append(chr)

    return out


def wrap_map(map: list): # takes a 1d/2d array as input. if 1d, each element is a str of fixed length. 2d, each list in the main list is of fixed length, with each element in each inner list being a string of each length
    width = len(map[0])*2 + 2 # width of shape outputted
    sides_vertical = "+" + "-" * width + "+"
    
    need_to_join = (type(map[0]) == list)
    print(sides_vertical)
    for line in map:
        if need_to_join:
            print("| " + " ".join(line) + "  |") 
        else:
            print("| ", end='')
            for s in line:
                print(s, end=" ")
            print(" |")

    print(sides_vertical)

# This function loads a map structure (a nested list) from a file
# It also updates MAP_WIDTH and MAP_HEIGHT

def load_map(filename, map_struct):
    map_file = open(filename, 'r')
    global MAP_WIDTH
    global MAP_HEIGHT
    
    map_struct.clear()
    
    # TODO: Add your map loading code here
    map_raw = map_file.readlines()
    for i in range(len(map_raw)):
        map_struct.append(map_raw[i].strip("\n"))


    map_struct = arr_of_str_to_2darr(map_struct, False)
    MAP_WIDTH = len(map_struct[0])
    MAP_HEIGHT = len(map_struct)

    map_file.close()

    return map_struct

def get_surrounding(x: int, y: int): # takes position, gets the bounds of the 3x3 area around it
    
    three_by_three = [['','',''],['','',''],['','','']]

    yrange = range(y-1, y+2)
    xrange = range(x-1, x+2)
    for yv in range(3):
        for xv in range(3):
            if ((0 > xrange[xv]) or (xrange[xv] > MAP_WIDTH)) or ((0 > yrange[yv]) or (yrange[yv] > MAP_HEIGHT)):
                three_by_three[yv][xv] = "#"
                
            else:
                three_by_three[yv][xv] = (xrange[xv], yrange[yv])
                

    return three_by_three

"""
# This function clears the fog of war at the 3x3 square around the player
def clear_fog(map, fog, player):
   
    area_to_clear = get_surrounding(player['x'], player['y'])
    #there must be a faster way
    for row in area_to_clear:
        for item in row:
            if item != '#':
                fog[item[1]][item[0]] = '1'
    
    return fog
"""

    
# This function draws the entire map, covered by the fog
def draw_map(game_map, fog, player):

    map_with_fog = []
    for h in range(MAP_HEIGHT):
        map_with_fog.append([])

        for w in range(MAP_WIDTH):

            if fog[h][w] == "1":
                map_with_fog[h].append(game_map[h][w])
            else:
                map_with_fog[h].append("?")

    if not ((player['x'] == 0) and (player['y'] == 0)):
        map_with_fog[player['y']][player['x']] = 'M'
    if type(player['portal_position']) == tuple:
        map_with_fog[player['portal_position'][1]][player['portal_position'][0]] = 'P'
    wrap_map(map_with_fog)

    continue_var = input("Press Enter to continue. ")

    return game_map, fog, player

# This function draws the 3x3 viewport, clears fog as well
def draw_view(game_map, fog, player):

    viewarea = get_surrounding(player['x'], player['y'])
    view = [[],[],[]]
    for row in range(len(viewarea)):
        for item in viewarea[row]:
            if item != "#":
                view[row].append(game_map[item[1]][item[0]])
                fog[item[1]][item[0]] = '1'
            else:
                view[row].append('#')
            
    view[1][1] = 'M'
    wrap_map(view)

def mining(game_map, player, moved_coords): # the enter mine function looks too long if i put this code in there without a function
    tile = game_map[moved_coords[1]][moved_coords[0]]

    
    if tile in mineral_names.keys():
        mineral_mining = mineral_names[tile]

        # get index of mineral from minerals list
        # if index of mineral > pickaxe lvl, cannot mine that mineral
        # pickaxe levels range from 0 to 2, same as index in minerals list

        mineral_idx = minerals.index(mineral_mining)
        if mineral_idx > player['pickaxe_lvl']:
            print(f"Your {minerals[player['pickaxe_lvl']]} pickaxe is not strong enough to mine this {mineral_mining}!\n")
        
        else:
            if player['current_load'] > player['bp_size']:
                print(f"Your backpack is full! You can't mine any more {mineral_mining}")
            else:
                if mineral_mining == 'copper':
                    mined_amt = randint(1,5)
                elif mineral_mining == 'silver':
                    mined_amt = randint(1,3)
                else:
                    mined_amt = randint(1,2)

                print(f"You mined up {mined_amt} piece(s) of {mineral_mining}!")
                if (player['current_load'] + mined_amt) > player['bp_size']:
                    mined_amt = player['bp_size'] - player['current_load']
                    print(f"...but you only can pick up {mined_amt} more pieces!")
                    player['current_load'] += mined_amt
                    player[mineral_mining] += mined_amt

                else:
                    player['current_load'] += mined_amt
                    player[mineral_mining] += mined_amt

            game_map[player['y']][player['x']] = ' '

            player['x'], player['y'] = moved_coords[0], moved_coords[1] # change player coordinates 
    else:
        player['x'], player['y'] = moved_coords[0], moved_coords[1] # change player coordinates
            
            

    return game_map, player

def selling(player): 

    player['current_load'] = 0 # resets player load to 0
    for ore in minerals: # iterates for every possible mineral
        sell_amount_particular_ore = 0
        for _ in range(player[ore]): # gets amount of particular mineral player is holding
            sell_amount_particular_ore += randint(prices[ore][0], prices[ore][1]) # gets sale value of 1 ore, sell price is a number in a range. said ranged is acquired from the prices dictionary, by using the ore as a key to get the assigned tuple value.
        print(f"You sell {player[ore]} {ore} ore for {sell_amount_particular_ore} GP!") 
        time.sleep(0.1) # delay in printing to make it more interesting to look at selling text. helps player actually catch info as well
        player['GP'] += sell_amount_particular_ore
        player[ore] = 0

    return player

def enter_mine(game_map, fog, player): 

    if type(player['portal_position']) == tuple: 
        go_to_portal = validate_usr_input("Do you want to go to your portal? [Y/N]", ['Y', 'N'])
        if go_to_portal: # sets player x, y to portal position
            player['x'] = player['portal_position'][0]
            player['y'] = player['portal_position'][1]
        else:
            player['x'] = 0
            player['y'] = 0

    while player['turns'] < TURNS_PER_DAY:
        print("----------------------------------------")
        print(f"DAY {player['day']+1}:")
        print(f"Turn {player['turns']+1} / {TURNS_PER_DAY}      Load: {player['current_load']} / {player['bp_size']}      Steps: {player['steps']}")
        

        draw_view(game_map, fog, player) # draws the viewport
        area = get_surrounding(player['x'], player['y']) # get the 3x3 surroundings
        options = ["W", "A", "S", "D", 'M', 'I', 'P', 'Q']

        

        # see if movement option is valid
        if '#' in area:

            if area[0][1] == "#":
                options.remove('W')
            elif area[2][1] == '#':
                options.remove('S')

            if area[1][0] == '#':
                options.remove('A')
            elif area[1][2] == '#':
                options.remove('D')

        print("Use the W, A, S, D keys to move around.")
        print("Additionally, (M)ap, (I)nformation, (P)ortal, (Q)uit to main menu are options.")
        choice = validate_usr_input("Which way do you want to go? ", options)
        print()

        # change player pos based on input
        # checks if player choice is movement key. if so, change steps and turns by 1
        if choice in ['W', 'A', 'S', 'D']: 

            player['steps'] += 1
            player['turns'] += 1

            # creates a tuple, which is the players new position - this is to prevent movement if tile being moved to is unminable
            x = player['x']
            y = player['y']

            

            if choice == 'W':
                new_coords = (x, y-1)
            elif choice == 'A':
                new_coords = (x-1, y)
            elif choice == 'S':
                new_coords = (x, y+1)
            elif choice == 'D':
                new_coords = (x+1 ,y)

            game_map, player = mining(game_map, player, new_coords)

        elif choice == 'M':
            draw_map(game_map, fog, player)
        elif choice == 'I':
            show_information(player)
        elif choice == 'P':

            # prevents player from placing portal on town 
            if (player['x'] + player['y']) == 0: 
                print("You're at town square! You can't place a portal here...")
            else:
                player['portal_position'] = (player['x'], player['y'])
                print(f"You place a portal at (x: {player['x']}, y: {player['y']})!\n")


            return game_map, fog, player
        else:
            game_map, fog, player = show_main_menu(game_map, fog, player)
            return game_map, fog, player

        # mining code
        

    print("You can't spend any longer in the cave, it's getting dark outside.")
    print(f"You place a portal at (x: {player['x']}, y: {player['y']}) and return home.\n")
    player['portal_position'] = (player['x'], player['y'])
    
        
        
    return game_map, fog, player # runs after turn limit is reached
# This function shows the information for the player

def show_information(player):
    print()

    print("----- Player Information -----")
    print("Name:", player['name'])
    print("Portal position:", player['portal_position'])
    print(f"Pickaxe level: {player['pickaxe_lvl']} ({minerals[player['pickaxe_lvl']]} pickaxe)") # using the mineral ranking as the pickaxe material ranking for now
    print("Gold:", player['gold'])
    print("Silver:", player['silver'])
    print("Bronze:", player['copper'])
    print("------------------------------")

    print(f"Load: {player['current_load']} / {player['bp_size']}")
    print("------------------------------")

    print("GP:", player['GP'])
    print("Steps taken:", player['steps'])
    print("------------------------------")

    continue_var = input("Press Enter to return. ")

def initialize_game(game_map, fog, player):
    # initialize map
    game_map = load_map("level1.txt", game_map)
    
    # TODO: initialize fog
    for i in range(MAP_HEIGHT):
        fog.append([])
        for j in range(MAP_WIDTH):
            fog[i].append('0')

    
    player['name'] = input("Greetings, miner! What is your name? ")
    player['bp_size'] = 10
    player['x'] = 0
    player['y'] = 0
    player['copper'] = 0
    player['silver'] = 0
    player['gold'] = 0
    player['GP'] = 0
    player['day'] = 0
    player['steps'] = 0
    player['turns'] = 0
    player['save_name'] = 'new'
    player['portal_position'] = "no portal placed right now."
    player['pickaxe_lvl'] = 0
    player['current_load'] = 0
    player['game_state'] = 'main'

    print()

    return game_map, fog, player

# This function saves the game
def save_game(game_map, fog, player):

    # checks if a save folder exists. if not, creates folder
    save_folder = "saves"
    if not os.path.exists(save_folder):
        os.mkdir('saves')

    # get the current saves available 
    saves_list = os.listdir(save_folder)
    

    
    if (player['save_name'] + '.json') not in saves_list:

        # get save number, starting from 1
        save_nums = [int(s[6]) for s in saves_list] # creates a list of integers, using the number from the save file names
        save_no = 1
        while save_no not in save_nums:
            save_no += 1

        # creates save file name and path
        save_name = "save_#" + str(save_no)
        player['save_name'] = save_name
        particular_save_file = os.path.join(save_folder, save_no + '.json')
    else:
        particular_save_file = os.path.join(save_folder, player['save_name'] + '.json')

    # add fog and map to dictnary written to save file
    player['fog'] = arr_of_str_to_2darr(fog, True)
    player['map'] = arr_of_str_to_2darr(game_map, True)

    # open file and write to save file
    save_file = open(particular_save_file, 'w')
    player_info_json = json.dumps(player, indent=1)
    save_file.write(player_info_json)

    save_file.close()
    
    # extra printing text to make saving feel legit
    print()
    for _ in range(3):
        print('Saving...')
        time.sleep(0.5)

    print()

    continue_var = input("Press Enter to continue. ")

    return
        
# This function loads the game
def load_game(game_map, fog, player):   
    save_folder = 'saves'
    if not os.path.exists(save_folder) or (os.listdir(save_folder) == []):
        print("There are no available saves for you to load!")
        if input("Do you want to start a new game? [y/n] ") == 'y':
            return initialize_game(game_map, fog, player)

    else:
        # show available saves and ask usr for which save to load
        saves_list = os.listdir(save_folder)
        print("----- Saves List -----")
        for save_idx in range(len(saves_list)):
            print(f" {save_idx+1}. {saves_list[save_idx][:-5]}")


        save_to_load = input("\nWhich save do you want to load, plaese enter the corresponding number? ")

        try: # to ensure that input can be read as an integer
            save_to_load = int(save_to_load) - 1
        except:
            print("\nPlease enter the save number.")
            save_to_load = int(input("\nWhich save do you want to load, plaese enter the corresponding number? ")) - 1

        while (-1 >= save_to_load) or (save_to_load >= len(saves_list)): # since this gets a number, outside of the use case of the above valid_usr_input function
            print("\nThats not a valid option! Please try again...")
            save_to_load = int(input("\nWhich save do you want to load, plaese enter the corresponding number? ")) - 1
        
        # load save info
        save_path = os.path.join(save_folder, saves_list[save_to_load])
        save_file = open(save_path, 'r')
        data_raw = json.load(save_file)
        
        # write the map and fog from save to the respective vars
        game_map = arr_of_str_to_2darr(data_raw['map'], False)
        fog = arr_of_str_to_2darr(data_raw['fog'], False)

        # gets map width + map height
        global MAP_WIDTH
        global MAP_HEIGHT

        MAP_WIDTH = len(game_map[0])
        MAP_HEIGHT = len(game_map)
       
        # creates a deepcopy of the dictionary read from the .json file
        player = deepcopy(data_raw)

        # remove map and fog from player
        del player['map']
        del player['fog']

        return game_map, fog, player
    

def show_main_menu(game_map, fog, player):
    print()
    print("--- Main Menu ----")
    print("(N)ew game")
    print("(L)oad saved game")
    print("(H)igh scores")
    print("(Q)uit")
    print("------------------")
    potential_options = ['N','L','Q', 'H']

    choice = validate_usr_input("Your choice? ", potential_options)
    if choice == 'N':
        return initialize_game(game_map, fog, player)
    elif choice == 'L':
        return load_game(game_map, fog, player)
    elif choice == 'H':
        pass
    else:
        print("buh bye")
        return None, None, None
    

def buy_menu(player):

    shopkeeper_dialogue_options = ["Nice wallet you have there!", "Hello buttercup!", "The best shop in the town for all things mining!"]
    
    print("\n------------------------")
    print(shopkeeper_dialogue_options[randint(0,2)], '\n') # random dialogue option lol
    while True: # loops until user decides to leave
        
        # calculate upgrade prices to show in buy menu
        upgrade_cost_pickaxe = pickaxe_price[player['pickaxe_lvl']]
        upgrade_cost_bp = player['bp_size'] * 2

        print(f"You have {player['GP']} GP right now!")
        print("What would you like to buy?")

        print(f"  1. (P)ickaxe upgrade to level {player['pickaxe_lvl']+1} to mine {minerals[player['pickaxe_lvl']+1]} for {upgrade_cost_pickaxe} GP.")
        print(f"  2. (B)ag space upgrade from {player['bp_size']} to {player['bp_size'] + 2} for {upgrade_cost_bp} GP.")
        print(f"  3. (L)eave shop")

        # get usr choice
        choice = validate_usr_input("What would you like to do? ", ['P','B','L'])
        print()

        if choice == 'P': # pickaxe buy
            if player['pickaxe_lvl'] == 2:
                print("You already have the best pickaxe there is!")
                print("We don't have any better for you.")
                
            else:
                upgrade_cost = pickaxe_price[player['pickaxe_lvl']]

                # shows user pickaxe price - reprompt them to see if they want to upgrade to pickaxe
                upgrade_choice = validate_usr_input(f"The next pickaxe costs {upgrade_cost_pickaxe} GP! Do you want to upgrade? [Y/N]", ["Y", "N"]) 
                if upgrade_choice == "Y":
                    if upgrade_cost > player['GP']: # if not enough money for upgrade
                        print("You don't have enough GP to upgrade you pickaxe.")
                        print(f"The next pickaxe, the {minerals[player['pickaxe_lvl']]} pickaxe costs {upgrade_cost} GP!")
                        print(f"You need {upgrade_cost - player["GP"]} more GP...")
                        print("Come back with more dough...\n")

                    else: # if enough money
                        player['GP'] -= upgrade_cost
                        print(f"Your {minerals[player['pickaxe_lvl']]} pickaxe has been upgrade to a {minerals[player['pickaxe_lvl']+1]} pickaxe!")
                        print("Come back again!\n")
                    
        elif choice == "B": # backpack buy
            upgrade_choice = validate_usr_input(f"It costs {upgrade_cost_bp} GP to upgrade your bag size from {player['bp_size']} to {player['bp_size'] + 2}! Do you want to upgrade? [Y/N]", ["Y", "N"])

            if upgrade_choice == "Y":
                if upgrade_cost > player['GP']:
                    print("You don't have enough money for a bigger bag...")
                    print(f"You need {upgrade_cost-player['GP']} more GP!")
                    print("Come back when you have enough.\n")

                else:
                    print(f"Your backpack size has increased from {player['bp_size']} to {player['bp_size'] + 2}!")
                    print("Come back again!\n")

                    player['GP'] -= upgrade_cost
                    player['bp_size'] += 2

        else:
            print("Nothing else? Really...")
            print("Bye then.")
            return player

    
def show_town_menu(game_map, fog, player):
    print()
    print(f"Day {player['day']+1}")
    # TODO: Show Day    
    day_ongoing = True
    while day_ongoing:
        print("----- Sundrop Town -----")
        print("(B)uy stuff")
        print("See Player (I)nformation")
        print("See Mine (M)ap")
        print("(E)nter mine")
        print("Sa(V)e game")
        print("(Q)uit to main menu")
        print("------------------------")
        
        options = ["B", "I", "M", "E", "V", "Q"]
        choice = validate_usr_input("Your choice? ", options)
            
        if choice == 'B':
            player = buy_menu(player)
        elif choice == 'I':
            show_information(player)
        elif choice == "M":
            game_map, fog, player = draw_map(game_map, fog, player)
        elif choice == "E":
            game_map, fog, player = enter_mine(game_map, fog, player)

            day_ongoing = False # end while loop
            

        elif choice == "V":
            save_game(game_map, fog, player)
        else:
            day_ongoing = False
            return show_main_menu(game_map, fog, player)
      
        #if player['turns'] == TURNS_PER_DAY:
        #    day_ongoing = False
        
        print()
    return game_map, fog, player

#--------------------------- MAIN GAME ---------------------------
game_state = 'main'
print()
print("---------------- Welcome to Sundrop Caves! ----------------")
print("You spent all your money to get the deed to a mine, a small")
print("  backpack, a simple pickaxe and a magical portal stone.")
print()
print("How quickly can you get the 1000 GP you need to retire")
print("  and live happily ever after?")
print("-----------------------------------------------------------")

# TODO: The game!

# first initialisation of player
game_map, fog, player = show_main_menu(game_map, fog, player)
while game_state == 'main':
   
    
    while (player != None) and (player['GP'] < WIN_GP) :
        # print(game_map, fog, player)
        currName = player['name']
        game_map, fog, player = show_town_menu(game_map, fog, player)
        if (player == None) or (currName != player['name']):
            break

        # between day to day functions
        print('a')
        player = selling(player)
        player['turns'] = 0
        player['x'] = 0
        player['y'] = 0
        player['day'] += 1

    # checking if win or quit game
    if player == None:
        print("\nThanks for playing!")
        break
    elif player['GP'] >= WIN_GP:
        print("you win")
        game_state = 'win'
        player['game_state'] = 'win'
        save_game(game_map, fog, player)










    
