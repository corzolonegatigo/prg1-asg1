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

SAVE_FOLDER = 'saves'

minerals = ['copper', 'silver', 'gold']
mineral_names = {'C': 'copper', 'S': 'silver', 'G': 'gold'}
pickaxe_price = [50, 150]

prices = {}
prices['copper'] = (1, 3)
prices['silver'] = (5, 8)
prices['gold'] = (10, 18)

warehouse_upgrade_prices = [30, 50, 70] # starts from 3x3, to 5x5
warehouse_storage_load = [9, 12, 15]



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
    if type(player['portal_position']) != str:
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

    if type(player['portal_position']) != str: 
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
    print(f"Pickaxe level: {player['pickaxe_lvl']+1} ({minerals[player['pickaxe_lvl']]} pickaxe)") # using the mineral ranking as the pickaxe material ranking for now
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
    player['game_state'] = 'ongoing'

    print()

    return game_map, fog, player

# This function saves the game
def save_game(game_map, fog, player):

    # checks if a save folder exists. if not, creates folder
    if not os.path.exists(SAVE_FOLDER):
        os.mkdir('saves')

    # get the current saves available 
    saves_list = os.listdir(SAVE_FOLDER)
    

    
    if (player['save_name'] + '.json') not in saves_list:

        # get save number, starting from 1
        save_nums = [int(s[6]) for s in saves_list] # creates a list of integers, using the number from the save file names
        save_no = 1
        while save_no not in save_nums:
            save_no += 1

        # creates save file name and path
        save_no = str(save_no) # typecast to str to allow for str concatenation
        save_name = "save_#" + save_no
        player['save_name'] = save_name
        particular_save_file = os.path.join(SAVE_FOLDER, save_no + '.json')
    else:
        particular_save_file = os.path.join(SAVE_FOLDER, player['save_name'] + '.json')

    # add fog and map to dictnary written to save file
    # converts into list of str to improve save file readability
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

    print("\nSaving Complete.\n")

    continue_var = input("Press Enter to continue. ")

def warehouse_menu(player):

    while True:

        print("----- Your Warehouse -----")

        free_warehouse_space = player['warehouse_load'] - len(player['warehouse_store'])
        warehouse_contents = player['warehouse_store'] + (" " * free_warehouse_space)
        warehouse_contents_formatted = []

        for item in range(player['warehouse_load']):
            
            if item % 3 == 2:
                warehouse_contents_formatted.append(warehouse_contents[item-2:item])

        wrap_map(warehouse_contents_formatted)

        move_to_warehouse_options = ["C", "S", "G", "L"]
        print()
        print("----- Your Bag -----")
        for ore in minerals:
            print(f"{ore}: {player[ore]}")
            if player[ore] == 0:
                move_to_warehouse_options.remove(ore[0].upper())

        move_over_choice = validate_usr_input("What mineral do you want to move to your warehouse? Enter the first letter of the mineral you want. Enter L to leave. ", move_to_warehouse_options)

        if move_over_choice == 'L':
            return player
        
        mineral_moved = mineral_names[move_over_choice]
        move_value = int(input(f"How much {mineral_moved} do you want to store in your warehouse? "))
        
        while (move_value <= 0) or (move_value > player[mineral_moved]):
            if move_value <= 0:
                print("You can't move nothing or less than nothing!")
            if move_value > player[mineral_moved]:
                print(f"You dont have enough {mineral_moved}!")
            move_value = int(input(f"How much {mineral_moved} do you want to store in your warehouse? "))
            
        if move_value > free_warehouse_space:
            print(f"You only can fit {free_warehouse_space} more ores in your warehouse.")
            print(f"{free_warehouse_space} {mineral_moved} ores were moved into your warehouse.")

            player[mineral_moved] -= free_warehouse_space

        else:
            print(f"{move_value} was moved to your warehouse!")

            player[mineral_moved] -= free_warehouse_space

    
        
# gets save info for display purposes. has option for additional columns if want to show extra info. base info that is always included is gp, day, steps, name, game_state.
# additional_columns is given default argument, makes it an optional argument.
def get_save_info(additional_columns = []): 

    if not os.path.exists(SAVE_FOLDER) or (os.listdir(SAVE_FOLDER) == []):
        print("There are no existing games")
        print("Returning to main menu...")
        time.sleep(0.5) # wait a little bit

    else:
        saves_list = os.listdir(SAVE_FOLDER)
        saves_info_to_display = []

        # creates list of keys
        key_values = ['state', 'name', 'day', 'steps', 'GP']
        for column in additional_columns:
            key_values.append(column)

        for save in saves_list:

            # load save info from json
            save_path = os.path.join(SAVE_FOLDER, save)
            save_file = open(save_path, 'r')
            data_raw = json.load(save_file)

            gp = data_raw['GP']
            day = data_raw['day']
            steps = data_raw['steps']
            name = data_raw['name']
            state = data_raw['game_state']

            save_info = [state, name, day+1, steps, gp] # day +1 for display purposes, since count starts from 0
            

            # gets data from additional columns if present
            for column in additional_columns:
                save_info.append(data_raw[column])


            saves_info_to_display.append(save_info) # order is state, name, ranking value of each cat

    return saves_info_to_display, key_values

def single_swap(v1, v2, k_idx: int): # goes down the available values used for ranking. v1, v2 = [state, name, day, step, gp]. swaps if needed. part of below 'show_high_score' function, look at that for full context.
    if v1[k_idx] < v2[k_idx]:
        return v2, v1
    elif v1[k_idx] == v2[k_idx]:
        return single_swap(v1, v2, k_idx + 1)
    else:
        return v1, v2
    

def show_high_scores(game_map, fog, player, saves_info, key_values):


    saves_won_info = []
    saves_incomplete_info = []
    for save in saves_info:
        if save[0] == 'win':
            saves_won_info.append(save)
        else:
            saves_incomplete_info.append(save)

    

    print("\nHIGH SCORE LIST")
    print("----------------------------------------------------")



    if len(saves_won_info) > 1:

        # bubble sort. quite slow but also not alot of save files to sort through
        for i in range(len(saves_won_info)):
            for save_idx in range(len(saves_won_info)-1-i):
                saves_won_info[save_idx], saves_won_info[save_idx+1] = single_swap(saves_won_info[save_idx], saves_won_info[save_idx+1], 2)


        for rank in range(len(saves_won_info)):
            print(f" {rank+1}. {saves_won_info[rank][1]}.")
            for key in range(2, len(key_values)):
                print(f" {key_values[ key].upper()}: {saves_won_info[rank][key]}      ", end="")
            # print(f"STATUS: {saves_won_info[rank][0]}") # adds status and \n to info

    elif len(saves_won_info) == 1:
        print(f" 1. {saves_info[0][1]}")
        for key in range(2, len(key_values)):
            print(f" {key_values[key].upper()}: {saves_info[0][key]}      ", end="")
        # print(f"STATUS: {saves_won_info[0][0]}") 
    
        

    else:
        print("There are no winning games! Let's get the first one.")

    print()
    continue_var = input("Press Enter to continue. ")

    return show_main_menu(game_map, fog, player)

# This function loads the game
def load_game(game_map, fog, player):   
    if not os.path.exists(SAVE_FOLDER) or (os.listdir(SAVE_FOLDER) == []):
        print("There are no available saves for you to load!")
        if input("Do you want to start a new game? [y/n] ") == 'y':
            return initialize_game(game_map, fog, player)

    else:
        # show available saves and ask usr for which save to load
        saves_list = os.listdir(SAVE_FOLDER)
        saves_information, key_values = get_save_info()

        print("----- Saves List -----")
        for save_idx in range(len(saves_list)):
            # print save file name
            print(f" {save_idx+1}. {saves_list[save_idx][:-5]}")

            # print save info
            
            for key_idx in range(len(key_values)):
                print(f" {key_values[key_idx].upper()}: {saves_information[save_idx][key_idx]}   ", end="")
            print()


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
        save_path = os.path.join(SAVE_FOLDER, saves_list[save_to_load])
        save_file = open(save_path, 'r')
        data_raw = json.load(save_file)
        
        # write the map and fog from save to the respective vars
        # converts from the storage format of str in list to the 2d array
        game_map = arr_of_str_to_2darr(data_raw['map'], False)
        fog = arr_of_str_to_2darr(data_raw['fog'], False)

        # gets map width + map height
        global MAP_WIDTH
        global MAP_HEIGHT

        MAP_WIDTH = len(game_map[0])
        MAP_HEIGHT = len(game_map)

        # assign value of player as the complete json read from the file as a dictionary
        player = data_raw

        # remove map and fog from player
        del player['map']
        del player['fog']

        save_file.close()

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
        saves_info, key_values = get_save_info()
        return show_high_scores(game_map, fog, player, saves_info, key_values)
    else:
        print("buh bye")
        return None, None, None
    

def buy_menu(player):

    shopkeeper_dialogue_options = ["Nice wallet you have there!", "Hello buttercup!", "The best shop in the town for all things mining!"]
    
    print("\n------------------------")
    print(shopkeeper_dialogue_options[randint(0,2)], '\n') # random dialogue option lol
    while True: # loops until user decides to leave
        print()

        # the options for user
        buy_options = ['P','B','L','W']
        
        # calculate upgrade prices to show in buy menu
        upgrade_cost_bp = player['bp_size'] * 2

        # show usr GP amount and prompts user to buy
        print(f"You have {player['GP']} GP right now!")
        print("What would you like to buy?")

        # if pickaxe lvl == 2, error will occur. since pickaxe lvl ranges from 0 to 2, and cannot upgrade pass 2, remove option to upgrade pickaxe if error raised
        try:
            upgrade_cost_pickaxe = pickaxe_price[player['pickaxe_lvl']]
            print(f"  (P)ickaxe upgrade to level {player['pickaxe_lvl']+1} to mine {minerals[player['pickaxe_lvl']+1]} for {upgrade_cost_pickaxe} GP.")
        except:
            buy_options.remove('P')

        # can always upgrade bag
        print(f"  (B)ag space upgrade from {player['bp_size']} to {player['bp_size'] + 2} for {upgrade_cost_bp} GP.")
        
        # unique print message depending on whether warehouse is bought, can be upgraded, or maxed out
        if player.get('warehouse_lvl') == None:
            upgrade_cost_warehouse = warehouse_upgrade_prices[0]
            print(f"  Buy a (W)arehouse for {upgrade_cost_warehouse} to store 9 ores.")
        elif player['warehouse_lvl'] < 2:
            upgrade_cost_warehouse = warehouse_upgrade_prices[player['warehouse_lvl']+1]
            print(f"  Upgrade your (W)arehouse for {upgrade_cost_warehouse} to store {warehouse_storage_load[player['warehouse_lvl']+1]}")
        else:
            buy_options.remove('W')

        print(f"  (L)eave shop")
       
        # get usr choice
        choice = validate_usr_input("What would you like to do? ", buy_options)
        print()

        if choice == 'P': # pickaxe buy

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


        elif choice == "W":
            if upgrade_cost_warehouse <= player['GP']:

                if player.get('warehouse_lvl') == None:
                    player['warehouse_lvl'] = 0
                    player['warehouse_load'] = warehouse_storage_load[0]
                    player['warehouse_store'] = ""
                    print("You have just bought your first warehouse!")
                    print("Your warehouse can be accessed from town.")        

                else:
                    player['warehouse_lvl'] += 1
                    player['warehouse_load'] = warehouse_storage_load[player['warehouse_lvl']]
                    print(f"Your warehouse has been upgraded and can now store {player['warehouse_load']} ores!")

                player['GP'] -= upgrade_cost_warehouse
            
            else:
                if player.get('warehouse_lvl') == None:
                    print("You don't have enough GP to buy a warehouse...")
                else:
                    print("You don't have enough GP to upgrade your warehouse")


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

        options = ["B", "I", "M", "E", "V", "Q"]


        print("----- Sundrop Town -----")
        print("(B)uy stuff")
        print("See Player (I)nformation")
        print("See Mine (M)ap")
        print("(E)nter mine")
        print("Sa(V)e game")
        print("(Q)uit to main menu")
        if player.get('warehouse_lvl') != None:
            print("Visit (W)arehouse")
            options.append("W")
        print("------------------------")
        
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
        elif choice == "W":
            player = warehouse_menu(player)
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
        print("\nYou win!!!")
        game_state = 'win'
        player['game_state'] = 'won'
        save_game(game_map, fog, player)

        print("\nThanks for playing!")










    
